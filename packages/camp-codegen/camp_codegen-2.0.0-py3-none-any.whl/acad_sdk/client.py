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
        default_network: Optional[str] = None,
        default_owner: Optional[str] = None,
    ):
        # Fixed production default unless ACAD_BASE_URL is explicitly provided
        self.base_url = base_url or os.getenv("ACAD_BASE_URL", "https://acadcodegen-production.up.railway.app")
        self.api_key = api_key or os.getenv("ACAD_API_KEY")
        self.auth_header_name = auth_header_name or os.getenv("ACAD_AUTH_HEADER", "X-API-Key")
        self.session = session or requests.Session()
        self.timeout = timeout
        # Smarter defaults
        self.default_network = default_network or os.getenv("ACAD_DEFAULT_NETWORK", "basecamp")
        self.default_owner = default_owner or os.getenv(
            "ACAD_DEFAULT_OWNER",
            "0xa58DCCb0F17279abD1d0D9069Aa8711Df4a4c58E",
        )

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

    def start_pipeline_auto(
        self,
        prompt: str,
        *,
        max_iters: Optional[int] = None,
        filename: Optional[str] = None,
        constructor_args: Optional[List[Any]] = None,
    ) -> str:
        """
        Convenience wrapper that auto-fills network and sensible defaults.

        Defaults:
          - network: self.default_network ("basecamp")
          - max_iters: ACAD_MAX_ITERS env or 5
          - filename: ACAD_DEFAULT_FILENAME env or "AIGenerated.sol"
        """
        if max_iters is None:
            try:
                max_iters = int(os.getenv("ACAD_MAX_ITERS", "5"))
            except ValueError:
                max_iters = 5
        filename = filename or os.getenv("ACAD_DEFAULT_FILENAME", "AIGenerated.sol")
        return self.start_pipeline(
            prompt=prompt,
            network=self.default_network,
            max_iters=max_iters,
            filename=filename,
            constructor_args=constructor_args,
        )

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
    def deploy_erc20(self, name: str, symbol: str, initial_supply: str, network: Optional[str], owner: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": name,
            "symbol": symbol,
            "initialSupply": initial_supply,
            "network": network or self.default_network,
        }
        if owner or self.default_owner:
            body["owner"] = owner or self.default_owner
        data = self._request("POST", "/api/deploy/erc20", json=body)
        return data.get("result", data)

    # --------------- Utilities ---------------
    def summarize_failure(self, job: Dict[str, Any]) -> str:
        """
        Produce a short, actionable summary for a failed job, based on logs/errors.
        """
        state = (job or {}).get("state")
        if state not in ("failed", "canceled"):
            return ""

        logs: List[Dict[str, Any]] = (job or {}).get("logs", []) or (job or {}).get("data", {}).get("logs", []) or []
        text = "\n".join([str(e.get("msg", "")) for e in logs])
        err_msg = ""
        if isinstance(job.get("error"), dict):
            err_msg = str(job["error"].get("message", ""))
        elif job.get("error"):
            err_msg = str(job.get("error"))

        blob = f"{text}\n{err_msg}".lower()

        hints: List[str] = []
        # Hardhat/solc issues
        if "hardhat" in blob or "hh506" in blob or "solcjs" in blob:
            hints.append("Hardhat/solc error detected. If you control the environment, use a Hardhat-supported Node version (per https://hardhat.org/nodejs-versions) and ensure solc is available.")
        if "node.js v" in blob or "not supported by hardhat" in blob:
            hints.append("Node version not supported by Hardhat. Prefer LTS versions supported by Hardhat (e.g., Node 18 LTS/20 depending on Hardhat release).")

        # General guidance for AI prompt complexity
        hints.append("Try a simpler prompt and smaller contract first (e.g., basic ERC20/721), then iterate with additional features.")

        # Contract compile tips
        hints.append("If errors mention specific lines, ask the AI to fix those compile errors or provide a minimal example that compiles.")

        return "\n".join(hints)

    # --------------- AI Helpers ---------------
    def ai_generate(self, prompt: str) -> Dict[str, Any]:
        return self._request("POST", "/api/ai/generate", json={"prompt": prompt})

    def ai_fix(self, code: str, errors: str) -> Dict[str, Any]:
        return self._request("POST", "/api/ai/fix", json={"code": code, "errors": errors})

    def ai_compile(self, filename: str, code: str) -> Dict[str, Any]:
        return self._request("POST", "/api/ai/compile", json={"filename": filename, "code": code})
