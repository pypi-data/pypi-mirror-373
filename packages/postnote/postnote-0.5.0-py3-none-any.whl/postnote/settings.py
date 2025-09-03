from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RequestSettings:
    base_url: str = "http://localhost"
    api_version: str = "v1"
    api_port: Optional[int] = None
    resource_name: str = ""
    headers: Dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "application/json"}
    )
    file_headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    verify: bool = True
    return_response: bool = True

    def with_resource(self, resource_name: str) -> "RequestSettings":
        return RequestSettings(
            base_url=self.base_url,
            api_version=self.api_version,
            api_port=self.api_port,
            resource_name=resource_name,
            headers=self.headers,
            file_headers=self.file_headers,
            timeout=self.timeout,
            verify=self.verify,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RequestSettings":
        return cls(**data)


settings = RequestSettings()
