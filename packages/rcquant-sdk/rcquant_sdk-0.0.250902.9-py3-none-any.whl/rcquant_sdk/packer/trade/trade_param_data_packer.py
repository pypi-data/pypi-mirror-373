from ...interface import IPacker
from typing import Tuple


class TradeParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return tuple([str(self._obj.TradeNames)])

    def tuple_to_obj(self, t):
        if len(t) >= 1:
            self._obj.TradeNames = t[0]
            return True
        return False
