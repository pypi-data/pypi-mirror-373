import threading
from typing import Tuple, Optional, List
from .tsocket import TSocket
from .listener import IListener

from .handle.chart_handle import ChartHandle
from .handle.base_handle import BaseHandle
from .handle.trade_handle import TradeHandle
from .handle.market_handle import MarketHandle


class FinClient(object):
    __instance_lock = threading.Lock()

    def __init__(self):
        self.__TSocket: TSocket = TSocket()
        self.__ChartHandle: ChartHandle = ChartHandle(self.__TSocket)
        self.__BaseHandle: BaseHandle = BaseHandle(self.__TSocket)
        self.__MarketHandle: MarketHandle = MarketHandle(self.__TSocket)
        self.__TradeHandle: TradeHandle = TradeHandle(self.__TSocket)

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
                    cls._instance = FinClient()
        return cls._instance

    def set_callback(self, **kwargs):
        if kwargs is None:
            return

        valid_keys = {"on_tick", "on_ohlc", "on_order_update", "on_tradeorder_update", "on_select_rect"}
        for key in kwargs:
            if key not in valid_keys:
                raise ValueError(f"无效的回调参数: {key}，支持的参数为: {valid_keys}")

        for key in kwargs:
            if key == "on_tick":
                self.__MarketHandle.set_callback(on_tick=kwargs[key])
            elif key == "on_ohlc":
                self.__MarketHandle.set_callback(on_ohlc=kwargs[key])
            elif key == "on_order_update":
                self.__TradeHandle.set_callback(on_order_update=kwargs[key])
            elif key == "on_tradeorder_update":
                self.__TradeHandle.set_callback(on_tradeorder_update=kwargs[key])
            elif key == "on_select_rect":
                self.__ChartHandle.set_callback(on_select_rect=kwargs[key])

    def set_listener(self, listener: IListener):
        self.__MarketHandle.set_listener(listener)
        self.__TradeHandle.set_listener(listener)

    def base_handle(self) -> BaseHandle:
        return self.__BaseHandle

    def chart_handle(self) -> ChartHandle:
        return self.__ChartHandle

    def market_handle(self) -> MarketHandle:
        return self.__MarketHandle

    def trade_handle(self) -> TradeHandle:
        return self.__TradeHandle

    def connect(self, host: str = '', port: int = -1, timeout: int = 30000) -> Tuple[bool, str]:
        if self.__TSocket is None:
            return (False, '')

        return self.__TSocket.connect(host, port, timeout)

    def is_connected(self) -> bool:
        if self.__TSocket is None:
            return False

        return self.__TSocket.is_connected()

    def close(self):
        if self.__TSocket is None:
            return

        self.__TSocket.close()
