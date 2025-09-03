"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import re
import sys
import shutil
import subprocess
from datetime import datetime, timezone
from flask import current_app

from qalita.internal.utils import logger
from qalita.internal.request import send_request


def qalita_home() -> str:
    try:
        cfg = current_app.config.get("QALITA_CONFIG_OBJ")
        return os.path.normpath(cfg.qalita_home)  # type: ignore[attr-defined]
    except Exception:
        return os.path.normpath(os.path.expanduser("~/.qalita"))


def selected_env_file_path() -> str:
    return os.path.normpath(os.path.join(qalita_home(), ".current_env"))


def parse_env_file(env_path: str) -> dict:
    vars: dict[str, str] = {}
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip().lstrip("\ufeff")
                v = v.strip().strip('"').strip("'")
                vars[k] = v
    except Exception:
        logger.error(f"Failed reading env file: [{env_path}]")
        pass
    return vars


def materialize_env_from_process_env(target_path: str) -> None:
    try:
        existing: dict[str, str] = {}
        if os.path.isfile(target_path):
            existing = parse_env_file(target_path) or {}
        env = os.environ
        key_groups = [
            ("QALITA_AGENT_NAME", ["QALITA_AGENT_NAME", "AGENT_NAME", "NAME"]),
            ("QALITA_AGENT_MODE", ["QALITA_AGENT_MODE", "AGENT_MODE", "MODE"]),
            ("QALITA_AGENT_TOKEN", ["QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN"]),
            (
                "QALITA_AGENT_ENDPOINT",
                ["QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"],
            ),
        ]
        updates: dict[str, str] = {}
        for _, aliases in key_groups:
            value = None
            for k in aliases:
                if k in env and env.get(k):
                    value = env.get(k)
                    updates[k] = value  # type: ignore[assignment]
                    break
        merged = dict(existing)
        merged.update(updates)
        lines = []
        for k in sorted(merged.keys()):
            v = merged[k]
            if v is None:
                continue
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
        pass


def ensure_default_env_selected(pointer_path: str):
    try:
        base = qalita_home()
        env = os.environ
        cfg = current_app.config.get("QALITA_CONFIG_OBJ")
        name = env.get("QALITA_AGENT_NAME") or env.get("AGENT_NAME") or env.get("NAME")
        if not name:
            try:
                name = getattr(cfg, "name", None)
            except Exception:
                name = None
        if not name:
            name = "agent"
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name)).strip("-_.") or "agent"
        target = os.path.normpath(os.path.join(base, f".env-{safe}"))
        os.makedirs(base, exist_ok=True)
        materialize_env_from_process_env(target)
        try:
            with open(pointer_path, "w", encoding="utf-8") as pf:
                pf.write(target)
        except Exception:
            pass
        return target
    except Exception:
        return None


def read_selected_env():
    p = selected_env_file_path()
    try:
        with open(p, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            path = os.path.normpath(raw) if raw else None
            if path and os.path.isfile(path):
                try:
                    materialize_env_from_process_env(path)
                except Exception:
                    pass
                return path
            try:
                base = qalita_home()
                if path:
                    candidate = os.path.normpath(os.path.join(base, os.path.basename(path)))
                    if os.path.isfile(candidate):
                        logger.warning(
                            f"Selected env pointer [{path}] not found. Using [{candidate}] under current QALITA_HOME."
                        )
                        try:
                            materialize_env_from_process_env(candidate)
                        except Exception:
                            pass
                        try:
                            with open(p, "w", encoding="utf-8") as pf:
                                pf.write(candidate)
                        except Exception:
                            pass
                        return candidate
                    try:
                        os.makedirs(base, exist_ok=True)
                        materialize_env_from_process_env(candidate)
                        logger.warning(
                            f"Selected env pointer [{path}] not found. Created [{candidate}] under current QALITA_HOME from environment."
                        )
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
            return ensure_default_env_selected(p)
    except Exception:
        logger.warning(f"No selected env pointer found at [{p}] or failed to read it")
        return ensure_default_env_selected(p)


def list_env_files():
    root = qalita_home()
    files = []
    try:
        for name in os.listdir(root):
            lower = name.lower()
            if lower.startswith(".env") or lower.endswith(".env"):
                files.append({"name": name, "path": os.path.normpath(os.path.join(root, name))})
    except Exception:
        files = []
    files.sort(key=lambda x: x["name"])  # stable order
    return files


def agent_pid_file_path():
    return os.path.join(qalita_home(), "agent_run.pid")


def read_agent_pid():
    p = agent_pid_file_path()
    try:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                return int(raw) if raw else None
    except Exception:
        return None
    return None


def agent_log_file_path():
    return os.path.join(qalita_home(), "agent_run.log")


def is_pid_running(pid: int) -> bool:
    try:
        if os.name == "nt":
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {int(pid)}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    return False
                return str(int(pid)) in result.stdout
            except Exception:
                return False
        else:
            os.kill(int(pid), 0)
            return True
    except Exception:
        return False


def agent_status_payload() -> dict:
    pid = read_agent_pid()
    running = bool(pid) and is_pid_running(int(pid))
    return {"running": running, "pid": int(pid) if running else None}


def open_path_in_file_explorer(target_path: str) -> tuple[bool, str]:
    try:
        target_path = os.path.normpath(target_path)
        if sys.platform == "darwin":
            if shutil.which("open"):
                subprocess.Popen(["open", target_path])
                return True, "open"
        if os.name == "nt":
            if shutil.which("explorer"):
                subprocess.Popen(["explorer", target_path])
                return True, "explorer"
        if os.environ.get("WSL_DISTRO_NAME"):
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
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", target_path])
            return True, "xdg-open"
        if shutil.which("open"):
            subprocess.Popen(["open", target_path])
            return True, "open"
    except Exception as exc:
        logger.warning(f"Failed opening explorer for [{target_path}]: {exc}")
        return False, "error"
    return False, "none"


def compute_agent_summary(cfg):
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
                "agent_id": pick(raw, "context", "remote", "id") or raw.get("agent_id", ""),
            }
        else:
            agent_conf = None
    except SystemExit:
        # Gracefully handle missing/invalid .agent in web requests
        agent_conf = None
    except Exception:
        agent_conf = None
    # Overlay with selected context values
    try:
        env_path = read_selected_env()
        if env_path:
            data = parse_env_file(env_path)
            if agent_conf is None:
                agent_conf = {}
            agent_conf["name"] = data.get("QALITA_AGENT_NAME") or data.get("AGENT_NAME") or data.get("NAME") or agent_conf.get("name", "")
            agent_conf["mode"] = data.get("QALITA_AGENT_MODE") or data.get("AGENT_MODE") or data.get("MODE") or agent_conf.get("mode", "")
            agent_conf["url"] = data.get("QALITA_AGENT_ENDPOINT") or data.get("QALITA_URL") or data.get("URL") or agent_conf.get("url", "")
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
                if pattern.match(entry) and os.path.isdir(os.path.join(run_root, entry)):
                    ts = entry.split("_")[0]
                    try:
                        when = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        when = ts
                    agent_runs.append({"name": entry, "path": os.path.join(run_root, entry), "timestamp": ts, "when": when})
    except Exception:
        agent_runs = []
    return agent_conf, agent_runs


