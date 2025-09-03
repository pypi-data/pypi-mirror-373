"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import sys
import subprocess
from flask import Blueprint, jsonify, current_app

from qalita.internal.utils import logger, validate_token
from qalita.internal.request import send_request
from .helpers import (
    agent_status_payload,
    read_selected_env,
    parse_env_file,
    agent_log_file_path,
    agent_pid_file_path,
    open_path_in_file_explorer,
    compute_agent_summary,
)


bp = Blueprint("agents", __name__)


@bp.get("/agent/status")
def agent_status():
    return jsonify(agent_status_payload())


@bp.post("/agent/start")
def agent_start():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_name = None

    st = agent_status_payload()
    if st.get("running"):
        return jsonify({"ok": True, "already_running": True, **st})

    try:
        sel_path = read_selected_env()
        if sel_path and os.path.isfile(sel_path):
            logger.info(f"agent_start: applying selected env at [{sel_path}]")
            _login_with_env(sel_path)
    except Exception as exc:
        logger.error(f"agent_start: failed applying selected env: {exc}")
        return jsonify({"ok": False, "error": f"Failed to apply selected context: {exc}"}), 400

    try:
        sel_path = read_selected_env()
        if sel_path and os.path.isfile(sel_path):
            data = parse_env_file(sel_path)
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

    # Ensure we have minimum credentials before preflight
    if not getattr(cfg, "token", None) or not getattr(cfg, "url", None):
        return jsonify({"ok": False, "error": "Missing TOKEN or URL. Select a context or login first."}), 400
    try:
        validated = validate_token(cfg.token)
        user_id = validated.get("user_id") if isinstance(validated, dict) else None
        if not user_id:
            return jsonify({"ok": False, "error": "Invalid or missing TOKEN in current context"}), 400
        try:
            r = send_request.__wrapped__(cfg, request=f"{cfg.url}/api/v1/version", mode="get")  # type: ignore[attr-defined]
        except Exception:
            r = None
        if r is None or getattr(r, "status_code", None) != 200:
            logger.error("Preflight failed: /api/v1/version not reachable or not 200")
            return jsonify({"ok": False, "error": "Backend unreachable or /api/v1/version not 200"}), 400
        try:
            r2 = send_request.__wrapped__(cfg, request=f"{cfg.url}/api/v2/users/{user_id}", mode="get")  # type: ignore[attr-defined]
        except Exception:
            r2 = None
        if r2 is None or getattr(r2, "status_code", None) != 200:
            logger.error("Preflight failed: /api/v2/users/{user_id} not 200 (invalid token?)")
            return jsonify({"ok": False, "error": "Token invalid or user not accessible"}), 400
    except Exception as exc:
        logger.error(f"Preflight login check failed: {exc}")
        return jsonify({"ok": False, "error": f"Preflight login check failed: {exc}"}), 400

    try:
        env = dict(os.environ)
        try:
            env["QALITA_HOME"] = cfg.qalita_home  # type: ignore[attr-defined]
        except Exception:
            env["QALITA_HOME"] = os.path.expanduser("~/.qalita")
        logger.info(f"agent_start: QALITA_HOME resolved to [{env.get('QALITA_HOME')}]")
        try:
            sel_path = read_selected_env()
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
        try:
            if not any(env.get(k) for k in ("QALITA_AGENT_MODE", "AGENT_MODE", "MODE")):
                env["QALITA_AGENT_MODE"] = "worker"
        except Exception:
            env["QALITA_AGENT_MODE"] = "worker"
        logger.info(f"agent_start: effective agent mode is [{env.get('QALITA_AGENT_MODE') or env.get('AGENT_MODE') or env.get('MODE')}]")
        if os.name == "nt":
            python_bin = sys.executable or "python"
            cmd = [python_bin, "-m", "qalita", "agent", "-n", str(agent_name), "-m", "worker", "run"]
            logger.info(f"agent_start: using python interpreter [{python_bin}]")
        else:
            cmd = ["qalita", "agent", "-n", str(agent_name), "-m", "worker", "run"]
        logger.info(f"agent_start: executing command: {' '.join(cmd)}")
        log_path = agent_log_file_path()
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        except Exception:
            pass
        logger.info(f"agent_start: logging to [{log_path}]")
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        popen_kwargs = {"stdout": log_file, "stderr": log_file, "env": env}
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
        try:
            with open(agent_pid_file_path(), "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
        except Exception:
            pass
        logger.info(f"agent_start: started process with PID [{proc.pid}]")
        return jsonify({"ok": True, "pid": proc.pid, "login_ok": True})
    except Exception as exc:
        logger.error(f"agent_start: primary launch failed: {exc}")
        try:
            env = dict(os.environ)
            try:
                env["QALITA_HOME"] = cfg.qalita_home  # type: ignore[attr-defined]
            except Exception:
                env["QALITA_HOME"] = os.path.expanduser("~/.qalita")
            logger.info(f"agent_start(fallback): QALITA_HOME resolved to [{env.get('QALITA_HOME')}]")
            sel_path = read_selected_env()
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
            try:
                if not any(env.get(k) for k in ("QALITA_AGENT_MODE", "AGENT_MODE", "MODE")):
                    env["QALITA_AGENT_MODE"] = "worker"
            except Exception:
                env["QALITA_AGENT_MODE"] = "worker"
            logger.info(f"agent_start(fallback): effective agent mode is [{env.get('QALITA_AGENT_MODE') or env.get('AGENT_MODE') or env.get('MODE')}]")
            python_bin = sys.executable or "python3"
            cmd = [python_bin, "-m", "qalita", "agent", "-n", str(agent_name), "-m", "worker", "run"]
            logger.info(f"agent_start(fallback): executing command: {' '.join(cmd)}")
            log_path = agent_log_file_path()
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
            except Exception:
                pass
            logger.info(f"agent_start(fallback): logging to [{log_path}]")
            log_file = open(log_path, "a", encoding="utf-8", buffering=1)
            popen_kwargs = {"stdout": log_file, "stderr": log_file, "env": env}
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
            with open(agent_pid_file_path(), "w", encoding="utf-8") as f:
                f.write(str(proc.pid))
            logger.info(f"agent_start(fallback): started process with PID [{proc.pid}]")
            return jsonify({"ok": True, "pid": proc.pid, "fallback": True, "login_ok": True})
        except Exception as exc2:
            logger.error(f"agent_start(fallback): launch failed: {exc2}")
            return (jsonify({"ok": False, "error": f"{exc}", "fallback_error": f"{exc2}"}), 500)


@bp.post("/agent/stop")
def agent_stop():
    pid = _read_agent_pid()
    if not pid:
        return jsonify({"ok": True, "already_stopped": True})
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(int(pid)), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass
    else:
        try:
            import signal
            os.killpg(int(pid), signal.SIGTERM)
        except Exception:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except Exception:
                pass
    try:
        p = agent_pid_file_path()
        if os.path.exists(p):
            os.remove(p)
    except Exception:
        pass
    return jsonify({"ok": True})


@bp.get("/agent/summary")
def agent_summary():
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    agent_conf, agent_runs = compute_agent_summary(cfg)
    return jsonify({"agent_conf": agent_conf or {}, "agent_runs": agent_runs})


@bp.get("/agent/run/<run_name>")
def open_agent_run(run_name: str):
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    run_root = cfg.get_agent_run_path()
    import os
    candidate = os.path.normpath(os.path.join(run_root, run_name))
    if not candidate.startswith(os.path.normpath(run_root) + os.sep):
        return ("Invalid path", 400)
    if not os.path.isdir(candidate):
        return ("Run folder not found", 404)
    ok, method_used = open_path_in_file_explorer(candidate)
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


def _read_agent_pid():
    try:
        with open(agent_pid_file_path(), "r", encoding="utf-8") as f:
            raw = f.read().strip()
            return int(raw) if raw else None
    except Exception:
        return None


def _login_with_env(env_path: str) -> None:
    cfg = current_app.config["QALITA_CONFIG_OBJ"]
    data = parse_env_file(env_path)

    def pick(*names: str, default: str | None = None) -> str | None:
        for n in names:
            if n in data and data[n]:
                return data[n]
        return default

    name = pick("QALITA_AGENT_NAME", "AGENT_NAME", "NAME") or getattr(cfg, "name", None) or "agent"
    mode = pick("QALITA_AGENT_MODE", "AGENT_MODE", "MODE") or getattr(cfg, "mode", None) or "job"
    token = pick("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN") or getattr(cfg, "token", None)
    url = pick("QALITA_AGENT_ENDPOINT", "QALITA_URL", "URL") or getattr(cfg, "url", None)

    if not token or not url:
        raise RuntimeError("Missing TOKEN or URL in context .env")

    cfg.name = name
    cfg.mode = mode
    cfg.token = token
    cfg.url = url


