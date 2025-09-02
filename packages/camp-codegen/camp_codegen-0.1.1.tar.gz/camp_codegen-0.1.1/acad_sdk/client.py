import os
import time
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

import requests


class AcadError(Exception):
    def __init__(self, message: str, status: Optional[int] = None, code: Optional[str] = None, details: Any = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details


class AcadClient:
    """
    Minimal Python SDK for the AI Deployment API.

    Base URLs:
      - Production: https://acadcodegen-production.up.railway.app
      - Local: http://localhost:3000

    Auth: default header 'X-API-Key: <key>' (configurable via auth_header_name)
    Env fallbacks: ACAD_BASE_URL, ACAD_API_KEY, ACAD_AUTH_HEADER
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        auth_header_name: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: int = 60,
    ):
        self.base_url = base_url or os.getenv("ACAD_BASE_URL", "https://acadcodegen-production.up.railway.app")
        self.api_key = api_key or os.getenv("ACAD_API_KEY")
        self.auth_header_name = auth_header_name or os.getenv("ACAD_AUTH_HEADER", "X-API-Key")
        self.session = session or requests.Session()
        self.timeout = timeout

    # --------------- internal HTTP helpers ---------------
    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h[self.auth_header_name] = self.api_key
        if extra:
            h.update(extra)
        return h

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url.rstrip('/')}{path}"

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = self._url(path)
        try:
            resp = self.session.request(method, url, timeout=self.timeout, headers=self._headers(kwargs.pop("headers", None)), **kwargs)
        except requests.RequestException as e:
            raise AcadError(f"Network error: {e}")

        # try JSON parse
        data: Any = None
        try:
            data = resp.json()
        except ValueError:
            data = None

        if not resp.ok or (isinstance(data, dict) and data.get("ok") is False):
            msg = (data or {}).get("error", {}).get("message") if isinstance(data, dict) else resp.text
            raise AcadError(msg or resp.reason, status=resp.status_code, code=(data or {}).get("error", {}).get("code") if isinstance(data, dict) else None, details=data or resp.text)

        return data

    # --------------- AI Pipeline ---------------
    def start_pipeline(self, prompt: str, network: str, max_iters: Optional[int] = None, filename: Optional[str] = None, constructor_args: Optional[List[Any]] = None) -> str:
        body: Dict[str, Any] = {
            "prompt": prompt,
            "network": network,
        }
        if max_iters is not None:
            body["maxIters"] = max_iters
        if filename is not None:
            body["filename"] = filename
        if constructor_args is not None:
            body["constructorArgs"] = constructor_args

        data = self._request("POST", "/api/ai/pipeline", json=body)
        job = (data or {}).get("job", {})
        job_id = job.get("id")
        if not job_id:
            raise AcadError("Missing job id in response", details=data)
        return job_id

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        data = self._request("GET", f"/api/job/{job_id}/status")
        # some snippets show payload with `data: {...}`
        return data.get("data", data)

    def get_job_logs(self, job_id: str, since: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        data = self._request("GET", f"/api/job/{job_id}/logs", params={"since": since})
        payload = data.get("data", data)
        logs: List[Dict[str, Any]] = payload.get("logs", [])
        # naive cursor: nextSince = since + len(logs)
        next_since = since + len(logs)
        return logs, next_since

    def wait_for_completion(
        self,
        job_id: str,
        interval_sec: float = 2.0,
        timeout_sec: int = 900,
        on_update: Optional[Any] = None,
        stream_logs: bool = False,
    ) -> Dict[str, Any]:
        start = time.time()
        cursor = 0
        last_state = None
        while True:
            job = self.get_job_status(job_id)
            state = job.get("state")
            if on_update and (state != last_state):
                try:
                    on_update(job)
                except Exception:
                    pass
            last_state = state

            if stream_logs:
                try:
                    logs, cursor = self.get_job_logs(job_id, since=cursor)
                    for entry in logs:
                        lvl = entry.get("level", "info").upper()
                        msg = entry.get("msg", "")
                        print(f"[{lvl}] {msg}")
                except AcadError:
                    # ignore log fetch transient errors
                    pass

            if state in ("completed", "failed", "canceled"):
                return job

            if time.time() - start > timeout_sec:
                raise AcadError("Timeout waiting for job to complete", code="TIMEOUT", details=job)

            time.sleep(interval_sec)

    # --------------- Artifacts ---------------
    def get_artifacts(self, job_id: str, include: str = "all") -> Dict[str, Any]:
        data = self._request("GET", "/api/artifacts", params={"include": include, "jobId": job_id})
        return data

    def get_sources(self, job_id: str) -> List[Dict[str, Any]]:
        data = self._request("GET", "/api/artifacts/sources", params={"jobId": job_id})
        return data.get("data", data)

    def get_abis(self, job_id: str) -> List[Dict[str, Any]]:
        data = self._request("GET", "/api/artifacts/abis", params={"jobId": job_id})
        return data.get("data", data)

    def get_scripts(self, job_id: str) -> List[Dict[str, Any]]:
        data = self._request("GET", "/api/artifacts/scripts", params={"jobId": job_id})
        return data.get("data", data)

    # --------------- ERC20 ---------------
    def deploy_erc20(self, name: str, symbol: str, initial_supply: str, network: str, owner: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": name,
            "symbol": symbol,
            "initialSupply": initial_supply,
            "network": network,
        }
        if owner:
            body["owner"] = owner
        data = self._request("POST", "/api/deploy/erc20", json=body)
        return data.get("result", data)

    # --------------- AI Helpers ---------------
    def ai_generate(self, prompt: str) -> Dict[str, Any]:
        return self._request("POST", "/api/ai/generate", json={"prompt": prompt})

    def ai_fix(self, code: str, errors: str) -> Dict[str, Any]:
        return self._request("POST", "/api/ai/fix", json={"code": code, "errors": errors})

    def ai_compile(self, filename: str, code: str) -> Dict[str, Any]:
        return self._request("POST", "/api/ai/compile", json={"filename": filename, "code": code})
