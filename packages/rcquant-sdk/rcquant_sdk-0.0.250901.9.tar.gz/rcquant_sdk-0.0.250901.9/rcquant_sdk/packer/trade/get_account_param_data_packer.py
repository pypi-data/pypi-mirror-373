from ...interface import IPacker
from typing import Tuple


class GetAccountParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.TradeName), self._obj.Account.obj_to_tuple())

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 2:
            self._obj.TradeName = t[0]
            self._obj.Account.tuple_to_obj(t[1])
            return True
        return False
