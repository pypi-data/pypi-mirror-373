"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

from typing import Any, Dict
import os

from flask import Blueprint, current_app, redirect, render_template, request, url_for, jsonify
from qalita.internal.request import send_request
from qalita.commands.source import validate_source_object, validate_source as _validate_all, push_single_programmatic


bp = Blueprint("sources", __name__)


@bp.get("/")
def list_sources():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    sources = cfg.config.get("sources", [])

    # Resolve public platform URL from backend /api/v1/info using the agent backend URL
    platform_url = None
    try:
        backend_url = getattr(cfg, "url", None)
        # Try override from selected .env context without loading agent config (avoid SystemExit)
        try:
            env_path_file = os.path.join(getattr(cfg, "qalita_home", os.path.expanduser("~/.qalita")), ".current_env")
            if os.path.isfile(env_path_file):
                with open(env_path_file, 'r', encoding='utf-8') as f:
                    sel = f.read().strip()
                    if sel and os.path.isfile(sel):
                        with open(sel, 'r', encoding='utf-8') as ef:
                            for line in ef.readlines():
                                line = line.strip()
                                if not line or line.startswith('#') or '=' not in line:
                                    continue
                                k, v = line.split('=', 1)
                                k = k.strip().upper(); v = v.strip().strip('"').strip("'")
                                if k in ("QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"):
                                    backend_url = v
                                    break
        except Exception:
            pass

        if backend_url:
            try:
                r = send_request.__wrapped__(
                    cfg, request=f"{backend_url}/api/v1/info", mode="get"
                )  # type: ignore[attr-defined]
            except Exception:
                r = None
            if r is not None and getattr(r, "status_code", None) == 200:
                try:
                    platform_url = (r.json() or {}).get("public_platform_url")
                except Exception:
                    platform_url = None
    except Exception:
        platform_url = None

    # Normalize platform_url to avoid double slashes when building links
    if isinstance(platform_url, str):
        platform_url = platform_url.rstrip('/')

    return render_template("sources/list.html", sources=sources, platform_url=platform_url)


@bp.get("/add")
def add_source_view():
    # If a valid type is provided as query param, go directly to the form with that type preselected.
    # Otherwise, render the selection grid first.
    t = (request.args.get("type") or "").strip().lower()
    allowed = [
        "file",
        "csv",
        "excel",
        "folder",
        "postgresql",
        "mysql",
        "oracle",
        "mssql",
        "sqlite",
        "mongodb",
        "s3",
        "gcs",
        "azure_blob",
        "hdfs",
    ]
    if t and t in allowed:
        return render_template(
            "sources/edit.html", title="Add source", source=None, preselected_type=t
        )
    return render_template("sources/select-source.html")


@bp.post("/add")
def add_source_post():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()

    name = request.form.get("name", "").strip()
    s_type = request.form.get("type", "").strip()

    # Build config from form according to type
    config_section = {}
    if s_type == "file":
        p = request.form.get("file_path", "").strip()
        if p: config_section["path"] = p
    elif s_type == "folder":
        p = request.form.get("folder_path", "").strip()
        if p: config_section["path"] = p
    elif s_type == "sqlite":
        fpath = request.form.get("sqlite_file_path", "").strip()
        if fpath:
            config_section["type"] = "sqlite"
            config_section["file_path"] = fpath
    elif s_type == "csv":
        p = request.form.get("csv_path", "").strip()
        if p:
            config_section["path"] = p
        d = request.form.get("csv_delimiter", ",").strip() or ","
        e = request.form.get("csv_encoding", "utf-8").strip() or "utf-8"
        h = request.form.get("csv_header") == "on"
        config_section.update({
            "delimiter": d,
            "encoding": e,
            "has_header": h,
        })
    elif s_type == "excel":
        p = request.form.get("excel_path", "").strip()
        if p:
            config_section["path"] = p
        sheet = request.form.get("excel_sheet", "").strip()
        header_row = request.form.get("excel_header_row", "1").strip()
        config_section.update({
            "sheet": sheet,
            "header_row": header_row,
        })
    elif s_type in ["mysql", "postgresql", "oracle", "mssql"]:
        config_section.update({
            "type": s_type,
            "host": request.form.get("db_host", "").strip(),
            "port": request.form.get("db_port", "").strip(),
            "username": request.form.get("db_username", "").strip(),
            "password": request.form.get("db_password", "").strip(),
            "database": request.form.get("db_database", "").strip(),
            "table_or_query": request.form.get("db_table_or_query", "*").strip() or "*",
        })
        # Optional schema for PostgreSQL and Oracle
        if s_type in ("postgresql", "oracle"):
            schema = request.form.get("db_schema", "").strip()
            if schema:
                config_section["schema"] = schema
    elif s_type == "mongodb":
        config_section.update({
            "host": request.form.get("mongo_host", "").strip(),
            "port": request.form.get("mongo_port", "").strip(),
            "username": request.form.get("mongo_username", "").strip(),
            "password": request.form.get("mongo_password", "").strip(),
            "database": request.form.get("mongo_database", "").strip(),
        })
    elif s_type == "s3":
        config_section.update({
            "bucket": request.form.get("s3_bucket", "").strip(),
            "prefix": request.form.get("s3_prefix", "").strip(),
            "access_key": request.form.get("s3_access_key", "").strip(),
            "secret_key": request.form.get("s3_secret_key", "").strip(),
            "region": request.form.get("s3_region", "").strip(),
        })
    elif s_type == "gcs":
        config_section.update({
            "bucket": request.form.get("gcs_bucket", "").strip(),
            "prefix": request.form.get("gcs_prefix", "").strip(),
            "credentials_json": request.form.get("gcs_credentials", "").strip(),
        })
    elif s_type == "azure_blob":
        config_section.update({
            "container": request.form.get("az_container", "").strip(),
            "prefix": request.form.get("az_prefix", "").strip(),
            "connection_string": request.form.get("az_connection", "").strip(),
        })
    elif s_type == "hdfs":
        config_section.update({
            "namenode_host": request.form.get("hdfs_namenode", "").strip(),
            "port": request.form.get("hdfs_port", "").strip(),
            "user": request.form.get("hdfs_user", "").strip(),
            "path": request.form.get("hdfs_path", "").strip(),
        })

    new_source = {
        "name": name,
        "type": s_type,
        "description": request.form.get("description", "").strip(),
        "reference": request.form.get("reference") == "on",
        "sensitive": request.form.get("sensitive") == "on",
        "visibility": request.form.get("visibility", "private"),
        "config": config_section,
    }

    if not validate_source_object(cfg, new_source, skip_connection=False):
        return render_template("sources/edit.html", title="Add source", source=request.form, error="Validation failed. Check fields and connectivity.")

    cfg.config.setdefault("sources", []).append(new_source)
    cfg.save_source_config()
    # Validate all to compute status fields, then push only this source
    try:
        try:
            _validate_all.__wrapped__(cfg)  # type: ignore[attr-defined]
        except Exception:
            _validate_all(cfg)  # type: ignore[misc]
    except (SystemExit, Exception):
        # Gracefully skip full validation if agent context is not initialized
        pass
    try:
        push_single_programmatic(cfg, name, approve_public=False)
    except (SystemExit, Exception):
        # Skip push when not logged in / no .agent
        pass

    # Resolve platform_url as in list_sources
    platform_url = None
    try:
        backend_url = getattr(cfg, "url", None)
        try:
            env_path_file = os.path.join(getattr(cfg, "qalita_home", os.path.expanduser("~/.qalita")), ".current_env")
            if os.path.isfile(env_path_file):
                with open(env_path_file, 'r', encoding='utf-8') as f:
                    sel = f.read().strip()
                    if sel and os.path.isfile(sel):
                        with open(sel, 'r', encoding='utf-8') as ef:
                            for line in ef.readlines():
                                line = line.strip()
                                if not line or line.startswith('#') or '=' not in line:
                                    continue
                                k, v = line.split('=', 1)
                                k = k.strip().upper(); v = v.strip().strip('"').strip("'")
                                if k in ("QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"):
                                    backend_url = v
                                    break
        except Exception:
            pass
        if backend_url:
            try:
                r = send_request.__wrapped__(
                    cfg, request=f"{backend_url}/api/v1/info", mode="get"
                )  # type: ignore[attr-defined]
            except Exception:
                r = None
            if r is not None and getattr(r, "status_code", None) == 200:
                try:
                    platform_url = (r.json() or {}).get("public_platform_url")
                except Exception:
                    platform_url = None
    except Exception:
        platform_url = None
    if isinstance(platform_url, str):
        platform_url = platform_url.rstrip('/')

    # Try to get the created source id (if present after validate/push)
    src_id = None
    try:
        # Reload config to get potential IDs added during push/validate
        cfg.load_source_config()
        created = next((s for s in cfg.config.get("sources", []) if s.get("name") == name), None)
        src_id = created.get('id') if isinstance(created, dict) else None
    except Exception:
        src_id = None

    return render_template("sources/added.html", name=name, platform_url=platform_url, source_id=src_id)


@bp.get("/edit/<name>")
def edit_source_view(name):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    src = next((s for s in cfg.config.get("sources", []) if s.get("name") == name), None)
    return render_template("sources/edit.html", title="Edit source", source=src)


@bp.post("/edit/<name>")
def edit_source_post(name):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    sources = cfg.config.get("sources", [])
    for i, src in enumerate(sources):
        if src.get("name") == name:
            new_name = request.form.get("name", src.get("name", "")).strip()
            new_type = request.form.get("type", src.get("type", "")).strip()
            new_desc = request.form.get("description", src.get("description", "")).strip()
            new_vis = request.form.get("visibility", src.get("visibility", "private"))
            new_ref = request.form.get("reference") == "on"
            new_sens = request.form.get("sensitive") == "on"
            # Build config
            config_section: Dict[str, Any] = {}
            if new_type == "file":
                p = request.form.get("file_path", "").strip()
                if p: config_section["path"] = p
            elif new_type == "folder":
                p = request.form.get("folder_path", "").strip()
                if p: config_section["path"] = p
            elif new_type == "sqlite":
                fpath = request.form.get("sqlite_file_path", "").strip()
                if fpath:
                    config_section["type"] = "sqlite"
                    config_section["file_path"] = fpath
            elif new_type in ["mysql", "postgresql", "oracle", "mssql"]:
                config_section.update({
                    "type": new_type,
                    "host": request.form.get("db_host", "").strip(),
                    "port": request.form.get("db_port", "").strip(),
                    "username": request.form.get("db_username", "").strip(),
                    "password": request.form.get("db_password", "").strip(),
                    "database": request.form.get("db_database", "").strip(),
                    "table_or_query": request.form.get("db_table_or_query", "*").strip() or "*",
                })
                if new_type in ("postgresql", "oracle"):
                    schema = request.form.get("db_schema", "").strip()
                    if schema:
                        config_section["schema"] = schema
            elif new_type == "mongodb":
                config_section.update({
                    "host": request.form.get("mongo_host", "").strip(),
                    "port": request.form.get("mongo_port", "").strip(),
                    "username": request.form.get("mongo_username", "").strip(),
                    "password": request.form.get("mongo_password", "").strip(),
                    "database": request.form.get("mongo_database", "").strip(),
                })
            elif new_type == "csv":
                p = request.form.get("csv_path", "").strip()
                if p:
                    config_section["path"] = p
                d = request.form.get("csv_delimiter", ",").strip() or ","
                e = request.form.get("csv_encoding", "utf-8").strip() or "utf-8"
                h = request.form.get("csv_header") == "on"
                config_section.update({
                    "delimiter": d,
                    "encoding": e,
                    "has_header": h,
                })
            elif new_type == "excel":
                p = request.form.get("excel_path", "").strip()
                if p:
                    config_section["path"] = p
                sheet = request.form.get("excel_sheet", "").strip()
                header_row = request.form.get("excel_header_row", "1").strip()
                config_section.update({
                    "sheet": sheet,
                    "header_row": header_row,
                })
            elif new_type == "s3":
                config_section.update({
                    "bucket": request.form.get("s3_bucket", "").strip(),
                    "prefix": request.form.get("s3_prefix", "").strip(),
                    "access_key": request.form.get("s3_access_key", "").strip(),
                    "secret_key": request.form.get("s3_secret_key", "").strip(),
                    "region": request.form.get("s3_region", "").strip(),
                })
            elif new_type == "gcs":
                config_section.update({
                    "bucket": request.form.get("gcs_bucket", "").strip(),
                    "prefix": request.form.get("gcs_prefix", "").strip(),
                    "credentials_json": request.form.get("gcs_credentials", "").strip(),
                })
            elif new_type == "azure_blob":
                config_section.update({
                    "container": request.form.get("az_container", "").strip(),
                    "prefix": request.form.get("az_prefix", "").strip(),
                    "connection_string": request.form.get("az_connection", "").strip(),
                })
            elif new_type == "hdfs":
                config_section.update({
                    "namenode_host": request.form.get("hdfs_namenode", "").strip(),
                    "port": request.form.get("hdfs_port", "").strip(),
                    "user": request.form.get("hdfs_user", "").strip(),
                    "path": request.form.get("hdfs_path", "").strip(),
                })

            updated = {
                "name": new_name,
                "type": new_type,
                "description": new_desc,
                "visibility": new_vis,
                "reference": new_ref,
                "sensitive": new_sens,
                "config": config_section if config_section else src.get("config", {}),
            }

            if not validate_source_object(cfg, updated, skip_connection=False, exclude_name=name):
                return render_template("sources/edit.html", title="Edit source", source=request.form, error="Validation failed. Check fields and connectivity.")

            sources[i].update(updated)
            break
    cfg.save_source_config()
    # Re-validate and push only the edited source
    try:
        try:
            _validate_all.__wrapped__(cfg)  # type: ignore[attr-defined]
        except Exception:
            _validate_all(cfg)  # type: ignore[misc]
    except (SystemExit, Exception):
        pass
    try:
        push_single_programmatic(cfg, new_name, approve_public=False)
    except (SystemExit, Exception):
        pass
    return redirect(url_for("dashboard.dashboard"))


@bp.post("/delete/<name>")
def delete_source_post(name):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()
    cfg.config["sources"] = [s for s in cfg.config.get("sources", []) if s.get("name") != name]
    cfg.save_source_config()
    return redirect(url_for("dashboard.dashboard"))


@bp.get("/pick-file")
def pick_file():
    try:
        import tkinter as tk  # type: ignore
        from tkinter import filedialog  # type: ignore

        root = tk.Tk()
        root.withdraw()
        try:
            root.wm_attributes("-topmost", 1)
        except Exception:
            pass
        path = filedialog.askopenfilename()
        root.update()
        root.destroy()
        return jsonify({"path": path})
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Picker unavailable: {exc}"}), 500


@bp.get("/pick-folder")
def pick_folder():
    try:
        import tkinter as tk  # type: ignore
        from tkinter import filedialog  # type: ignore

        root = tk.Tk()
        root.withdraw()
        try:
            root.wm_attributes("-topmost", 1)
        except Exception:
            pass
        path = filedialog.askdirectory()
        root.update()
        root.destroy()
        return jsonify({"path": path})
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Picker unavailable: {exc}"}), 500


# Lightweight validation endpoint for the edit form (no save/push)
@bp.post("/validate")
def validate_source_form():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    cfg.load_source_config()

    # Accept either JSON or form-encoded payload
    data = request.get_json(silent=True) or request.form or {}

    def _get(name: str) -> str:
        v = data.get(name)
        if isinstance(v, list):
            return (v[0] or "").strip()
        return (v or "").strip()

    name = _get("name")
    s_type = _get("type")
    original_name = _get("original_name") or None

    # Build config from payload mirroring add/edit logic
    config_section: Dict[str, Any] = {}
    if s_type == "file":
        p = _get("file_path")
        if p:
            config_section["path"] = p
    elif s_type == "folder":
        p = _get("folder_path")
        if p:
            config_section["path"] = p
    elif s_type == "sqlite":
        fpath = _get("sqlite_file_path")
        if fpath:
            config_section["type"] = "sqlite"
            config_section["file_path"] = fpath
    elif s_type in ["mysql", "postgresql", "oracle", "mssql"]:
        config_section.update(
            {
                "type": s_type,
                "host": _get("db_host"),
                "port": _get("db_port"),
                "username": _get("db_username"),
                "password": _get("db_password"),
                "database": _get("db_database"),
                "table_or_query": _get("db_table_or_query") or "*",
            }
        )
        if s_type in ("postgresql", "oracle"):
            schema = _get("db_schema")
            if schema:
                config_section["schema"] = schema
    elif s_type == "mongodb":
        config_section.update(
            {
                "host": _get("mongo_host"),
                "port": _get("mongo_port"),
                "username": _get("mongo_username"),
                "password": _get("mongo_password"),
                "database": _get("mongo_database"),
            }
        )
    elif s_type == "csv":
        p = _get("csv_path")
        if p:
            config_section["path"] = p
        d = _get("csv_delimiter") or ","
        e = _get("csv_encoding") or "utf-8"
        h = (_get("csv_header").lower() == "on") if isinstance(data, dict) else False
        config_section.update(
            {
                "delimiter": d,
                "encoding": e,
                "has_header": h,
            }
        )
    elif s_type == "excel":
        p = _get("excel_path")
        if p:
            config_section["path"] = p
        sheet = _get("excel_sheet")
        header_row = _get("excel_header_row") or "1"
        config_section.update(
            {
                "sheet": sheet,
                "header_row": header_row,
            }
        )
    elif s_type == "s3":
        config_section.update(
            {
                "bucket": _get("s3_bucket"),
                "prefix": _get("s3_prefix"),
                "access_key": _get("s3_access_key"),
                "secret_key": _get("s3_secret_key"),
                "region": _get("s3_region"),
            }
        )
    elif s_type == "gcs":
        config_section.update(
            {
                "bucket": _get("gcs_bucket"),
                "prefix": _get("gcs_prefix"),
                "credentials_json": _get("gcs_credentials"),
            }
        )
    elif s_type == "azure_blob":
        config_section.update(
            {
                "container": _get("az_container"),
                "prefix": _get("az_prefix"),
                "connection_string": _get("az_connection"),
            }
        )
    elif s_type == "hdfs":
        config_section.update(
            {
                "namenode_host": _get("hdfs_namenode"),
                "port": _get("hdfs_port"),
                "user": _get("hdfs_user"),
                "path": _get("hdfs_path"),
            }
        )

    candidate = {
        "name": name,
        "type": s_type,
        "description": _get("description"),
        "reference": (_get("reference").lower() == "on") if isinstance(data, dict) else False,
        "sensitive": (_get("sensitive").lower() == "on") if isinstance(data, dict) else False,
        "visibility": _get("visibility") or "private",
        "config": config_section,
    }

    ok = validate_source_object(cfg, candidate, skip_connection=False, exclude_name=original_name)
    if ok:
        return jsonify({"ok": True, "message": "Source is valid."})
    return jsonify({"ok": False, "message": "Validation failed. Check fields and connectivity."}), 400

