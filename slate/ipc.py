from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class IPCMessage:
    type: str
    payload: dict[str, Any]
    sender: str = "slate-core"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def create_webview_ipc(tab_id: str, url: str, ad_blocked: bool) -> IPCMessage:
    return IPCMessage(
        type="BROWSER_WEBVIEW_LOAD",
        payload={
            "tab_id": tab_id,
            "url": url,
            "config": {
                "sandbox": True,
                "ad_blocked": ad_blocked,
            },
        },
    )
