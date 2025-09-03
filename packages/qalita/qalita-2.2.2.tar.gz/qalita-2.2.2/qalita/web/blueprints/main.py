"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import re
from datetime import datetime
import shutil
from flask import (
    Blueprint,
    current_app,
    render_template,
    jsonify,
    request,
)
import os
import sys
import signal
import subprocess
from qalita.internal.utils import logger, validate_token, get_version
from qalita.commands.agent import authenticate, send_alive
from qalita.internal.request import send_request


bp = Blueprint("main", __name__)


@bp.route("/")
def dashboard():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf = None
    try:
        raw = cfg.load_agent_config()
        # Map nested raw config to flat fields expected by the template
        if isinstance(raw, dict) and raw:

            def pick(obj, *path):
                cur = obj
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        return ""
                    cur = cur[key]
                return cur

            agent_conf = {
                "name": pick(raw, "context", "remote", "name") or raw.get("name", ""),
                "mode": raw.get("mode", ""),
                "url": pick(raw, "context", "local", "url") or raw.get("url", ""),
                "agent_id": pick(raw, "context", "remote", "id")
                or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except Exception:
        agent_conf = None
    # Overlay with selected context values (immediate UI reflect of selection)
    try:
        env_path = _read_selected_env()
        if env_path:
            data = _parse_env_file(env_path)
            if agent_conf is None:
                agent_conf = {}
            agent_conf["name"] = (
                data.get("QALITA_AGENT_NAME")
                or data.get("AGENT_NAME")
                or data.get("NAME")
                or agent_conf.get("name", "")
            )
            agent_conf["mode"] = (
                data.get("QALITA_AGENT_MODE")
                or data.get("AGENT_MODE")
                or data.get("MODE")
                or agent_conf.get("mode", "")
            )
            agent_conf["url"] = (
                data.get("QALITA_AGENT_ENDPOINT")
                or data.get("QALITA_URL")
                or data.get("URL")
                or agent_conf.get("url", "")
            )
    except Exception:
        pass
    try:
        pass
    except Exception:
        pass
    # As a final overlay, prefer values currently set on cfg (applied via _login_with_env)
    try:
        if agent_conf is None:
            agent_conf = {}
        if not agent_conf.get("name"):
            agent_conf["name"] = getattr(cfg, "name", "") or agent_conf.get("name", "")
        if not agent_conf.get("mode"):
            agent_conf["mode"] = getattr(cfg, "mode", "") or agent_conf.get("mode", "")
        if not agent_conf.get("url"):
            agent_conf["url"] = getattr(cfg, "url", "") or agent_conf.get("url", "")
    except Exception:
        pass
    try:
        pass
    except Exception:
        pass
    cfg.load_source_config()
    sources = list(reversed(cfg.config.get("sources", [])))
    # Resolve public platform URL from backend /api/v1/info using the agent backend URL (non-intrusive)
    platform_url = None
    try:
        backend_url = getattr(cfg, "url", None)
        try:
            env_path_file = os.path.join(
                getattr(cfg, "qalita_home", os.path.expanduser("~/.qalita")),
                ".current_env",
            )
            if os.path.isfile(env_path_file):
                with open(env_path_file, "r", encoding="utf-8") as f:
                    sel = f.read().strip()
                    if sel and os.path.isfile(sel):
                        with open(sel, "r", encoding="utf-8") as ef:
                            for line in ef.readlines():
                                line = line.strip()
                                if not line or line.startswith("#") or "=" not in line:
                                    continue
                                k, v = line.split("=", 1)
                                k = k.strip().upper()
                                v = v.strip().strip('"').strip("'")
                                if k in (
                                    "QALITA_AGENT_ENDPOINT",
                                    "AGENT_ENDPOINT",
                                    "QALITA_URL",
                                    "URL",
                                ):
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
        platform_url = platform_url.rstrip("/")
    # Build agent run list from agent_run_temp
    agent_runs = []
    try:
        run_root = cfg.get_agent_run_path()
        if os.path.isdir(run_root):
            pattern = re.compile(r"^\d{14}_[a-z0-9]{5}$")
            for entry in sorted(os.listdir(run_root), reverse=True):
                if pattern.match(entry) and os.path.isdir(
                    os.path.join(run_root, entry)
                ):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except Exception:
                        when = ts
                    agent_runs.append(
                        {
                            "name": entry,
                            "path": os.path.join(run_root, entry),
                            "timestamp": ts,
                            "when": when,
                        }
                    )
    except Exception:
        agent_runs = []
    # Pagination for runs
    try:
        page = int((request.args.get("runs_page") or "1").strip() or "1")
    except Exception:
        page = 1
    try:
        per_page = int((request.args.get("runs_per_page") or "10").strip() or "10")
    except Exception:
        per_page = 10
    if page < 1:
        page = 1
    if per_page <= 0:
        per_page = 10
    total_runs = len(agent_runs)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    agent_runs_page = agent_runs[start_idx:end_idx]
    runs_has_prev = start_idx > 0
    runs_has_next = end_idx < total_runs
    runs_start = (start_idx + 1) if total_runs > 0 and start_idx < total_runs else 0
    runs_end = min(end_idx, total_runs) if total_runs > 0 else 0
    # Guarantee agent_conf is a non-empty dict for the template (avoid falsy checks)
    try:
        if not agent_conf or not isinstance(agent_conf, dict):
            agent_conf = {}
        agent_conf.setdefault("name", getattr(cfg, "name", "") or agent_conf.get("name", ""))
        agent_conf.setdefault("mode", getattr(cfg, "mode", "") or agent_conf.get("mode", ""))
        agent_conf.setdefault("url", getattr(cfg, "url", "") or agent_conf.get("url", ""))
    except Exception:
        pass
    return render_template(
        "dashboard.html",
        agent_conf=agent_conf,
        sources=sources,
        agent_runs=agent_runs,
        agent_runs_page=agent_runs_page,
        runs_total=total_runs,
        runs_page=page,
        runs_per_page=per_page,
        runs_has_prev=runs_has_prev,
        runs_has_next=runs_has_next,
        runs_start=runs_start,
        runs_end=runs_end,
        platform_url=platform_url,
    )


@bp.post("/validate")
def validate_sources():
    from qalita.commands.source import validate_source as _validate

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # Run validation
    try:
        _validate.__wrapped__(cfg)  # type: ignore[attr-defined]
    except Exception:
        _validate(cfg)  # type: ignore[misc]
    # Build feedback from results
    try:
        cfg.load_source_config()
        sources = cfg.config.get("sources", []) or []
        total = len(sources)
        valid_count = sum(
            1 for s in sources if (s.get("validate") or "").lower() == "valid"
        )
        invalid_count = sum(
            1 for s in sources if (s.get("validate") or "").lower() == "invalid"
        )
        msg = (
            f"Validated {total} source(s): {valid_count} valid, {invalid_count} invalid"
        )
        level = "info" if invalid_count == 0 else "error"
    except Exception:
        msg = "Validation completed."
        level = "info"
    # Render dashboard with feedback
    return dashboard_with_feedback(msg, level)


@bp.post("/push")
def push_sources():
    from flask import request
    from qalita.commands.source import push_programmatic

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # For web, we do not want interactive confirms, so public approvals are off by default
    try:
        ok, message = push_programmatic(cfg, skip_validate=False, approve_public=False)
    except Exception as exc:
        ok, message = False, f"Push failed: {exc}"
    level = "info" if ok else "error"
    return dashboard_with_feedback(message, level)


@bp.post("/pack/push")
def push_pack_from_ui():
    from flask import request
    from qalita.commands.pack import push_from_directory

    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    pack_dir = request.form.get("pack_dir", "").strip()
    feedback = None
    feedback_level = "info"
    if pack_dir:
        ok, message = push_from_directory(cfg, pack_dir)
        feedback = message or (
            "Pack pushed successfully." if ok else "Pack push failed."
        )
        feedback_level = "info" if ok else "error"
    else:
        feedback = "Please select a pack folder."
        feedback_level = "error"
    # Refresh dashboard with feedback
    return dashboard_with_feedback(feedback, feedback_level)


def dashboard_with_feedback(feedback_msg=None, feedback_level: str = "info"):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf = None
    try:
        raw = cfg.load_agent_config()
        if isinstance(raw, dict) and raw:

            def pick(obj, *path):
                cur = obj
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        return ""
                    cur = cur[key]
                return cur

            agent_conf = {
                "name": pick(raw, "context", "remote", "name") or raw.get("name", ""),
                "mode": raw.get("mode", ""),
                "url": pick(raw, "context", "local", "url") or raw.get("url", ""),
                "agent_id": pick(raw, "context", "remote", "id")
                or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except Exception:
        agent_conf = None
    # Overlay with selected context values
    try:
        env_path = _read_selected_env()
        if env_path:
            data = _parse_env_file(env_path)
            if agent_conf is None:
                agent_conf = {}
            agent_conf["name"] = (
                data.get("QALITA_AGENT_NAME")
                or data.get("AGENT_NAME")
                or data.get("NAME")
                or agent_conf.get("name", "")
            )
            agent_conf["mode"] = (
                data.get("QALITA_AGENT_MODE")
                or data.get("AGENT_MODE")
                or data.get("MODE")
                or agent_conf.get("mode", "")
            )
            agent_conf["url"] = (
                data.get("QALITA_AGENT_ENDPOINT")
                or data.get("QALITA_URL")
                or data.get("URL")
                or agent_conf.get("url", "")
            )
    except Exception:
        pass
    # Final overlay from cfg state
    try:
        if agent_conf is None:
            agent_conf = {}
        if not agent_conf.get("name"):
            agent_conf["name"] = getattr(cfg, "name", "") or agent_conf.get("name", "")
        if not agent_conf.get("mode"):
            agent_conf["mode"] = getattr(cfg, "mode", "") or agent_conf.get("mode", "")
        if not agent_conf.get("url"):
            agent_conf["url"] = getattr(cfg, "url", "") or agent_conf.get("url", "")
    except Exception:
        pass
    cfg.load_source_config()
    sources = list(reversed(cfg.config.get("sources", [])))
    # Resolve public platform URL similarly for feedback rendering
    platform_url = None
    try:
        backend_url = getattr(cfg, "url", None)
        try:
            env_path_file = os.path.join(
                getattr(cfg, "qalita_home", os.path.expanduser("~/.qalita")),
                ".current_env",
            )
            if os.path.isfile(env_path_file):
                with open(env_path_file, "r", encoding="utf-8") as f:
                    sel = f.read().strip()
                    if sel and os.path.isfile(sel):
                        with open(sel, "r", encoding="utf-8") as ef:
                            for line in ef.readlines():
                                line = line.strip()
                                if not line or line.startswith("#") or "=" not in line:
                                    continue
                                k, v = line.split("=", 1)
                                k = k.strip().upper()
                                v = v.strip().strip('"').strip("'")
                                if k in (
                                    "QALITA_AGENT_ENDPOINT",
                                    "AGENT_ENDPOINT",
                                    "QALITA_URL",
                                    "URL",
                                ):
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
        platform_url = platform_url.rstrip("/")
    # Build agent runs
    agent_runs = []
    try:
        run_root = cfg.get_agent_run_path()
        if os.path.isdir(run_root):
            pattern = re.compile(r"^\d{14}_[a-z0-9]{5}$")
            for entry in sorted(os.listdir(run_root), reverse=True):
                if pattern.match(entry) and os.path.isdir(
                    os.path.join(run_root, entry)
                ):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except Exception:
                        when = ts
                    agent_runs.append(
                        {
                            "name": entry,
                            "path": os.path.join(run_root, entry),
                            "timestamp": ts,
                            "when": when,
                        }
                    )
    except Exception:
        agent_runs = []
    # Pagination for runs
    try:
        page = int((request.args.get("runs_page") or "1").strip() or "1")
    except Exception:
        page = 1
    try:
        per_page = int((request.args.get("runs_per_page") or "10").strip() or "10")
    except Exception:
        per_page = 10
    if page < 1:
        page = 1
    if per_page <= 0:
        per_page = 10
    total_runs = len(agent_runs)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    agent_runs_page = agent_runs[start_idx:end_idx]
    runs_has_prev = start_idx > 0
    runs_has_next = end_idx < total_runs
    runs_start = (start_idx + 1) if total_runs > 0 and start_idx < total_runs else 0
    runs_end = min(end_idx, total_runs) if total_runs > 0 else 0
    # Guarantee agent_conf is a non-empty dict for the template (avoid falsy checks)
    try:
        if not agent_conf or not isinstance(agent_conf, dict):
            agent_conf = {}
        agent_conf.setdefault("name", getattr(cfg, "name", "") or agent_conf.get("name", ""))
        agent_conf.setdefault("mode", getattr(cfg, "mode", "") or agent_conf.get("mode", ""))
        agent_conf.setdefault("url", getattr(cfg, "url", "") or agent_conf.get("url", ""))
    except Exception:
        pass
    return render_template(
        "dashboard.html",
        agent_conf=agent_conf,
        sources=sources,
        agent_runs=agent_runs,
        agent_runs_page=agent_runs_page,
        runs_total=total_runs,
        runs_page=page,
        runs_per_page=per_page,
        runs_has_prev=runs_has_prev,
        runs_has_next=runs_has_next,
        runs_start=runs_start,
        runs_end=runs_end,
        feedback=feedback_msg,
        feedback_level=feedback_level,
        platform_url=platform_url,
    )


# Helper to compute agent summary (conf + runs)
def _compute_agent_summary(cfg):
    agent_conf = None
    try:
        raw = cfg.load_agent_config()
        if isinstance(raw, dict) and raw:

            def pick(obj, *path):
                cur = obj
                for key in path:
                    if not isinstance(cur, dict) or key not in cur:
                        return ""
                    cur = cur[key]
                return cur

            agent_conf = {
                "name": pick(raw, "context", "remote", "name") or raw.get("name", ""),
                "mode": raw.get("mode", ""),
                "url": pick(raw, "context", "local", "url") or raw.get("url", ""),
                "agent_id": pick(raw, "context", "remote", "id")
                or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except Exception:
        agent_conf = None
    # Overlay with selected context values
    try:
        env_path = _read_selected_env()
        if env_path:
            data = _parse_env_file(env_path)
            if agent_conf is None:
                agent_conf = {}
            agent_conf["name"] = (
                data.get("QALITA_AGENT_NAME")
                or data.get("AGENT_NAME")
                or data.get("NAME")
                or agent_conf.get("name", "")
            )
            agent_conf["mode"] = (
                data.get("QALITA_AGENT_MODE")
                or data.get("AGENT_MODE")
                or data.get("MODE")
                or agent_conf.get("mode", "")
            )
            agent_conf["url"] = (
                data.get("QALITA_AGENT_ENDPOINT")
                or data.get("QALITA_URL")
                or data.get("URL")
                or agent_conf.get("url", "")
            )
    except Exception:
        pass
    # Final overlay from live cfg values
    try:
        if agent_conf is None:
            agent_conf = {}
        if not agent_conf.get("name"):
            agent_conf["name"] = getattr(cfg, "name", "") or agent_conf.get("name", "")
        if not agent_conf.get("mode"):
            agent_conf["mode"] = getattr(cfg, "mode", "") or agent_conf.get("mode", "")
        if not agent_conf.get("url"):
            agent_conf["url"] = getattr(cfg, "url", "") or agent_conf.get("url", "")
    except Exception:
        pass
    # Build agent runs
    agent_runs = []
    try:
        run_root = cfg.get_agent_run_path()
        if os.path.isdir(run_root):
            pattern = re.compile(r"^\d{14}_[a-z0-9]{5}$")
            for entry in sorted(os.listdir(run_root), reverse=True):
                if pattern.match(entry) and os.path.isdir(
                    os.path.join(run_root, entry)
                ):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except Exception:
                        when = ts
                    agent_runs.append(
                        {
                            "name": entry,
                            "path": os.path.join(run_root, entry),
                            "timestamp": ts,
                            "when": when,
                        }
                    )
    except Exception:
        agent_runs = []
    return agent_conf, agent_runs


@bp.get("/agent/summary")
def agent_summary():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf, agent_runs = _compute_agent_summary(cfg)
    return jsonify(
        {
            "agent_conf": agent_conf or {},
            "agent_runs": agent_runs,
        }
    )


# ---- Context management (env-based) ----


def _qalita_home():
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    try:
        return os.path.normpath(cfg.qalita_home)  # type: ignore[attr-defined]
    except Exception:
        import os

        return os.path.normpath(os.path.expanduser("~/.qalita"))


def _list_env_files():
    import os

    root = _qalita_home()
    files = []
    try:
        for name in os.listdir(root):
            lower = name.lower()
            if lower.startswith(".env") or lower.endswith(".env"):
                files.append(
                    {
                        "name": name,
                        "path": os.path.normpath(os.path.join(root, name)),
                    }
                )
    except Exception:
        files = []
    files.sort(key=lambda x: x["name"])  # stable order
    return files


def _selected_env_file_path():
    import os

    return os.path.normpath(os.path.join(_qalita_home(), ".current_env"))


def _read_selected_env():
    import os

    p = _selected_env_file_path()
    try:
        with open(p, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            path = os.path.normpath(raw) if raw else None
            # If the path exists as-is, return it
            if path and os.path.isfile(path):
                # Also keep the env file in sync with current process env variables
                try:
                    _materialize_env_from_process_env(path)
                except Exception:
                    pass
                return path
            # If it doesn't exist (e.g., absolute path from host), try remapping to current QALITA_HOME
            try:
                base = _qalita_home()
                if path:
                    candidate = os.path.normpath(os.path.join(base, os.path.basename(path)))
                    # If the candidate exists, use it
                    if os.path.isfile(candidate):
                        logger.warning(
                            f"Selected env pointer [{path}] not found. Using [{candidate}] under current QALITA_HOME."
                        )
                        # Sync with current process env variables
                        try:
                            _materialize_env_from_process_env(candidate)
                        except Exception:
                            pass
                        # Rewrite pointer to the resolved path
                        try:
                            with open(p, "w", encoding="utf-8") as pf:
                                pf.write(candidate)
                        except Exception:
                            pass
                        return candidate
                    # If not found, create it from process environment
                    try:
                        os.makedirs(base, exist_ok=True)
                        _materialize_env_from_process_env(candidate)
                        logger.warning(
                            f"Selected env pointer [{path}] not found. Created [{candidate}] under current QALITA_HOME from environment."
                        )
                        # Rewrite pointer to the newly created file
                        try:
                            with open(p, "w", encoding="utf-8") as pf:
                                pf.write(candidate)
                        except Exception:
                            pass
                        return candidate
                    except Exception:
                        pass
            except Exception:
                pass
            # Fallback: use default .env-<QALITA_AGENT_NAME>
            return _ensure_default_env_selected(p)
    except Exception:
        logger.warning(f"No selected env pointer found at [{p}] or failed to read it")
        # Fallback: use default .env-<QALITA_AGENT_NAME>
        return _ensure_default_env_selected(p)


def _materialize_env_from_process_env(target_path: str) -> None:
    """Create or update an env file at target_path using current process environment variables.

    - If the file exists, update/override keys present in process env and keep other keys untouched.
    - If it does not exist, create it with keys available in process env.
    Relevant keys include multiple aliases to support existing conventions.
    """
    try:
        existing: dict[str, str] = {}
        if os.path.isfile(target_path):
            existing = _parse_env_file(target_path) or {}
        # Collect values from environment with precedence
        env = os.environ
        # Build updates from env for known keys (aliases included)
        key_groups = [
            ("QALITA_AGENT_NAME", ["QALITA_AGENT_NAME", "AGENT_NAME", "NAME"]),
            ("QALITA_AGENT_MODE", ["QALITA_AGENT_MODE", "AGENT_MODE", "MODE"]),
            ("QALITA_AGENT_TOKEN", ["QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN"]),
            ("QALITA_AGENT_ENDPOINT", ["QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"]),
        ]
        updates: dict[str, str] = {}
        for canonical, aliases in key_groups:
            value = None
            for k in aliases:
                if k in env and env.get(k):
                    value = env.get(k)
                    # Preserve the exact provided key name rather than always canonical
                    updates[k] = value  # type: ignore[assignment]
                    break
            # If nothing found, leave untouched
        # Merge and write back
        merged = dict(existing)
        merged.update(updates)
        # Serialize as KEY=VALUE lines, stable order (by key)
        lines = []
        for k in sorted(merged.keys()):
            v = merged[k]
            if v is None:
                continue
            # Quote only when needed (wrap in double quotes and escape inner quotes)
            if any(ch.isspace() for ch in str(v)):
                escaped = str(v).replace('"', '\\"')
                lines.append(f'{k}="{escaped}"')
            else:
                lines.append(f"{k}={v}")
        content = "\n".join(lines) + ("\n" if lines else "")
        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as wf:
            wf.write(content)
    except Exception:
        # Non-fatal: caller should continue gracefully
        pass


def _ensure_default_env_selected(pointer_path: str):
    """Ensure there is a default selected env file named .env-<QALITA_AGENT_NAME>.

    Creates/updates it from current process env vars and updates the pointer file.
    Returns the absolute path to the env file, or None on failure.
    """
    try:
        base = _qalita_home()
        env = os.environ
        # Determine agent name from ENV first, then from persisted cfg, then fallback
        name = env.get("QALITA_AGENT_NAME") or env.get("AGENT_NAME") or env.get("NAME")
        if not name:
            try:
                cfg = current_app.config.get("QALITA_CONFIG_OBJ")
                name = getattr(cfg, "name", None)
            except Exception:
                name = None
        if not name:
            name = "agent"
        # Sanitize for filename
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name)).strip("-_.") or "agent"
        target = os.path.normpath(os.path.join(base, f".env-{safe}"))
        os.makedirs(base, exist_ok=True)
        _materialize_env_from_process_env(target)
        try:
            with open(pointer_path, "w", encoding="utf-8") as pf:
                pf.write(target)
        except Exception:
            pass
        return target
    except Exception:
        return None


def _agent_pid_file_path():
    import os

    return os.path.join(_qalita_home(), "agent_run.pid")


def _read_agent_pid():
    import os

    p = _agent_pid_file_path()
    try:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                return int(raw) if raw else None
    except Exception:
        return None
    return None


def _agent_log_file_path():
    import os

    return os.path.join(_qalita_home(), "agent_run.log")


def _is_pid_running(pid: int) -> bool:
    try:
        if os.name == "nt":
            # On Windows, use tasklist to check if the PID exists
            try:
                result = subprocess.run(
                    [
                        "tasklist",
                        "/FI",
                        f"PID eq {int(pid)}",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    return False
                # The filtered output will include the PID if the process exists
                return str(int(pid)) in result.stdout
            except Exception:
                return False
        else:
            # Signal 0 does not kill the process; it just checks existence/permission
            os.kill(int(pid), 0)
            return True
    except Exception:
        return False


def _agent_status_payload() -> dict:
    pid = _read_agent_pid()
    running = bool(pid) and _is_pid_running(int(pid))
    return {"running": running, "pid": int(pid) if running else None}


@bp.get("/contexts")
def list_contexts():
    files = _list_env_files()
    selected = _read_selected_env()
    # Align selected with items for Windows case-insensitive matching
    try:
        if selected:
            sel_norm = os.path.normcase(os.path.normpath(selected))
            for it in files:
                if os.path.normcase(os.path.normpath(it.get("path", ""))) == sel_norm:
                    selected = it.get("path")
                    break
    except Exception:
        pass
    return jsonify(
        {
            "items": files,
            "selected": selected,
        }
    )


@bp.post("/context/select")
def select_context():
    import os

    data = request.get_json(silent=True) or {}
    path = (data.get("path") or "").strip()

    ok = False
    message = ""
    if not path:
        # clear selection
        try:
            p = _selected_env_file_path()
            if os.path.exists(p):
                os.remove(p)
            ok = True
            message = "Selection cleared"

        except Exception as exc:
            ok = False
            message = f"Failed to clear selection: {exc}"
    else:
        try:
            # Ensure the file exists under qalita home
            root = _qalita_home()
            abs_root = os.path.abspath(root)
            abs_path = os.path.abspath(path)

            if not abs_path.startswith(abs_root + os.sep):
                logger.warning("Invalid context path outside qalita home")
                return jsonify({"ok": False, "message": "Invalid path"}), 400
            if not os.path.isfile(abs_path):
                logger.warning("Context env file not found on disk")
                return jsonify({"ok": False, "message": "Env file not found"}), 404
            with open(_selected_env_file_path(), "w", encoding="utf-8") as f:
                f.write(abs_path)

            # After selecting, perform agent login with this context
            try:
                _login_with_env(abs_path)
                ok = True
                message = "Context selected and agent logged in"

            except Exception as exc:
                logger.error(f"Context select: login failed: {exc}")
                ok = False
                message = f"Selected, but login failed: {exc}"
        except Exception as exc:
            ok = False
            message = f"Failed to select context: {exc}"
    # Attach latest agent summary for immediate UI refresh
    try:
        cfg = current_app.config["QALITA_CONFIG_OBJ"]
        agent_conf, agent_runs = _compute_agent_summary(cfg)
    except Exception:
        agent_conf, agent_runs = None, []
    return jsonify(
        {
            "ok": ok,
            "message": message,
            "agent_conf": agent_conf or {},
            "agent_runs": agent_runs,
        }
    )


def _parse_env_file(env_path: str) -> dict:
    """Very small .env parser: KEY=VALUE per line, ignores comments/blank lines."""
    vars: dict[str, str] = {}
    try:

        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip().lstrip("\ufeff")  # remove potential UTF-8 BOM
                v = v.strip().strip('"').strip("'")
                vars[k] = v

    except Exception:
        logger.error(f"Failed reading env file: [{env_path}]")
        pass
    return vars


def _login_with_env(env_path: str) -> None:
    """Use env file to configure agent and perform login programmatically."""
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    data = _parse_env_file(env_path)


    # Resolve fields with multiple aliases
    def pick(*names: str, default: str | None = None) -> str | None:
        for n in names:
            if n in data and data[n]:
                return data[n]
        return default

    name = (
        pick("QALITA_AGENT_NAME", "AGENT_NAME", "NAME")
        or getattr(cfg, "name", None)
        or "agent"
    )
    mode = (
        pick("QALITA_AGENT_MODE", "AGENT_MODE", "MODE")
        or getattr(cfg, "mode", None)
        or "job"
    )
    token = pick("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN") or getattr(
        cfg, "token", None
    )
    url = pick("QALITA_AGENT_ENDPOINT", "QALITA_URL", "URL") or getattr(
        cfg, "url", None
    )

    if not token or not url:
        raise RuntimeError("Missing TOKEN or URL in context .env")

    # Apply on config
    cfg.name = name
    cfg.mode = mode
    cfg.token = token
    cfg.url = url


    # Version check (best-effort)
    try:
        r = send_request.__wrapped__(cfg, request=f"{cfg.url}/api/v1/version", mode="get")  # type: ignore[attr-defined]
        if r.status_code == 200:
            v = r.json().get("version")
            if v and v != get_version():
                pass
    except Exception:
        pass


@bp.get("/agent/status")
def agent_status():
    return jsonify(_agent_status_payload())


@bp.post("/agent/start")
def agent_start():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    # We will determine the agent name AFTER applying the selected context
    # to ensure the selected .env takes priority over persisted config
    agent_name = None

    # If already running, return ok
    st = _agent_status_payload()
    if st.get("running"):
        return jsonify({"ok": True, "already_running": True, **st})

    # Ensure current context is applied and agent login is valid before starting
    try:
        sel_path = _read_selected_env()
        if sel_path and os.path.isfile(sel_path):
            logger.info(f"agent_start: applying selected env at [{sel_path}]")
            _login_with_env(sel_path)

    except Exception as exc:
        logger.error(f"agent_start: failed applying selected env: {exc}")
        return jsonify({"ok": False, "error": f"Failed to apply selected context: {exc}"}), 400

    # Determine agent name with precedence: selected env -> cfg.name -> persisted remote -> default
    try:
        sel_path = _read_selected_env()
        if sel_path and os.path.isfile(sel_path):
            data = _parse_env_file(sel_path)
            agent_name = (
                data.get("QALITA_AGENT_NAME")
                or data.get("AGENT_NAME")
                or data.get("NAME")
                or None
            )
    except Exception:
        agent_name = None
    if not agent_name:
        try:
            agent_name = getattr(cfg, "name", None) or None
        except Exception:
            agent_name = None
    if not agent_name:
        try:
            raw = cfg.load_agent_config()
            if isinstance(raw, dict) and raw:
                agent_name = (
                    (raw.get("context", {}).get("remote", {}) or {}).get("name")
                    or raw.get("name")
                    or None
                )
        except Exception:
            agent_name = None
    if not agent_name:
        agent_name = "agent"


    # Validate token against backend endpoints without requiring Click context
    try:
        validated = validate_token(cfg.token)
        user_id = validated.get("user_id") if isinstance(validated, dict) else None
        if not user_id:
            return jsonify({"ok": False, "error": "Invalid or missing TOKEN in current context"}), 400
        # Check backend version (reachability)
        try:
            r = send_request.__wrapped__(
                cfg, request=f"{cfg.url}/api/v1/version", mode="get"
            )  # type: ignore[attr-defined]
        except Exception:
            r = None
        if r is None or getattr(r, "status_code", None) != 200:
            logger.error("Preflight failed: /api/v1/version not reachable or not 200")
            return jsonify({"ok": False, "error": "Backend unreachable or /api/v1/version not 200"}), 400
        # Check user endpoint with token
        try:
            r2 = send_request.__wrapped__(
                cfg, request=f"{cfg.url}/api/v2/users/{user_id}", mode="get"
            )  # type: ignore[attr-defined]
        except Exception:
            r2 = None
        if r2 is None or getattr(r2, "status_code", None) != 200:
            logger.error("Preflight failed: /api/v2/users/{user_id} not 200 (invalid token?)")
            return jsonify({"ok": False, "error": "Token invalid or user not accessible"}), 400
    except Exception as exc:
        logger.error(f"Preflight login check failed: {exc}")
        return jsonify({"ok": False, "error": f"Preflight login check failed: {exc}"}), 400

    # Launch the agent in background: qalita agent run -n <name>
    try:
        # Propagate the selected context environment variables to the subprocess (simple KEY=VALUE parsing)
        env = dict(os.environ)
        # Ensure CLI uses the same QALITA_HOME as UI
        try:
            env["QALITA_HOME"] = os.path.normpath(cfg.qalita_home)  # type: ignore[attr-defined]
        except Exception:
            env["QALITA_HOME"] = os.path.normpath(os.path.expanduser("~/.qalita"))
        logger.info(f"agent_start: QALITA_HOME resolved to [{env.get('QALITA_HOME')}]")
        try:
            sel_path = _read_selected_env()
            if sel_path and os.path.isfile(sel_path):
                with open(sel_path, "r", encoding="utf-8") as ef:
                    for line in ef.readlines():
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v:
                            env[k] = v
        except Exception:
            pass
        # Force worker mode if not set in environment
        try:
            if not any(env.get(k) for k in ("QALITA_AGENT_MODE", "AGENT_MODE", "MODE")):
                env["QALITA_AGENT_MODE"] = "worker"
        except Exception:
            env["QALITA_AGENT_MODE"] = "worker"
        logger.info(f"agent_start: effective agent mode is [{env.get('QALITA_AGENT_MODE') or env.get('AGENT_MODE') or env.get('MODE')}]")
        # Prefer python -m on Windows to avoid PATH resolution issues; use binary on others
        if os.name == "nt":
            python_bin = sys.executable or "python"
            cmd = [
                python_bin,
                "-m",
                "qalita",
                "agent",
                "-n",
                str(agent_name),
                "-m",
                "worker",
                "run",
            ]
            logger.info(f"agent_start: using python interpreter [{python_bin}]")
        else:
            cmd = [
                "qalita",
                "agent",
                "-n",
                str(agent_name),
                "-m",
                "worker",
                "run",
            ]
        logger.info(f"agent_start: executing command: {' '.join(cmd)}")
        # Redirect output to log file to avoid PIPE deadlocks and allow post-mortem debugging
        log_path = _agent_log_file_path()
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        except Exception:
            pass
        logger.info(f"agent_start: logging to [{log_path}]")
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        popen_kwargs = {
            "cwd": env.get("QALITA_HOME") or cfg.qalita_home,
            "stdout": log_file,
            "stderr": log_file,
            "env": env,
        }
        if os.name == "nt":
            try:
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                CREATE_NO_WINDOW = 0x08000000
                popen_kwargs["creationflags"] = (
                    DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
                )
                logger.info("agent_start: using Windows creation flags DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW")
            except Exception:
                pass
        else:
            popen_kwargs["start_new_session"] = True
            logger.info("agent_start: using POSIX start_new_session=True")
        proc = subprocess.Popen(cmd, **popen_kwargs)
        # Persist PID
        try:
            with open(_agent_pid_file_path(), "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
        except Exception:
            pass
        logger.info(f"agent_start: started process with PID [{proc.pid}]")
        # Quick health check: did the process exit immediately? If so, attach last log lines
        try:
            import time
            time.sleep(0.5)
            if proc.poll() is not None:
                tail = ""
                try:
                    with open(log_path, "r", encoding="utf-8") as lf:
                        lines = lf.readlines()
                        tail = "".join(lines[-50:])
                except Exception:
                    pass
                logger.error("agent_start: process exited immediately. Last log lines follow:")
                for l in tail.splitlines()[-10:]:
                    logger.error(f"agent_start: tail> {l}")
        except Exception:
            pass
        return jsonify({"ok": True, "pid": proc.pid, "login_ok": True})
    except Exception as exc:
        logger.error(f"agent_start: primary launch failed: {exc}")
        # Fallback: try invoking as python -m qalita.cli agent run -n <name>
        try:
            env = dict(os.environ)
            try:
                env["QALITA_HOME"] = cfg.qalita_home  # type: ignore[attr-defined]
            except Exception:
                env["QALITA_HOME"] = os.path.expanduser("~/.qalita")
            logger.info(f"agent_start(fallback): QALITA_HOME resolved to [{env.get('QALITA_HOME')}]")
            sel_path = _read_selected_env()
            if sel_path and os.path.isfile(sel_path):
                with open(sel_path, "r", encoding="utf-8") as ef:
                    for line in ef.readlines():
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v:
                            env[k] = v
            # Force worker mode in fallback too
            try:
                if not any(env.get(k) for k in ("QALITA_AGENT_MODE", "AGENT_MODE", "MODE")):
                    env["QALITA_AGENT_MODE"] = "worker"
            except Exception:
                env["QALITA_AGENT_MODE"] = "worker"
            logger.info(f"agent_start(fallback): effective agent mode is [{env.get('QALITA_AGENT_MODE') or env.get('AGENT_MODE') or env.get('MODE')}]")
            python_bin = sys.executable or "python3"
            cmd = [
                python_bin,
                "-m",
                "qalita",
                "agent",
                "-n",
                str(agent_name),
                "-m",
                "worker",
                "run",
            ]
            logger.info(f"agent_start(fallback): executing command: {' '.join(cmd)}")
            log_path = _agent_log_file_path()
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
            except Exception:
                pass
            logger.info(f"agent_start(fallback): logging to [{log_path}]")
            log_file = open(log_path, "a", encoding="utf-8", buffering=1)
            popen_kwargs = {
                "stdout": log_file,
                "stderr": log_file,
                "env": env,
            }
            if os.name == "nt":
                try:
                    DETACHED_PROCESS = 0x00000008
                    CREATE_NEW_PROCESS_GROUP = 0x00000200
                    CREATE_NO_WINDOW = 0x08000000
                    popen_kwargs["creationflags"] = (
                        DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
                    )
                    logger.info("agent_start(fallback): using Windows creation flags DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW")
                except Exception:
                    pass
            else:
                popen_kwargs["start_new_session"] = True
                logger.info("agent_start(fallback): using POSIX start_new_session=True")
            proc = subprocess.Popen(cmd, **popen_kwargs)
            with open(_agent_pid_file_path(), "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
            logger.info(f"agent_start(fallback): started process with PID [{proc.pid}]")
            return jsonify({"ok": True, "pid": proc.pid, "fallback": True, "login_ok": True})
        except Exception as exc2:
            logger.error(f"agent_start(fallback): launch failed: {exc2}")
            return (
                jsonify({"ok": False, "error": f"{exc}", "fallback_error": f"{exc2}"}),
                500,
            )


@bp.post("/agent/stop")
def agent_stop():
    pid = _read_agent_pid()
    if not pid:
        return jsonify({"ok": True, "already_stopped": True})
    if os.name == "nt":
        # On Windows, terminate the process tree started for the PID
        try:
            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(int(pid)),
                    "/T",
                    "/F",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    else:
        try:
            # Kill the whole process group started with start_new_session/setsid
            os.killpg(int(pid), signal.SIGTERM)
        except Exception:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except Exception:
                pass

    # Cleanup pid file
    try:
        p = _agent_pid_file_path()
        if os.path.exists(p):
            os.remove(p)
    except Exception:
        pass
    return jsonify({"ok": True})

    # Authenticate and persist agent config
    validated = validate_token(cfg.token)
    authenticate.__wrapped__(cfg, validated["user_id"])  # type: ignore[attr-defined]

    # Send alive and persist latest state
    try:
        agent_conf = cfg.load_agent_config()
        send_alive.__wrapped__(cfg, config_file=agent_conf)  # type: ignore[attr-defined]
    except Exception:
        pass


# ---- Open agent run folder in system file explorer ----


def _open_path_in_file_explorer(target_path: str) -> tuple[bool, str]:
    """Attempt to open target_path in the user's file explorer.

    Returns (ok, method_used).
    """
    try:
        # Normalize path
        target_path = os.path.normpath(target_path)
        # macOS
        if sys.platform == "darwin":
            if shutil.which("open"):
                subprocess.Popen(["open", target_path])
                return True, "open"
        # Windows (native)
        if os.name == "nt":
            if shutil.which("explorer"):
                subprocess.Popen(["explorer", target_path])
                return True, "explorer"
        # Linux / WSL
        # Prefer wslview if in WSL
        if os.environ.get("WSL_DISTRO_NAME"):
            # Try explorer.exe with Windows path translation first
            try:
                if shutil.which("wslpath") and shutil.which("explorer.exe"):
                    win_path = subprocess.check_output(["wslpath", "-w", target_path], text=True).strip()
                    subprocess.Popen(["explorer.exe", win_path])
                    return True, "explorer.exe(wslpath)"
            except Exception:
                pass
            if shutil.which("wslview"):
                subprocess.Popen(["wslview", target_path])
                return True, "wslview"
        # Fallbacks on Linux
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", target_path])
            return True, "xdg-open"
        # Last resort: try to open with "open" if present
        if shutil.which("open"):
            subprocess.Popen(["open", target_path])
            return True, "open"
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Failed opening explorer for [{target_path}]: {exc}")
        return False, "error"
    return False, "none"


@bp.get("/agent/run/<run_name>")
def open_agent_run(run_name: str):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    run_root = cfg.get_agent_run_path()
    # Security: ensure the resolved path stays within run_root
    candidate = os.path.normpath(os.path.join(run_root, run_name))
    if not candidate.startswith(os.path.normpath(run_root) + os.sep):
        return ("Invalid path", 400)
    if not os.path.isdir(candidate):
        return ("Run folder not found", 404)
    ok, method_used = _open_path_in_file_explorer(candidate)
    # Render a minimal HTML response so the new tab shows something useful
    status = "Opened" if ok else "Could not open automatically"
    return (
        f"""
<!doctype html><html><head><meta charset='utf-8'><title>Agent Run</title></head>
<body style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;padding:24px;'>
  <h2>{status} file explorer</h2>
  <p>Path: <code>{candidate}</code></p>
  <p>Method: <code>{method_used}</code></p>
  <p><a href='/'>Back to Dashboard</a></p>
  <hr/>
  <p>If the explorer did not open, you can navigate to this folder manually.</p>
  <ul>
    <li>macOS: open Finder and Go to Folder…</li>
    <li>Linux: use your file manager or run: <code>xdg-open {candidate}</code></li>
    <li>Windows/WSL: use Explorer at <code>\\\\wsl$\\{os.environ.get('WSL_DISTRO_NAME','<distro>')}\\{candidate}</code></li>
  </ul>
</body></html>
""",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )
