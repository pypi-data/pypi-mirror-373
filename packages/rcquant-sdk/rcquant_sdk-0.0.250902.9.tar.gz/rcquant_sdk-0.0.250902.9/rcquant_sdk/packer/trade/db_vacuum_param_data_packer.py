from ...interface import IPacker
from typing import Tuple


class DBVacuumParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (list(self._obj.InstrumentID), list(self._obj.Period))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 2:
            self._obj.InstrumentID = t[0]
            self._obj.Period = t[1]

            return True
        return False
