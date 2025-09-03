import os
import time
import sys
import requests
from qalita.__main__ import pass_config
from qalita.internal.utils import logger


@pass_config
def send_api_request(
    config,
    request,
    mode,
    timeout=10,
    total_retry=3,
    current_retry=0,
    grace_period=10,
    query_params={},
    data=None,
):
    # If a context selection exists, we can load variables from that .env file to override URL/token
    # Selected env is stored by the UI in ~/.qalita/.current_env as an absolute path
    agent_conf = config.load_agent_config()
    base_url = agent_conf['context']['local']['url']
    # Try override from selected .env
    try:
        env_path_file = os.path.join(getattr(config, "qalita_home", os.path.expanduser("~/.qalita")), ".current_env")
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
                            if k in ("QALITA_URL", "URL"):
                                base_url = v
                                break
    except Exception:
        pass
    url = f"{base_url}{request}"
    # Ensure we pass the Config explicitly to avoid requiring a Click context
    try:
        return send_request.__wrapped__(
            config,
            url,
            mode,
            timeout,
            total_retry,
            current_retry,
            grace_period,
            query_params,
            data=data,
        )  # type: ignore[attr-defined]
    except Exception:
        return send_request(
            url,
            mode,
            timeout,
            total_retry,
            current_retry,
            grace_period,
            query_params,
            data=data,
        )


@pass_config
def send_request(
    config,
    request,
    mode,
    timeout=300,
    total_retry=3,
    current_retry=0,
    grace_period=10,
    query_params={},
    data=None,
    file_path=None,
):
    """Send a request to the backend, manages retries and timeout"""
    if current_retry == total_retry:
        logger.error(
            f"Agent can't communicate with backend after {total_retry} retries"
        )
        sys.exit(1)

    # Build headers using explicit Config instance (not Click context)
    token = None
    if getattr(config, "token", None):
        token = config.token
    else:
        try:
            # If a .current_env is set, use its values to override
            env_path = None
            try:
                env_path = os.path.join(getattr(config, "qalita_home", os.path.expanduser("~/.qalita")), ".current_env")
                if os.path.isfile(env_path):
                    with open(env_path, 'r', encoding='utf-8') as f:
                        selected_env_path = f.read().strip()
                        if selected_env_path and os.path.isfile(selected_env_path):
                            # simple .env parser: KEY=VALUE per line
                            with open(selected_env_path, 'r', encoding='utf-8') as ef:
                                for line in ef.readlines():
                                    line = line.strip()
                                    if not line or line.startswith('#') or '=' not in line:
                                        continue
                                    k, v = line.split('=', 1)
                                    k = k.strip(); v = v.strip().strip('"').strip("'")
                                    if k.upper() in ("QALITA_TOKEN", "TOKEN") and not token:
                                        token = v
            except Exception:
                pass
            if not token:
                agent_conf = config.load_agent_config()
                token = agent_conf.get("context", {}).get("local", {}).get("token")
        except Exception:
            token = None
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    verify_ssl = not os.getenv("SKIP_SSL_VERIFY", False)

    try:
        if mode == "post":
            r = requests.post(
                request,
                headers=headers,
                timeout=timeout,
                params=query_params,
                json=data,
                verify=verify_ssl,
            )
        elif mode == "post-multipart":
            with open(file_path, "rb") as f:
                r = requests.post(
                    request,
                    headers=headers,
                    files={"file": f},
                    timeout=timeout,
                    params=query_params,
                    json=data,
                    verify=verify_ssl,
                )
        elif mode == "get":
            r = requests.get(
                request,
                headers=headers,
                timeout=timeout,
                params=query_params,
                verify=verify_ssl,
            )
        elif mode == "put":
            r = requests.put(
                request,
                headers=headers,
                timeout=timeout,
                params=query_params,
                json=data,
                verify=verify_ssl,
            )
        return r
    except Exception as exception:
        logger.warning(f"Agent can't communicate with backend : {exception}")
        logger.info(
            f"Retrying {current_retry+1}/{total_retry} in {grace_period} seconds..."
        )
        time.sleep(grace_period)
        r = send_request(
            config,
            request,
            mode,
            timeout,
            total_retry,
            current_retry + 1,
            grace_period,
            query_params,
            data,
            file_path,
        )
        logger.success(f"Backend communication restored")
        return r
