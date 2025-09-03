from abc import ABC
from typing import Optional

import aiohttp


class HuibiaoAbstractClient(ABC):
    def __init__(
        self, client_name: str, *, session: Optional[aiohttp.ClientSession] = None
    ):
        self.__session = session
        self.__name = client_name
        assert self.__session is not None, "会话不能为空"

    @property
    def session(self):
        return self.__session

    @property
    def client_name(self) -> Optional[str]:
        return self.__name

    def session_tag(self, session_id: str) -> str:
        session_id_suffix = f"[{session_id}]" if session_id else ""
        return f"[{self.client_name}]{session_id_suffix}"
