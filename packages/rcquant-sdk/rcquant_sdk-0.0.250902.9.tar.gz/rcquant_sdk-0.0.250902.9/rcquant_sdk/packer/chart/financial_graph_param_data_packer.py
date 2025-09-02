from ...interface import IPacker


class FinancialGraphParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ID), str(self._obj.Name), int(self._obj.Style), str(self._obj.AscColor),
                str(self._obj.AscBrush), str(self._obj.DescColor), str(self._obj.DescBrush), int(self._obj.PlotIndex),
                int(self._obj.ValueAxisID), float(self._obj.PriceTick), float(self._obj.TickValidMul), (self._obj.ShowLegend),
                str(self._obj.LegendFormat), str(self._obj.LegendColor), str(self._obj.BindInsID), str(self._obj.BindRange), bool(self._obj.JoinValueAxis),
                float(self._obj.ValidMaxValue), float(self._obj.ValidMinValue), self._obj.UserData, bool(self._obj.Visible))

    def tuple_to_obj(self, t):
        if len(t) >= 21:
            self._obj.ID = t[0]
            self._obj.Name = t[1]
            self._obj.Style = t[2]
            self._obj.AscColor = t[3]
            self._obj.AscBrush = t[4]
            self._obj.DescColor = t[5]
            self._obj.DescBrush = t[6]
            self._obj.PlotIndex = t[7]
            self._obj.ValueAxisID = t[8]
            self._obj.PriceTick = t[9]
            self._obj.TickValidMul = t[10]
            self._obj.ShowLegend = t[11]
            self._obj.LegendFormat = t[12]
            self._obj.LegendColor = t[13]
            self._obj.BindInsID = t[14]
            self._obj.BindRange = t[15]
            self._obj.JoinValueAxis = t[16]
            self._obj.ValidMaxValue = t[17]
            self._obj.ValidMinValue = t[18]
            self._obj.UserData = t[19]
            self._obj.Visible = t[20]

            return True
        return False
