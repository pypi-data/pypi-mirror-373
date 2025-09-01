from ...interface import IPacker


class QueryParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.MarketName), str(self._obj.InvestorID), str(self._obj.BrokerID), str(self._obj.ExchangeID),
                str(self._obj.ExchangeInstID), str(self._obj.InstrumentID), int(self._obj.ProductType), str(self._obj.ProductID),
                str(self._obj.OrderID), str(self._obj.TradeID), str(self._obj.InsertTimeStart), str(self._obj.InsertTimeEnd),
                str(self._obj.TradeTimeStart), str(self._obj.TradeTimeEnd), str(self._obj.CurrencyID), int(self._obj.HedgeType))

    def tuple_to_obj(self, t):
        if len(t) >= 16:
            self._obj.MarketName = t[0]
            self._obj.InvestorID = t[1]
            self._obj.BrokerID = t[2]
            self._obj.ExchangeID = t[3]
            self._obj.ExchangeInstID = t[4]
            self._obj.InstrumentID = t[5]
            self._obj.ProductType = t[6]
            self._obj.ProductID = t[7]
            self._obj.OrderID = t[8]
            self._obj.TradeID = t[9]
            self._obj.InsertTimeStart = t[10]
            self._obj.InsertTimeEnd = t[11]
            self._obj.TradeTimeStart = t[12]
            self._obj.TradeTimeEnd = t[13]
            self._obj.CurrencyID = t[14]
            self._obj.HedgeType = t[15]

            return True
        return False
