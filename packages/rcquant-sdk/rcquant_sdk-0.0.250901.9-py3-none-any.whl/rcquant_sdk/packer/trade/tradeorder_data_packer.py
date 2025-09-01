from ...interface import IPacker
from typing import Tuple


class TradeOrderDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.ExchangeID), str(self._obj.ProductID), str(self._obj.InstrumentID), str(self._obj.TradeTime),
                str(self._obj.TradingDay), str(self._obj.TradeDate), str(self._obj.BrokerOrderSeq), str(self._obj.OrderID),
                str(self._obj.TradeID), float(self._obj.Price), int(self._obj.Volume), int(self._obj.UnCloseVolume),
                int(self._obj.Direction), int(self._obj.OpenCloseType), int(self._obj.HedgeType), bool(self._obj.IsYesterdayTrade),
                float(self._obj.CloseProfit), float(self._obj.CurrMargin), float(self._obj.Commission), int(self._obj.TradeType),
                int(self._obj.RtnTradeOrderLocalTime))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 21:
            self._obj.ExchangeID = t[0]
            self._obj.ProductID = t[1]
            self._obj.InstrumentID = t[2]
            self._obj.TradeTime = t[3]
            self._obj.TradingDay = t[4]
            self._obj.TradeDate = t[5]
            self._obj.BrokerOrderSeq = t[6]
            self._obj.OrderID = t[7]
            self._obj.TradeID = t[8]
            self._obj.Price = t[9]
            self._obj.Volume = t[10]
            self._obj.UnCloseVolume = t[11]
            self._obj.Direction = t[12]
            self._obj.OpenCloseType = t[13]
            self._obj.HedgeType = t[14]
            self._obj.IsYesterdayTrade = t[15]
            self._obj.CloseProfit = t[16]
            self._obj.CurrMargin = t[17]
            self._obj.Commission = t[18]
            self._obj.TradeType = t[19]
            self._obj.RtnTradeOrderLocalTime = t[20]

            return True
        return False
