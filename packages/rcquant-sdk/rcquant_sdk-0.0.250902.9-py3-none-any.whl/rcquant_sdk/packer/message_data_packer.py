from ..interface import IPacker
from typing import Tuple


class MessageDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        return (int(self._obj.MID), int(self._obj.ActionID), int(self._obj.RequestID), bool(self._obj.IsLast),
                bool(self._obj.RspSuccess), str(self._obj.RspMsg), bytes(self._obj.UData), int(self._obj.CompressType))

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 8:
            self._obj.MID = t[0]
            self._obj.ActionID = t[1]
            self._obj.RequestID = t[2]
            self._obj.IsLast = t[3]
            self._obj.RspSuccess = t[4]
            self._obj.RspMsg = t[5]
            self._obj.UData = t[6]
            self._obj.CompressType = t[7]
            return True
        return False
