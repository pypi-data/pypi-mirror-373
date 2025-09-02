from ...interface import IPacker
from typing import Tuple


class ExcProductDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.ExchangeID), str(self._obj.ProductID), str(self._obj.ProductName), float(self._obj.VolumeMultiple),
                float(self._obj.PriceTick), int(self._obj.MaxMarketOrderVolume), int(self._obj.MaxLimitOrderVolume), (self._obj.Times))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 8:
            self._obj.ExchangeID = t[0]
            self._obj.ProductID = t[1]
            self._obj.ProductName = t[2]
            self._obj.VolumeMultiple = t[3]
            self._obj.PriceTick = t[4]
            self._obj.MaxMarketOrderVolume = t[5]
            self._obj.MaxLimitOrderVolume = t[6]
            self._obj.Times = t[7]

            return True
        return False
