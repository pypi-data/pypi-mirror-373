import sys
from typing import Dict
from ...interface import IData
from ...packer.chart.bar_graph_param_data_packer import BarGraphParamDataPacker


class BarGraphParamData(IData):

    def __init__(self, id: str = '', name: str = '', style: int = 0, frame_style: int = 0, color: str = "white",
                 price_tick: float = 1.0, tick_valid_mul: float = -1.0, line_width: int = 1, plot_index: int = 0,
                 value_axis_id: int = -1, show_legend: bool = True, legend_format: str = '', legend_color: str = "",
                 join_value_axis: bool = True, valid_max_value: float = 9 * 1e18, valid_min_value: float = -9 * 1e18,
                 user_data: Dict[str, str] = {}, visible: bool = True):
        """柱状图配置参数

        Args:
            id (str, optional):  图唯一编码，不能重复. Defaults to ''.
            name (str, optional): 图名称. Defaults to ''.
            style (int, optional): 样式 -1 NoStyle, 0 Box,1000 UserStyle. Defaults to 0.
            frame_style (int, optional): 边框样式 0 无边框 1 线形 2 3D效果. Defaults to 0.
            color (str, optional): 颜色 white #FFFFFF 格式. Defaults to "white".
            price_tick (float, optional): 有效的变动值. Defaults to 1.0.
            tick_valid_mul (float, optional): 有效倍数,超过倍数的不会计算在轴显示范围内. Defaults to -1.0.
            line_width (int, optional): . Defaults to 1.
            plot_index (int, optional): 图形所属图块. Defaults to 0.
            value_axis_id (int, optional): 图形所属y轴 -1左侧第一个Y轴 -2 左侧第二个,以此类推。1右侧第一个Y轴. Defaults to -1.
            show_legend (bool, optional): 是否显示在legend上. Defaults to True.
            legend_format (str, optional): 在legend上显示的格式,默认是name:value. Defaults to ''.
            legend_color (str, optional): legend上显示的颜色,默认与图的颜色相同. Defaults to "".
            join_value_axis (bool, optional): 是否加入到Y轴显示范围的计算. Defaults to True.
            valid_max_value (float, optional): 最大有效值. Defaults to 9999999.99.
            valid_min_value (float, optional): 最小有效值. Defaults to -9999999.99.
            user_data (Dict[str, str], optional): 用户自定义数据. Defaults to {}.
            visible (bool, optional): 是否显示 Defaults to True.
        """
        super().__init__(BarGraphParamDataPacker(self))
        self._ID: str = id
        self._Name: str = name
        self._Style: int = style
        self._FrameStyle: int = frame_style
        self._Color: str = color
        self._PriceTick: float = price_tick
        self._LineWidth: int = line_width
        self._PlotIndex: int = plot_index
        self._ValueAxisID: int = value_axis_id
        self._ShowLegend: bool = show_legend
        self._LegendFormat: str = legend_format
        self._LegendColor: str = legend_color
        self._JoinValueAxis: bool = join_value_axis
        self._TickValidMul: float = tick_valid_mul
        self._ValidMaxValue: float = valid_max_value
        self._ValidMinValue: float = valid_min_value
        self._UserData: Dict[str, str] = user_data
        self._Visible: bool = visible

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value: str):
        self._ID = value

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, value: str):
        self._Name = value

    @property
    def Style(self):
        return self._Style

    @Style.setter
    def Style(self, value: int):
        self._Style = value

    @property
    def FrameStyle(self):
        return self._FrameStyle

    @FrameStyle.setter
    def FrameStyle(self, value: int):
        self._FrameStyle = value

    @property
    def Color(self):
        return self._Color

    @Color.setter
    def Color(self, value: str):
        self._Color = value

    @property
    def PriceTick(self):
        return self._PriceTick

    @PriceTick.setter
    def PriceTick(self, value):
        self._PriceTick = float(value)

    @property
    def LineWidth(self):
        return self._LineWidth

    @LineWidth.setter
    def LineWidth(self, value: int):
        self._LineWidth = value

    @property
    def PlotIndex(self):
        return self._PlotIndex

    @PlotIndex.setter
    def PlotIndex(self, value: int):
        self._PlotIndex = value

    @property
    def ValueAxisID(self):
        return self._ValueAxisID

    @ValueAxisID.setter
    def ValueAxisID(self, value: int):
        self._ValueAxisID = value

    @property
    def ShowLegend(self):
        return self._ShowLegend

    @ShowLegend.setter
    def ShowLegend(self, value: bool):
        self._ShowLegend = value

    @property
    def LegendFormat(self):
        return self._LegendFormat

    @LegendFormat.setter
    def LegendFormat(self, value: str):
        self._LegendFormat = value

    @property
    def LegendColor(self):
        return self._LegendColor

    @LegendColor.setter
    def LegendColor(self, value: str):
        self._LegendColor = value

    @property
    def JoinValueAxis(self):
        return self._JoinValueAxis

    @JoinValueAxis.setter
    def JoinValueAxis(self, value: bool):
        self._JoinValueAxis = value

    @property
    def ValidMaxValue(self):
        return self._ValidMaxValue

    @ValidMaxValue.setter
    def ValidMaxValue(self, value):
        self._ValidMaxValue = float(value)

    @property
    def ValidMinValue(self):
        return self._ValidMinValue

    @ValidMinValue.setter
    def ValidMinValue(self, value):
        self._ValidMinValue = float(value)

    @property
    def TickValidMul(self):
        return self._TickValidMul

    @TickValidMul.setter
    def TickValidMul(self, value):
        self._TickValidMul = float(value)

    @property
    def UserData(self):
        return self._UserData

    @UserData.setter
    def UserData(self, value: Dict[str, str]):
        self._UserData = value

    @property
    def Visible(self):
        return self._Visible

    @Visible.setter
    def Visible(self, value: bool):
        self._Visible = value
