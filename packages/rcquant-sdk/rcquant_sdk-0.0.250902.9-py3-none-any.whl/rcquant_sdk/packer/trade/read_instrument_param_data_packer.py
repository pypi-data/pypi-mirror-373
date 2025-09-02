from ...interface import IPacker
from typing import Tuple


class ReadInstrumentParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (list(self._obj.ExchangeID), list(self._obj.InstrumentID),
                list(self._obj.UniCode), str(self._obj.LikeUniCode),
                list(self._obj.DataList))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 5:
            self._obj.ExchangeID = t[0]
            self._obj.InstrumentID = t[1]
            self._obj.UniCode = t[2]
            self._obj.LikeUniCode = t[3]
            self._obj.DataList = t[4]

            return True
        return False
