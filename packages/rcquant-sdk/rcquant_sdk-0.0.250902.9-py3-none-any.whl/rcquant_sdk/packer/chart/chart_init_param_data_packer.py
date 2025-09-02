from ...interface import IPacker


class ChartInitParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    @staticmethod
    def objlist_to_tuplelist(objlist):
        retlist = list()
        for obj in objlist:
            retlist.append(obj.obj_to_tuple())
        return retlist

    def obj_to_tuple(self):
        return (str(self._obj.ChartID), str(self._obj.Title), int(self._obj.Height), int(self._obj.Width),
                bool(self._obj.IsSaveGeometry), int(self._obj.ReplotTime),
                self._obj.GlobalTimeAxisParam.obj_to_tuple(),
                self._obj.GlobalValueAxisParam.obj_to_tuple(),
                self._obj.GlobalPlotParam.obj_to_tuple(),
                self._obj.GlobalLegendItemParam.obj_to_tuple(),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.PlotParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.ValueAxisParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.LegendItemParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.LineGraphParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.FinancialGraphParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.BarGraphParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.TextGraphParamList),
                ChartInitParamDataPacker.objlist_to_tuplelist(self._obj.MarkerGraphParamList),
                self._obj.TimeSpanList,
                self._obj.GraphValueList,
                self._obj.OHLCValueList,
                bool(self._obj.IsFullScreen),
                bool(self._obj.IsRangeSliderVisible),
                int(self._obj.ShowDays),
                self._obj.BottomLabelList,
                str(self._obj.LastDataFile),
                dict(self._obj.UserData),
                bool(self._obj.IsActivateWindow),
                int(self._obj.UnActiveRefreshRange),
                bool(self._obj.IsStatusWidgetVisible),
                str(self._obj.ScreenName))

    def tuple_to_obj(self, t):
        if len(t) >= 31:
            self._obj.ChartID = t[0]
            self._obj.Title = t[1]
            self._obj.Height = t[2]
            self._obj.Width = t[3]
            self._obj.IsSaveGeometry = t[4]
            self._obj.ReplotTime = t[5]
            self._obj.GlobalTimeAxisParam = t[6]
            self._obj.GlobalValueAxisParam = t[7]
            self._obj.GlobalPlotParam = t[8]
            self._obj.GlobalLegendItemParam = t[9]
            self._obj.PlotParamList = t[10]
            self._obj.ValueAxisParamList = t[11]
            self._obj.LegendItemParamList = t[12]
            self._obj.LineGraphParamList = t[13]
            self._obj.FinancialGraphParamList = t[14]
            self._obj.BarGraphParamList = t[15]
            self._obj.TextGraphParamList = t[16]
            self._obj.MarkerGraphParamList = t[17]
            self._obj.TimeSpanList = t[18]
            self._obj.GraphValueList = t[19]
            self._obj.OHLCValueList = t[20]
            self._obj.IsFullScreen = t[21]
            self._obj.IsRangeSliderVisible = t[22]
            self._obj.ShowDays = t[23]
            self._obj.BottomLabelList = t[24]
            self._obj.LastDataFile = t[25]
            self._obj.UserData = t[26]
            self._obj.IsActivateWindow = t[27]
            self._obj.UnActiveRefreshRange = t[28]
            self._obj.IsStatusWidgetVisible = t[29]
            self._obj.ScreenName = t[30]

            return True
        return False
