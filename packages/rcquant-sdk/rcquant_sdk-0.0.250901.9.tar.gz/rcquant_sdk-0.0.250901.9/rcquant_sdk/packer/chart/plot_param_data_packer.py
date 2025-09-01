from ...interface import IPacker


class PlotParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (int(self._obj.PlotIndex), int(self._obj.Height), (self._obj.IsEqValueAxis), int(self._obj.GridStyle),
                str(self._obj.GridColor), str(self._obj.BackGroundColor), str(self._obj.BorderColor), int(self._obj.BorderWidth),
                bool(self._obj.ShowLegendItem), str(self._obj.PlotName), str(self._obj.PlotNameColor), int(self._obj.GridXStyle),
                str(self._obj.GridXColor), bool(self._obj.Visible), bool(self._obj.ShowTitleCheck))

    def tuple_to_obj(self, t):
        if len(t) >= 15:
            self._obj.PlotIndex = t[0]
            self._obj.Height = t[1]
            self._obj.IsEqValueAxis = t[2]
            self._obj.GridStyle = t[3]
            self._obj.GridColor = t[4]
            self._obj.BackGroundColor = t[5]
            self._obj.BorderColor = t[6]
            self._obj.BorderWidth = t[7]
            self._obj.ShowLegendItem = t[8]
            self._obj.PlotName = t[9]
            self._obj.PlotNameColor = t[10]
            self._obj.GridXStyle = t[11]
            self._obj.GridXColor = t[12]
            self._obj.Visible = t[13]
            self._obj.ShowTitleCheck = t[14]

            return True
        return False
