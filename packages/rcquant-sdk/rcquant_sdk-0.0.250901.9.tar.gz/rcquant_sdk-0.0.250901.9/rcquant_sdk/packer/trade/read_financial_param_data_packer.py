from ...interface import IPacker
from typing import Tuple


class ReadFinancialParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.InstrumentID),
                int(self._obj.BeginDate),
                int(self._obj.EndDate),
                int(self._obj.Type),
                list(self._obj.DataList))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 5:
            self._obj.InstrumentID = t[0]
            self._obj.BeginDate = t[1]
            self._obj.EndDate = t[2]
            self._obj.Type = t[3]
            self._obj.DataList = t[4]

            return True
        return False
