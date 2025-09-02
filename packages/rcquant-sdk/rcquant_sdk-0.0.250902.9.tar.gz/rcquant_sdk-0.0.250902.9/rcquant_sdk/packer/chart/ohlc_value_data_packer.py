from ...interface import IPacker


class OHLCValueDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.GraphID), self._obj.OHLC.obj_to_tuple())

    def tuple_to_obj(self, t):
        if len(t) >= 2:
            self._obj.GraphID = t[0]
            self._obj.OHLC.tuple_to_obj(t[1])

            return True
        return False
