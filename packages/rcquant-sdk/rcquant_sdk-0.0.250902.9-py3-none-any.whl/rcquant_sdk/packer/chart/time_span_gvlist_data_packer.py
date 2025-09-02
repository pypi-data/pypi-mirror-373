from ...interface import IPacker


class TimeSpanGVListDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (self._obj.TimeSpanList, self._obj.GraphValueList, self._obj.OHLCValueList)

    def tuple_to_obj(self, t):
        if len(t) >= 3:
            self._obj.TimeSpanList = t[0]
            self._obj.GraphValueList = t[1]
            self._obj.OHLCValueList = t[2]

            return True
        return False
