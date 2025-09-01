import threading
from .tsocket import TSocket
from typing import Tuple, Optional

from .handle.findata_handle import FinDataHandle
from .handle.base_handle import BaseHandle


class FinDataClient(object):
    __instance_lock = threading.Lock()

    def __init__(self):
        self.__TSocket: TSocket = TSocket()
        self.__FinDataHandle: FinDataHandle = FinDataHandle(self.__TSocket)
        self.__BaseHandle: BaseHandle = BaseHandle(self.__TSocket)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            with cls.__instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = FinDataClient()
        return cls._instance

    def base_handle(self) -> BaseHandle:
        return self.__BaseHandle

    def findata_handle(self) -> FinDataHandle:
        return self.__FinDataHandle

    def connect(self, host: str = '', port: int = -1, timeout: int = 60000) -> Tuple[bool, str]:
        return self.__TSocket.connect(host, port, timeout)

    def is_connected(self):
        return self.__TSocket.is_connected()

    def close(self):
        self.__TSocket.close()
