from ...interface import IPacker
from typing import Tuple


class InstrumentDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.InstrumentID), str(self._obj.ExchangeID), str(self._obj.InstrumentName),
                str(self._obj.UniCode), str(self._obj.ProductID), int(self._obj.ProductType), str(self._obj.DeliveryYear),
                str(self._obj.DeliveryMonth), str(self._obj.CreateDate), str(self._obj.OpenDate), str(self._obj.ExpireDate),
                str(self._obj.StartDelivDate), str(self._obj.EndDelivDate), int(self._obj.MaxMarketOrderVolume), int(self._obj.MinMarketOrderVolume),
                int(self._obj.MaxLimitOrderVolume), int(self._obj.MinLimitOrderVolume), int(self._obj.VolumeMultiple), float(self._obj.PriceTick),
                int(self._obj.PricePrecision), bool(self._obj.IsTrading), bool(self._obj.MaxMarginSideAlgorithm), str(self._obj.ProductGroupID),
                float(self._obj.StrikePrice), int(self._obj.OptionsType), str(self._obj.UnderlyingInstrID), float(self._obj.UnderlyingMultiple),
                int(self._obj.CombinationType), int(self._obj.StrikeModeType), float(self._obj.ObjectPrice), float(self._obj.ObjectMarginRatioByMoney),
                float(self._obj.ObjectMarginRatioByVolume), float(self._obj.EnsureRatio1), float(self._obj.EnsureRatio2), bool(self._obj.IsCloseToday),
                self._obj.Times)

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 36:
            self._obj.InstrumentID = t[0]
            self._obj.ExchangeID = t[1]
            self._obj.InstrumentName = t[2]
            self._obj.UniCode = t[3]
            self._obj.ProductID = t[4]
            self._obj.ProductType = t[5]
            self._obj.DeliveryYear = t[6]
            self._obj.DeliveryMonth = t[7]
            self._obj.CreateDate = t[8]
            self._obj.OpenDate = t[9]
            self._obj.ExpireDate = t[10]
            self._obj.StartDelivDate = t[11]
            self._obj.EndDelivDate = t[12]
            self._obj.MaxMarketOrderVolume = t[13]
            self._obj.MinMarketOrderVolume = t[14]
            self._obj.MaxLimitOrderVolume = t[15]
            self._obj.MinLimitOrderVolume = t[16]
            self._obj.VolumeMultiple = t[17]
            self._obj.PriceTick = t[18]
            self._obj.PricePrecision = t[19]
            self._obj.IsTrading = t[20]
            self._obj.MaxMarginSideAlgorithm = t[21]
            self._obj.ProductGroupID = t[22]
            self._obj.StrikePrice = t[23]
            self._obj.OptionsType = t[24]
            self._obj.UnderlyingInstrID = t[25]
            self._obj.UnderlyingMultiple = t[26]
            self._obj.CombinationType = t[27]
            self._obj.StrikeModeType = t[28]
            self._obj.ObjectPrice = t[29]
            self._obj.ObjectMarginRatioByMoney = t[30]
            self._obj.ObjectMarginRatioByVolume = t[31]
            self._obj.EnsureRatio1 = t[32]
            self._obj.EnsureRatio2 = t[33]
            self._obj.IsCloseToday = t[34]
            self._obj.Times = t[35]

            return True
        return False
