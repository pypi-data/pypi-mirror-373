from ...interface import IPacker


class TickDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ExchangeID), str(self._obj.InstrumentID), str(self._obj.ActionDay),
                str(self._obj.ActionTime), int(self._obj.UpdateMillisec), float(self._obj.LastPrice),
                int(self._obj.LastVolume), float(self._obj.BidPrice), int(self._obj.BidVolume),
                float(self._obj.AskPrice), int(self._obj.AskVolume), float(self._obj.TotalTurnover),
                int(self._obj.TotalVolume), float(self._obj.OpenInterest), float(self._obj.PreClosePrice),
                float(self._obj.PreSettlementPrice), float(self._obj.PreOpenInterest))

    def tuple_to_obj(self, t):
        if len(t) >= 17:
            self._obj.ExchangeID = t[0]
            self._obj.InstrumentID = t[1]
            self._obj.ActionDay = t[2]
            self._obj.ActionTime = t[3]
            self._obj.UpdateMillisec = t[4]
            self._obj.LastPrice = t[5]
            self._obj.LastVolume = t[6]
            self._obj.BidPrice = t[7]
            self._obj.BidVolume = t[8]
            self._obj.AskPrice = t[9]
            self._obj.AskVolume = t[10]
            self._obj.TotalTurnover = t[11]
            self._obj.TotalVolume = t[12]
            self._obj.OpenInterest = t[13]
            self._obj.PreClosePrice = t[14]
            self._obj.PreSettlementPrice = t[15]
            self._obj.PreOpenInterest = t[16]
            return True
        return False
