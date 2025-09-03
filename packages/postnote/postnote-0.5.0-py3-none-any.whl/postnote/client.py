from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import requests

from .base import BaseRequest
from .display import NotebookDisplay
from .settings import RequestSettings, settings as settings_default


@dataclass
class Request(BaseRequest):
    show_curl: bool = True
    verbose: bool = True

    def __init__(
        self,
        settings: RequestSettings = None,
        show_curl: bool = True,
        verbose: bool = True,
    ):
        if settings is None:
            settings = settings_default

        object.__setattr__(self, "settings", settings)
        object.__setattr__(self, "show_curl", show_curl)
        object.__setattr__(self, "verbose", verbose)
        self.__post_init__()

    def _displayer(self) -> NotebookDisplay:
        return NotebookDisplay(show_curl=self.show_curl, verbose=self.verbose)

    def request(
        self,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        id: Union[str, int, None] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[List[Tuple]] = None,
        headers: Optional[Dict[str, str]] = None,
        key: Optional[str] = None,
        to_polars: bool = False,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = self.build_url(id=id, endpoint=endpoint, params=params)
        disp = self._displayer()
        # disp.show_url(url)
        curl = self.build_curl(
            method,
            url,
            headers=headers,
            payload=payload if files is None else None,
            files=files,
        )
        if self.show_curl:
            disp.show_curl(curl)
        resp = super().request(
            method=method,
            payload=payload,
            id=id,
            endpoint=endpoint,
            params=params,
            files=files,
            headers=headers,
            timeout=timeout,
        )
        disp.show_response(resp, key=key, to_polars=to_polars)

        if self.settings.return_response:
            return resp
