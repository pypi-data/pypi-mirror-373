from ...interface import IData
from ...packer.trade.tradeorder_data_packer import TradeOrderDataPacker


class TradeOrderData(IData):
    def __init__(self, exchange_id: str = '', product_id: str = '', instrument_id: str = '', trade_time: str = '',
                 trading_day: str = '', trade_date: str = '', broker_order_seq: str = '', order_id: str = '',
                 trade_id: str = '', price: float = 0.0, volume: int = 0, unclose_volume: int = 0, direction: int = 1,
                 open_close_type: int = 0, hedge_type: int = 0, is_yesterday_trade: bool = False,
                 close_profit: float = 0.0, curr_margin: float = 0.0, commission: float = 0.0, trade_type: int = 0,
                 rtn_tradeorder_local_time: int = 0):
        super().__init__(TradeOrderDataPacker(self))
        self._ExchangeID: str = exchange_id
        self._ProductID: str = product_id
        self._InstrumentID: str = instrument_id
        self._TradeTime: str = trade_time
        self._TradingDay: str = trading_day
        self._TradeDate: str = trade_date
        self._BrokerOrderSeq: str = broker_order_seq
        self._OrderID: str = order_id
        self._TradeID: str = trade_id
        self._Price: float = price
        self._Volume: int = volume
        self._UnCloseVolume: int = unclose_volume
        self._Direction: int = direction
        self._OpenCloseType: int = open_close_type
        self._HedgeType: int = hedge_type
        self._IsYesterdayTrade: bool = is_yesterday_trade
        self._CloseProfit: float = close_profit
        self._CurrMargin: float = curr_margin
        self._Commission: float = commission
        self._TradeType: int = trade_type
        self._RtnTradeOrderLocalTime: int = rtn_tradeorder_local_time

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def ProductID(self):
        return self._ProductID

    @ProductID.setter
    def ProductID(self, value: str):
        self._ProductID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def TradeTime(self):
        return self._TradeTime

    @TradeTime.setter
    def TradeTime(self, value: str):
        self._TradeTime = value

    @property
    def TradingDay(self):
        return self._TradingDay

    @TradingDay.setter
    def TradingDay(self, value: str):
        self._TradingDay = value

    @property
    def TradeDate(self):
        return self._TradeDate

    @TradeDate.setter
    def TradeDate(self, value: str):
        self._TradeDate = value

    @property
    def BrokerOrderSeq(self):
        return self._BrokerOrderSeq

    @BrokerOrderSeq.setter
    def BrokerOrderSeq(self, value: str):
        self._BrokerOrderSeq = value

    @property
    def OrderID(self):
        return self._OrderID

    @OrderID.setter
    def OrderID(self, value: str):
        self._OrderID = value

    @property
    def TradeID(self):
        return self._TradeID

    @TradeID.setter
    def TradeID(self, value: str):
        self._TradeID = value

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, value: float):
        self._Price = value

    @property
    def Volume(self):
        return self._Volume

    @Volume.setter
    def Volume(self, value: int):
        self._Volume = value

    @property
    def UnCloseVolume(self):
        return self._UnCloseVolume

    @UnCloseVolume.setter
    def UnCloseVolume(self, value: int):
        self._UnCloseVolume = value

    @property
    def Direction(self):
        return self._Direction

    @Direction.setter
    def Direction(self, value: int):
        self._Direction = value

    @property
    def OpenCloseType(self):
        return self._OpenCloseType

    @OpenCloseType.setter
    def OpenCloseType(self, value: int):
        self._OpenCloseType = value

    @property
    def HedgeType(self):
        return self._HedgeType

    @HedgeType.setter
    def HedgeType(self, value: int):
        self._HedgeType = value

    @property
    def IsYesterdayTrade(self):
        return self._IsYesterdayTrade

    @IsYesterdayTrade.setter
    def IsYesterdayTrade(self, value: bool):
        self._IsYesterdayTrade = value

    @property
    def CloseProfit(self):
        return self._CloseProfit

    @CloseProfit.setter
    def CloseProfit(self, value: float):
        self._CloseProfit = value

    @property
    def CurrMargin(self):
        return self._CurrMargin

    @CurrMargin.setter
    def CurrMargin(self, value: float):
        self._CurrMargin = value

    @property
    def Commission(self):
        return self._Commission

    @Commission.setter
    def Commission(self, value: float):
        self._Commission = value

    @property
    def TradeType(self):
        return self._TradeType

    @TradeType.setter
    def TradeType(self, value: int):
        self._TradeType = value

    @property
    def RtnTradeOrderLocalTime(self):
        return self._RtnTradeOrderLocalTime

    @RtnTradeOrderLocalTime.setter
    def RtnTradeOrderLocalTime(self, value: int):
        self._RtnTradeOrderLocalTime = value
