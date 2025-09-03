from requests import Session
from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumenteClientMixin(object):
    api_url: str
    api_key: str
    tenant: Optional[str] = None
    session: Optional[Session] = None

    def __post_init__(self):
        if self.session is None:
            self.session = Session()
        self.session.headers.update(self.get_common_headers())


    def get_common_headers(self) -> dict:
        common_headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        if self.tenant:
            common_headers.update({"X-Tenant": self.tenant})
        return common_headers
        