from ...interface import IPacker
from typing import Tuple


class ExcProductTimeDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (str(self._obj.StartTime), str(self._obj.EndTime),
                int(self._obj.Index), int(self._obj.AddDay),
                int(self._obj.InstrumentStatusKind))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 5:
            self._obj.StartTime = t[0]
            self._obj.EndTime = t[1]
            self._obj.Index = t[2]
            self._obj.AddDay = t[3]
            self._obj.InstrumentStatusKind = t[4]

            return True
        return False
