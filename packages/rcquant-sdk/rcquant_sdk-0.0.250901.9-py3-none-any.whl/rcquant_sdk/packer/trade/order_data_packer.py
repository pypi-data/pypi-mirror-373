from ...interface import IPacker
from typing import Tuple


class OrderDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.InvestorID), str(self._obj.BrokerID), str(self._obj.ExchangeID), str(self._obj.ProductID),
                int(self._obj.ProductType), str(self._obj.InstrumentID), str(self._obj.OrderTime), str(self._obj.CancelTime),
                str(self._obj.TradingDay), str(self._obj.InsertDate), str(self._obj.UpdateTime), str(self._obj.StatusMsg),
                int(self._obj.FrontID), int(self._obj.SessionID), str(self._obj.OrderRef), str(self._obj.OrderLocalNo),
                str(self._obj.OrderID), str(self._obj.RelativeOrderSysID), str(self._obj.BrokerOrderSeq), float(self._obj.Price),
                float(self._obj.StopPrice), int(self._obj.Volume), int(self._obj.NoTradedVolume), int(self._obj.Status),
                int(self._obj.Direction), int(self._obj.OpenCloseType), int(self._obj.PriceCond), int(self._obj.TimeCond),
                int(self._obj.VolumeCond), int(self._obj.HedgeType), int(self._obj.OrderType), int(self._obj.ActionType),
                int(self._obj.ContingentCond), float(self._obj.FrozenMarginPrice), float(self._obj.FrozenMargin), float(self._obj.FrozenCommission),
                int(self._obj.ShowVolume), int(self._obj.MinVolume), (self._obj.PricePrecision), str(self._obj.FinBizNo),
                str(self._obj.FinAlgoNo), int(self._obj.FinInsertLocalTime), int(self._obj.FinRtnOrderLocalTime), str(self._obj.FinLockNo),
                str(self._obj.BizName), int(self._obj.RtnOrderLocalTime))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 46:
            self._obj.InvestorID = t[0]
            self._obj.BrokerID = t[1]
            self._obj.ExchangeID = t[2]
            self._obj.ProductID = t[3]
            self._obj.ProductType = t[4]
            self._obj.InstrumentID = t[5]
            self._obj.OrderTime = t[6]
            self._obj.CancelTime = t[7]
            self._obj.TradingDay = t[8]
            self._obj.InsertDate = t[9]
            self._obj.UpdateTime = t[10]
            self._obj.StatusMsg = t[11]
            self._obj.FrontID = t[12]
            self._obj.SessionID = t[13]
            self._obj.OrderRef = t[14]
            self._obj.OrderLocalNo = t[15]
            self._obj.OrderID = t[16]
            self._obj.RelativeOrderSysID = t[17]
            self._obj.BrokerOrderSeq = t[18]
            self._obj.Price = t[19]
            self._obj.StopPrice = t[20]
            self._obj.Volume = t[21]
            self._obj.NoTradedVolume = t[22]
            self._obj.Status = t[23]
            self._obj.Direction = t[24]
            self._obj.OpenCloseType = t[25]
            self._obj.PriceCond = t[26]
            self._obj.TimeCond = t[27]
            self._obj.VolumeCond = t[28]
            self._obj.HedgeType = t[29]
            self._obj.OrderType = t[30]
            self._obj.ActionType = t[31]
            self._obj.ContingentCond = t[32]
            self._obj.FrozenMarginPrice = t[33]
            self._obj.FrozenMargin = t[34]
            self._obj.FrozenCommission = t[35]
            self._obj.ShowVolume = t[36]
            self._obj.MinVolume = t[37]
            self._obj.PricePrecision = t[38]
            self._obj.FinBizNo = t[39]
            self._obj.FinAlgoNo = t[40]
            self._obj.FinInsertLocalTime = t[41]
            self._obj.FinRtnOrderLocalTime = t[42]
            self._obj.FinLockNo = t[43]
            self._obj.BizName = t[44]
            self._obj.RtnOrderLocalTime = t[45]

            return True
        return False
