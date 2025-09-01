from ...interface import IPacker


class TimeAxisParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ShowLabels), str(self._obj.Format))

    def tuple_to_obj(self, t):
        if len(t) >= 2:
            self._obj.ShowLebels = t[0]
            self._obj.Format = t[1]

            return True
        return False
