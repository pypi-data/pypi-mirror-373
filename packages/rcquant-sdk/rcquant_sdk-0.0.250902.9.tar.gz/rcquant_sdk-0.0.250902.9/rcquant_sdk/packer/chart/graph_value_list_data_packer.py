from ...interface import IPacker


class GraphValueListDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        gv_list = []
        for o in self._obj.GVList:
            gv_list.append(o.obj_to_tuple())
        return tuple([gv_list])

    def tuple_to_obj(self, t):
        if len(t) >= 1:
            self._obj.OHLCList = t[0]

            return True
        return False
