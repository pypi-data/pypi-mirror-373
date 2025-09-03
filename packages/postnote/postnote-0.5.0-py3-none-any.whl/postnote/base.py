from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode
import requests

from .settings import RequestSettings

JSONType = Union[Dict[str, Any], List[Any]]


@dataclass
class BaseRequest:
    settings: RequestSettings
    _session: requests.Session = field(init=False, repr=False)

    def __post_init__(self):
        self._session = requests.Session()
        if self.settings.headers:
            self._session.headers.update(self.settings.headers)

    def request(
        self,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self.build_url(id=id, endpoint=endpoint, params=params)
        hdrs = dict(self._session.headers)
        if headers:
            hdrs.update(headers)

        if files is not None:
            effective_headers = {
                k: v for k, v in hdrs.items() if k.lower() != "content-type"
            }
            resp = self._session.request(
                method=method.upper(),
                url=url,
                headers=effective_headers,
                data=payload,
                files=files,
                timeout=timeout or self.settings.timeout,
                verify=self.settings.verify,
            )
        else:
            resp = self._session.request(
                method=method.upper(),
                url=url,
                headers=hdrs,
                json=payload,
                timeout=timeout or self.settings.timeout,
                verify=self.settings.verify,
            )
        return resp

    def get(
        self,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "GET",
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def post(
        self,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        local_headers = self.settings.file_headers if files else None
        if headers and local_headers:
            local_headers = {**local_headers, **headers}
        elif headers:
            local_headers = headers
        return self.request(
            "POST",
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            files=files,
            headers=local_headers,
            timeout=timeout,
        )

    def put(
        self,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "PUT",
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def patch(
        self,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "PATCH",
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def delete(
        self,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ):
        return self.request(
            "DELETE",
            id=id,
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def set_bearer(self, token: str):
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        return self

    def set_basic(self, username: str, password: str):
        self._session.auth = (username, password)
        return self

    def _join(self, *parts: str) -> str:
        return "/".join(
            str(p).strip("/") for p in parts if p is not None and str(p) != ""
        )

    def _base(self) -> str:
        if (
            self.settings.api_port is not None
            and ":" not in self.settings.base_url.split("//")[-1]
        ):
            return f"{self.settings.base_url}:{self.settings.api_port}"
        return self.settings.base_url

    def build_url(
        self,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        path = self._join(
            self.settings.api_version,
            self.settings.resource_name,
            str(id) if id is not None else None,
            endpoint,
        )
        url = f"{self._base()}/{path}"
        if params:
            url += f"?{urlencode(params, doseq=True)}"
        return url

    def build_curl(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple]] = None,
    ) -> str:
        hdrs = dict(self.settings.headers)
        if headers:
            hdrs.update(headers)
        parts = [f"curl -X {method.upper()} '{url}'"]
        for k, v in hdrs.items():
            parts.append(f"-H '{k}: {v}'")
        if files:
            for f in files:
                if len(f) == 2:
                    k, fp = f
                    parts.append(f"-F '{k}=@{getattr(fp, 'name', 'file')}'")
                else:
                    k, fp, meta = f
                    ctype = meta.get("Content-Type", "application/octet-stream")
                    parts.append(
                        f"-F '{k}=@{getattr(fp, 'name', 'file')};type={ctype}'"
                    )
        elif payload is not None:
            parts.append(f"-d '{payload}'")
        return " ".join(parts)
