from ...interface import IPacker
from typing import Tuple


class FinancialFiledDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (int(self._obj.ID), str(self._obj.Day),
                int(self._obj.Type), str(self._obj.JsonData))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 4:
            self._obj.ID = t[0]
            self._obj.Day = t[1]
            self._obj.Type = t[2]
            self._obj.JsonData = t[3]

            return True
        return False
