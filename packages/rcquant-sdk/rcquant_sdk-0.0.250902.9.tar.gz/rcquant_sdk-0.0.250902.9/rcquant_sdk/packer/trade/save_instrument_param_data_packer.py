from ...interface import IPacker
from typing import Tuple


class SaveInstrumentParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (list(self._obj.DataList), str(self._obj.BasePath))

    def tuple_to_obj(self, t):
        if len(t) >= 2:
            self._obj.DataList = t[0]
            self._obj.BasePath = t[1]

            return True
        return False
