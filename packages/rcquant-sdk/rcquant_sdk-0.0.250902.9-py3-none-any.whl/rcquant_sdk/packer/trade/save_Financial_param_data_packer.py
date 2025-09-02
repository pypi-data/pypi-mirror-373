from ...interface import IPacker
from typing import Tuple


class SaveFinancialParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.InstrumentID), list(self._obj.DataList), str(self._obj.BasePath))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 3:
            self._obj.InstrumentID = t[0]
            self._obj.DataList = t[1]
            self._obj.BasePath = t[2]

            return True
        return False
