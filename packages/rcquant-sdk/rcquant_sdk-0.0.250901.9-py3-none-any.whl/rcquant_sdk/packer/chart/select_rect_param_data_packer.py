from ...interface import IPacker


class SelectRectParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ChartID), int(self._obj.PlotIndex), str(self._obj.ActionKey), float(self._obj.XMin),
                float(self._obj.XMax), (self._obj.GraphParams))

    def tuple_to_obj(self, t):
        if len(t) >= 6:
            self._obj.ChartID = t[0]
            self._obj.PlotIndex = t[1]
            self._obj.ActionKey = t[2]
            self._obj.XMin = t[3]
            self._obj.XMax = t[4]
            self._obj.GraphParams = t[5]

            return True
        return False
