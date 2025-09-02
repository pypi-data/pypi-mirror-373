from abc import abstractmethod
from .data.market.tick_data import TickData
from .data.market.ohlc_data import OHLCData
from .data.trade.order_data import OrderData
from .data.trade.tradeorder_data import TradeOrderData


class IListener(object):

    @abstractmethod
    def on_connect(self):
        pass

    @abstractmethod
    def on_disconnect(self):
        pass

    @abstractmethod
    def on_tick(self, tick: TickData):
        pass

    @abstractmethod
    def on_ohlc(self, ohlc: OHLCData):
        pass

    @abstractmethod
    def on_order_update(self, order: OrderData):
        pass

    @abstractmethod
    def on_tradeorder_update(self, tradeorder: TradeOrderData):
        pass
    
