from ...interface import IPacker
from typing import Tuple


class ReadInsDateRangeDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.InstrumentID),
                str(self._obj.Period),
                int(self._obj.StartDate),
                int(self._obj.EndDate),
                str(self._obj.RangeBegin),
                str(self._obj.RangeEnd))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 6:
            self._obj.InstrumentID = t[0]
            self._obj.Period = t[1]
            self._obj.StartDate = t[2]
            self._obj.EndDate = t[3]
            self._obj.RangeBegin = t[4]
            self._obj.RangeEnd = t[5]

            return True
        return False
