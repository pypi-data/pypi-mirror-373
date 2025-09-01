from typing import Dict
from ...interface import IData
from ...packer.chart.marker_graph_param_data_packer import MarkerGraphParamDataPacker


class MarkerGraphParamData(IData):
    def __init__(self, id: str = '', name: str = '', plot_index: int = 0, value_axis_id: int = -1, text: str = '',
                 text_color: str = "white", text_v_align: int = 1, text_h_align: int = 1,
                 orientation: int = 1, line_direc: int = 1, line_width: int = 1, line_style: int = 1,
                 line_color: str = "white", key: float = 0.0, value: float = 0.0, mill_ts: int = -1,
                 join_value_axis=True, show_legend: bool = False, legend_format: str = '',
                 legend_color: str = '', user_data: Dict[str, str] = {}, visible: bool = True):
        """标记配置参数

        Args:
            id (str, optional): 图编码. Defaults to ''.
            name (str, optional): 图名称. Defaults to ''.
            plot_index (int, optional): 所属图块. Defaults to 0.
            value_axis_id (int, optional): 所属值轴. Defaults to -1.
            text (str, optional): 显示文字. Defaults to ''.
            text_color (str, optional): 文字颜色. Defaults to "white".
            text_v_align (int, optional): 文字垂直对齐方式 1.顶部 2.中间 3.底部 Defaults to 1.
            text_h_align (int, optional): 文字水平对齐方式 1.左侧 2.中间 3.右侧 Defaults to 1.
            orientation (int, optional): 文字方向 1.水平 2垂直 Defaults to 1.
            line_direc (int, optional): 线方向 1.水平 2.垂直. Defaults to 1.
            line_width (int, optional): 线宽度. Defaults to 1.
            line_style (int, optional): 线样式.1.实线 2.线状虚线 3.点状虚线 4.点线间隔线 5.点点线间隔线 Defaults to 1.
            line_color (str, optional): 线颜色. Defaults to "white".
            key (float, optional): 数值格式的x轴值. Defaults to 0.0.
            value (float, optional): 数值格式的y轴值. Defaults to 0.0.
            mill_ts (int, optional): 时间戳格式的x轴值. Defaults to -1.
            join_value_axis (bool, optional): 是否加入到y轴可视范围的计算中. Defaults to True.
            show_legend (bool, optional): 是否显示标签. Defaults to True.
            legend_format (str, optional): 标签格式. Defaults to ''.
            legend_color (str, optional): 标签颜色,默认与图颜色相同. Defaults to ''.
            user_data (Dict[str, str], optional): 用户自定义数据. Defaults to {}.
            visible (bool, optional): 是否显示 Defaults to True.
        """
        super().__init__(MarkerGraphParamDataPacker(self))
        self._ID: str = id
        self._Name: str = name
        self._PlotIndex: int = plot_index
        self._ValueAxisID: int = value_axis_id
        self._Text: str = text
        self._TextColor: str = text_color
        self._TextVAlign: int = text_v_align
        self._TextHAlign: int = text_h_align
        self._Orientation: int = orientation
        self._LineDirec: int = line_direc
        self._LineWidth: int = line_width
        self._LineStyle: int = line_style
        self._LineColor: str = line_color
        self._Key: float = key
        self._Value: float = value
        self._MillTimeSpan: int = mill_ts
        self._JoinValueAxis: bool = join_value_axis
        self._ShowLegend: bool = show_legend
        self._LegendFormat: str = legend_format
        self._LegendColor: str = legend_color
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
    def Text(self):
        return self._Text

    @Text.setter
    def Text(self, value: str):
        self._Text = value

    @property
    def TextColor(self):
        return self._TextColor

    @TextColor.setter
    def TextColor(self, value: str):
        self._TextColor = value

    @property
    def TextVAlign(self):
        return self._TextVAlign

    @TextVAlign.setter
    def TextVAlign(self, value: int):
        self._TextVAlign = value

    @property
    def TextHAlign(self):
        return self._TextHAlign

    @TextHAlign.setter
    def TextHAlign(self, value: int):
        self._TextHAlign = value

    @property
    def Orientation(self):
        return self._Orientation

    @Orientation.setter
    def Orientation(self, value: int):
        self._Orientation = value

    @property
    def LineDirec(self):
        return self._LineDirec

    @LineDirec.setter
    def LineDirec(self, value: int):
        self._LineDirec = value

    @property
    def LineWidth(self):
        return self._LineWidth

    @LineWidth.setter
    def LineWidth(self, value: int):
        self._LineWidth = value

    @property
    def LineStyle(self):
        return self._LineStyle

    @LineStyle.setter
    def LineStyle(self, value: int):
        self._LineStyle = value

    @property
    def LineColor(self):
        return self._LineColor

    @LineColor.setter
    def LineColor(self, value: str):
        self._LineColor = value

    @property
    def Key(self):
        return self._Key

    @Key.setter
    def Key(self, value: float):
        self._Key = value

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, value: float):
        self._Value = value

    @property
    def MillTimeSpan(self):
        return self._MillTimeSpan

    @MillTimeSpan.setter
    def MillTimeSpan(self, value: int):
        self._MillTimeSpan = value

    @property
    def JoinValueAxis(self):
        return self._JoinValueAxis

    @JoinValueAxis.setter
    def JoinValueAxis(self, value: bool):
        self._JoinValueAxis = value

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
