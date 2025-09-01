import sys
from typing import Dict
from ...interface import IData
from ...packer.chart.financial_graph_param_data_packer import FinancialGraphParamDataPacker


class FinancialGraphParamData(IData):
    def __init__(self, id: str = '', name: str = '', style: int = 0,
                 asc_color: str = 'red', asc_brush: str = 'black', desc_color: str = 'cyan',
                 desc_brush: str = 'cyan', plot_index: int = 0, value_axis_id: int = -1,
                 price_tick: float = -1.0, tick_valid_mul: float = -1.0, show_legend: bool = True,
                 legend_format: str = '', legend_color: str = 'white', bind_ins_id: str = '', bind_range: str = '',
                 join_value_axis=True, valid_max_value: float = 9 * 1e18, valid_min_value: float = -9 * 1e18,
                 user_data: Dict[str, str] = {}, visible: bool = True):
        """K线图配置参数

        Args:
            id (str, optional): 图唯一编码，不能重复. Defaults to ''.
            name (str, optional): 图名称. Defaults to ''.
            style (int, optional): 0 蜡烛图. Defaults to 0.
            asc_color (str, optional): 涨颜色. Defaults to 'red'.
            asc_brush (str, optional): 涨填充. Defaults to 'black'.
            desc_color (str, optional): 跌颜色. Defaults to 'cyan'.
            desc_brush (str, optional): 跌填充. Defaults to 'cyan'.
            plot_index (int, optional): 所属区块. Defaults to 0.
            value_axis_id (int, optional): 所属Y轴. Defaults to -1.
            price_tick (float, optional): 有效变动值. Defaults to -1.0.
            tick_valid_mul (float, optional): 有效倍数,超过倍数的不会计算在轴显示范围内. Defaults to -1.0.
            show_legend (bool, optional): 是否显示在legend上. Defaults to True.
            legend_format (str, optional): 在legend上显示的格式. Defaults to ''.
            legend_color (str, optional): legend上显示的颜色. Defaults to 'white'.
            bind_ins_id (str, optional): 绑定合约编码. Defaults to ''.
            bind_range (str, optional): 绑定周期. Defaults to ''.
            join_value_axis (bool, optional): 是否加入到Y轴显示范围的计算. Defaults to True.
            valid_max_value (float, optional): 最大有效值. Defaults to 9999999.99.
            valid_min_value (float, optional): 最小有效值. Defaults to -9999999.99.
            user_data (Dict[str, str], optional): 用户自定义数据. Defaults to {}.
            visible (bool, optional): 是否显示 Defaults to True.
        """
        super().__init__(FinancialGraphParamDataPacker(self))
        self._ID: str = id
        self._Name: str = name
        self._Style: int = style
        self._AscColor: str = asc_color
        self._AscBrush: str = asc_brush
        self._DescColor: str = desc_color
        self._DescBrush: str = desc_brush
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
    def AscColor(self):
        return self._AscColor

    @AscColor.setter
    def AscColor(self, value: str):
        self._AscColor = value

    @property
    def AscBrush(self):
        return self._AscBrush

    @AscBrush.setter
    def AscBrush(self, value):
        self._AscBrush = str(value)

    @property
    def DescColor(self):
        return self._DescColor

    @DescColor.setter
    def DescColor(self, value):
        self._DescColor = str(value)

    @property
    def DescBrush(self):
        return self._DescBrush

    @DescBrush.setter
    def DescBrush(self, value):
        self._DescBrush = str(value)

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
        self._ShowLegend = bool(value)

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
