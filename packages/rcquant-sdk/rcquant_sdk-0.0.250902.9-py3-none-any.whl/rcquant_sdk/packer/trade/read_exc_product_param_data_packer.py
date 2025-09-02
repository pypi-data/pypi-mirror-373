from ...interface import IPacker
from typing import Tuple


class ReadExcProductParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (list(self._obj.ExchangeID), list(self._obj.ProductID), list(self._obj.DataList))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 3:
            self._obj.ExchangeID = t[0]
            self._obj.ProductID = t[1]
            self._obj.DataList = t[2]

            return True
        return False
