from ...interface import IPacker


class OHLCValueListDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        ohlc_list = []
        for o in self._obj.OHLCList:
            ohlc_list.append(o.obj_to_tuple())
        return (ohlc_list)

    def tuple_to_obj(self, t):
        if len(t) >= 1:
            self._obj.OHLCList = t[0]

            return True
        return False
