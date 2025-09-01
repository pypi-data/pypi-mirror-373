from ...interface import IPacker


class TextGraphParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ID), str(self._obj.Name), str(self._obj.Color), int(self._obj.PlotIndex),
                int(self._obj.ValueAxisID), str(self._obj.Text), float(self._obj.Key), float(self._obj.Value),
                int(self._obj.MillTimeSpan), bool(self._obj.JoinValueAxis), bool(self._obj.ShowLegend),
                str(self._obj.LegendFormat), str(self._obj.LegendColor), dict(self._obj.UserData), bool(self._obj.Visible))

    def tuple_to_obj(self, t):
        if len(t) >= 15:
            self._obj.ID = t[0]
            self._obj.Name = t[1]
            self._obj.Color = t[2]
            self._obj.PlotIndex = t[3]
            self._obj.ValueAxisID = t[4]
            self._obj.Text = t[5]
            self._obj.Key = t[6]
            self._obj.Value = t[7]
            self._obj.MillTimeSpan = t[8]
            self._obj.JoinValueAxis = t[9]
            self._obj.ShowLegend = t[10]
            self._obj.LegendFormat = t[11]
            self._obj.LegendColor = t[12]
            self._obj.UserData = t[13]
            self._obj.Visible = t[14]

            return True
        return False
