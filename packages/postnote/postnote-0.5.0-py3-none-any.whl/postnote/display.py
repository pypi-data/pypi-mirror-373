from typing import Any, Dict, List, Optional, Tuple, Union
import json

try:
    from IPython.display import display, Markdown
except Exception:

    def display(x):
        print(x)

    def Markdown(x):
        return x


try:
    import polars as pl
except Exception:
    pl = None

import requests

JSONType = Union[Dict[str, Any], List[Any]]


class NotebookDisplay:
    def __init__(self, show_curl: bool = True, verbose: bool = True):
        self._show_curl = show_curl
        self.verbose = verbose

    def show_url(self, url: str):
        if self.verbose:
            display(f"URL: {url}")

    def show_curl(self, curl: str):
        if self._show_curl:
            display(curl)

    def show_response(
        self,
        response: requests.Response,
        key: Optional[str] = None,
        to_polars: bool = False,
    ):
        status = response.status_code
        if self.verbose:
            display(Markdown(f"**[ Response - {status} ]**"))

        try:
            content = response.json()
        except ValueError:
            if self.verbose:
                display(Markdown(f"**[ Response - {status} ]** - *non-JSON body*:"))
            display(response.text)
            return

        if to_polars and pl is not None:
            data = content
            if isinstance(content, dict):
                if not response.ok:
                    data = content.get("errors", content)
                elif key is not None:
                    data = content.get(key, content)
            try:
                if isinstance(data, list):
                    df = pl.DataFrame(data)
                    display(df)
                    return
            except Exception:
                pass

        display(content)
