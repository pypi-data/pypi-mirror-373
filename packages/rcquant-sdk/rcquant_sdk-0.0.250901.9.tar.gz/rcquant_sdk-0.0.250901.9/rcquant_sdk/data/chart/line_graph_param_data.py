import sys
from typing import Dict
from ...interface import IData
from ...packer.chart.line_graph_param_data_packer import LineGraphParamDataPacker


class LineGraphParamData(IData):
    def __init__(self, id: str = '', name: str = '', style: int = 1,
                 color: str = 'white', width: int = 1, plot_index: int = 0, value_axis_id: int = -1,
                 price_tick: float = -1.0, tick_valid_mul: float = -1.0, show_legend: bool = True,
                 legend_format: str = '', legend_color: str = '', bind_ins_id: str = '', bind_range: str = '',
                 join_value_axis=True, valid_max_value: float = 9 * 1e18, valid_min_value: float = -9 * 1e18,
                 user_data: Dict[str, str] = {}, visible: bool = True, is_show_symbol: bool = False, show_symbol_limit: int = 1000,
                 render_antialiased: bool = False):
        """线图配置参数

        Args:
            id (str, optional): 图形编码. Defaults to ''.
            name (str, optional): 图形名称. Defaults to ''.
            style (int, optional): 图形样式.1.实线 2.线状虚线 3.点状虚线 4.点线间隔线 5.点点线间隔线 7.只显示数据点,没有线 Defaults to 1.
            color (str, optional): 颜色. Defaults to 'white'.
            width (int, optional): 宽度. Defaults to 1.
            plot_index (int, optional): 所属图块. Defaults to 0.
            value_axis_id (int, optional): 所属值轴. Defaults to -1.
            price_tick (float, optional): 变动值. Defaults to -1.0.
            tick_valid_mul (float, optional): 有效倍数. Defaults to -1.0.
            show_legend (bool, optional): 是否显示标签. Defaults to True.
            legend_format (str, optional): 标签格式. Defaults to ''.
            legend_color (str, optional): 标签颜色,默认与图颜色相同. Defaults to ''.
            bind_ins_id (str, optional): 绑定合约编码. Defaults to ''.
            bind_range (str, optional): 绑定合约周期. Defaults to ''.
            join_value_axis (bool, optional): 是否加入值轴可视范围计算内. Defaults to True.
            valid_max_value (float, optional): 最大有效值. Defaults to 9999999.99.
            valid_min_value (float, optional): 最小有效值. Defaults to -9999999.99.
            user_data (Dict[str, str], optional): 用户自定义数据. Defaults to {}.
            visible (bool, optional): 是否显示 Defaults to True.
            is_show_symbol (bool, optional): 是否显示数据点 Defaults to True.
            show_symbol_limit (int, optional): 数据量不超设置值时显示数据点 Defaults to 1000.
            render_antialiased (bool, optional): 是否抗锯齿 Defaults to True.
        """
        super().__init__(LineGraphParamDataPacker(self))
        self._ID: str = id
        self._Name: str = name
        if self._Name == '':
            self._Name = self._ID
        self._Style: int = style
        self._Color: str = color
        self._Width: int = width
        self._PlotIndex: int = plot_index
        self._ValueAxisID: int = value_axis_id
        self._PriceTick: float = price_tick
        self._TickValidMul: float = tick_valid_mul
        self._ShowLegend: bool = show_legend
        self._LegendFormat: str = legend_format
        self._LegendColor: str = legend_color
        self._BindInsID: str = bind_ins_id
        self._BindRange: str = bind_range
        self._JoinValueAxis: bool = join_value_axis
        self._ValidMaxValue: float = valid_max_value
        self._ValidMinValue: float = valid_min_value
        self._UserData: Dict[str, str] = user_data
        self._Visible: bool = visible
        self._IsShowSymbol: bool = is_show_symbol
        self._ShowSymbolLimit: int = show_symbol_limit
        self._RenderAntialiased: bool = render_antialiased

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
    def Style(self, value):
        self._Style = int(value)

    @property
    def Color(self):
        return self._Color

    @Color.setter
    def Color(self, value):
        self._Color = str(value)

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, value):
        self._Width = int(value)

    @property
    def PlotIndex(self):
        return self._PlotIndex

    @PlotIndex.setter
    def PlotIndex(self, value):
        self._PlotIndex = int(value)

    @property
    def ValueAxisID(self):
        return self._ValueAxisID

    @ValueAxisID.setter
    def ValueAxisID(self, value):
        self._ValueAxisID = int(value)

    @property
    def PriceTick(self):
        return self._PriceTick

    @PriceTick.setter
    def PriceTick(self, value):
        self._PriceTick = float(value)

    @property
    def TickValidMul(self):
        return self._TickValidMul

    @TickValidMul.setter
    def TickValidMul(self, value):
        self._TickValidMul = float(value)

    @property
    def ShowLegend(self):
        return self._ShowLegend

    @ShowLegend.setter
    def ShowLegend(self, value):
        self._ShowLegend = (value)

    @property
    def LegendFormat(self):
        return self._LegendFormat

    @LegendFormat.setter
    def LegendFormat(self, value):
        self._LegendFormat = str(value)

    @property
    def LegendColor(self):
        return self._LegendColor

    @LegendColor.setter
    def LegendColor(self, value):
        self._LegendColor = str(value)

    @property
    def BindInsID(self):
        return self._BindInsID

    @BindInsID.setter
    def BindInsID(self, value):
        self._BindInsID = str(value)

    @property
    def BindRange(self):
        return self._BindRange

    @BindRange.setter
    def BindRange(self, value):
        self._BindRange = str(value)

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

    @property
    def IsShowSymbol(self):
        return self._IsShowSymbol

    @IsShowSymbol.setter
    def IsShowSymbol(self, value: bool):
        self._IsShowSymbol = value

    @property
    def ShowSymbolLimit(self):
        return self._ShowSymbolLimit

    @ShowSymbolLimit.setter
    def ShowSymbolLimit(self, value):
        self._ShowSymbolLimit = int(value)

    @property
    def RenderAntialiased(self):
        return self._RenderAntialiased

    @RenderAntialiased.setter
    def RenderAntialiased(self, value: bool):
        self._RenderAntialiased = value
