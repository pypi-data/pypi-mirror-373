from ...interface import IPacker


class LegendItemParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (int(self._obj.PlotIndex), int(self._obj.Type), int(self._obj.HAlgin),
                int(self._obj.VAlgin), int(self._obj.ItemMargin),
                int(self._obj.ItemSpace), int(self._obj.HOffset),
                int(self._obj.VOffset), int(self._obj.MaxColumns),
                int(self._obj.BorderWidth), str(self._obj.BorderColor),
                int(self._obj.BorderRadius), int(self._obj.BackGroundAlpha),
                str(self._obj.BackGroundColor))

    def tuple_to_obj(self, t):
        if len(t) >= 14:
            self._obj.PlotIndex = t[0]
            self._obj.Type = t[1]
            self._obj.HAlgin = t[2]
            self._obj.VAlgin = t[3]
            self._obj.ItemMargin = t[4]
            self._obj.ItemSpace = t[5]
            self._obj.HOffset = t[6]
            self._obj.VOffset = t[7]
            self._obj.MaxColumns = t[8]
            self._obj.BorderWidth = t[9]
            self._obj.BorderColor = t[10]
            self._obj.BorderRadius = t[11]
            self._obj.BackGroundAlpha = t[12]
            self._obj.BackGroundColor = t[13]

            return True
        return False
