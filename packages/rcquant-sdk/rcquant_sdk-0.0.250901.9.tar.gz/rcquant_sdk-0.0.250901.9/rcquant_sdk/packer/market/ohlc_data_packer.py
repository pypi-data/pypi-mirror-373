from ...interface import IPacker


class OHLCDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ExchangeID), str(self._obj.InstrumentID), str(self._obj.TradingDay), str(self._obj.TradingTime),
                str(self._obj.StartTime), str(self._obj.EndTime), str(self._obj.ActionDay), int(self._obj.ActionTimeSpan),
                int(self._obj.Range), int(self._obj.Index), float(self._obj.OpenPrice), float(self._obj.HighestPrice),
                float(self._obj.LowestPrice), float(self._obj.ClosePrice), float(self._obj.TotalTurnover), int(self._obj.TotalVolume),
                float(self._obj.OpenInterest), float(self._obj.PreSettlementPrice), float(self._obj.ChangeRate), float(self._obj.ChangeValue),
                float(self._obj.OpenBidPrice), float(self._obj.OpenAskPrice), int(self._obj.OpenBidVolume), int(self._obj.OpenAskVolume),
                float(self._obj.HighestBidPrice), float(self._obj.HighestAskPrice), int(self._obj.HighestBidVolume), int(self._obj.HighestAskVolume),
                float(self._obj.LowestBidPrice), float(self._obj.LowestAskPrice), int(self._obj.LowestBidVolume), int(self._obj.LowestAskVolume),
                float(self._obj.CloseBidPrice), float(self._obj.CloseAskPrice), int(self._obj.CloseBidVolume), int(self._obj.CloseAskVolume))

    def tuple_to_obj(self, t):
        if len(t) >= 36:
            self._obj.ExchangeID = t[0]
            self._obj.InstrumentID = t[1]
            self._obj.TradingDay = t[2]
            self._obj.TradingTime = t[3]
            self._obj.StartTime = t[4]
            self._obj.EndTime = t[5]
            self._obj.ActionDay = t[6]
            self._obj.ActionTimeSpan = t[7]
            self._obj.Range = t[8]
            self._obj.Index = t[9]
            self._obj.OpenPrice = t[10]
            self._obj.HighestPrice = t[11]
            self._obj.LowestPrice = t[12]
            self._obj.ClosePrice = t[13]
            self._obj.TotalTurnover = t[14]
            self._obj.TotalVolume = t[15]
            self._obj.OpenInterest = t[16]
            self._obj.PreSettlementPrice = t[17]
            self._obj.ChangeRate = t[18]
            self._obj.ChangeValue = t[19]
            self._obj.OpenBidPrice = t[20]
            self._obj.OpenAskPrice = t[21]
            self._obj.OpenBidVolume = t[22]
            self._obj.OpenAskVolume = t[23]
            self._obj.HighestBidPrice = t[24]
            self._obj.HighestAskPrice = t[25]
            self._obj.HighestBidVolume = t[26]
            self._obj.HighestAskVolume = t[27]
            self._obj.LowestBidPrice = t[28]
            self._obj.LowestAskPrice = t[29]
            self._obj.LowestBidVolume = t[30]
            self._obj.LowestAskVolume = t[31]
            self._obj.CloseBidPrice = t[32]
            self._obj.CloseAskPrice = t[33]
            self._obj.CloseBidVolume = t[34]
            self._obj.CloseAskVolume = t[35]

            return True
        return False
