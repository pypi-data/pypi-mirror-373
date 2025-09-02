from ...interface import IData
from ...packer.chart.plot_param_data_packer import PlotParamDataPacker


class PlotParamData(IData):
    def __init__(self, plot_index: int = 0, plot_name: str = '', plot_name_color: str = 'white', height: int = 100,
                 is_eqvalue_axis: bool = True, grid_style: int = 2, grid_color: str = "#4f4f4f", back_ground_color: str = "black",
                 border_color: str = "rgb(139,0,0)", border_width: int = 1, show_legend_item: bool = True, grid_x_style: int = 2, grid_x_color: str = '#4f4f4f',
                 visible: bool = True, show_title_check: bool = True):
        """图块配置参数

        Args:
            plot_index (int, optional): 所属图块. Defaults to 0.
            plot_name (str, optional): 图块名称. Defaults to ''.
            plot_name_color (str, optional): 图块名称颜色. Defaults to 'white'.
            height (int, optional): 默认高度(比例). Defaults to 100.
            is_eqvalue_axis (bool, optional): 是否左右y轴相同显示. Defaults to True.
            grid_style (int, optional): 网格水平线样式.1.实线 2.线状虚线 3.点状虚线 4.点线间隔线 5.点点线间隔线 Defaults to 1 Defaults to 2.
            grid_color (str, optional): 网格水平线颜色. Defaults to "#4f4f4f".
            back_ground_color (str, optional): 背景色. Defaults to "black".
            border_color (str, optional): 边框颜色. Defaults to "rgb(139,0,0)".
            border_width (int, optional): 边框宽度. Defaults to 1.
            show_legend_item (bool, optional): 是否显示标签区域. Defaults to True.
            grid_x_style (int, optional): 网格垂直线样式.1.实线 2.线状虚线 3.点状虚线 4.点线间隔线 5.点点线间隔线 Defaults to 2.
            grid_x_color (str, optional): 网格垂直线颜色. Defaults to '#4f4f4f'.
            visible(boo,optional): 是否显示，默认 True
            show_title_check(bool):是否在标题上显示checkbox
        """
        super().__init__(PlotParamDataPacker(self))
        self._PlotIndex: int = plot_index
        self._Height: int = height
        self._IsEqValueAxis: bool = is_eqvalue_axis
        self._GridStyle: int = grid_style
        self._GridColor: str = grid_color
        self._BackGroundColor: str = back_ground_color
        self._BorderColor: str = border_color
        self._BorderWidth: int = border_width
        self._ShowLegendItem: bool = show_legend_item
        self._PlotName: str = plot_name
        self._PlotNameColor: str = plot_name_color
        self._GridXColor: str = grid_x_color
        self._GridXStyle: int = grid_x_style
        self._Visible: bool = visible
        self._ShowTitleCheck: bool = show_title_check

    @property
    def PlotIndex(self):
        return self._PlotIndex

    @PlotIndex.setter
    def PlotIndex(self, value: int):
        self._PlotIndex = value

    @property
    def PlotName(self):
        return self._PlotName

    @PlotName.setter
    def PlotName(self, value: str):
        self._PlotName = value

    @property
    def PlotNameColor(self):
        return self._PlotNameColor

    @PlotNameColor.setter
    def PlotNameColor(self, value: str):
        self._PlotNameColor = value

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, value: int):
        self._Height = value

    @property
    def IsEqValueAxis(self):
        return self._IsEqValueAxis

    @IsEqValueAxis.setter
    def IsEqValueAxis(self, value: bool):
        self._IsEqValueAxis = value

    @property
    def GridStyle(self):
        return self._GridStyle

    @GridStyle.setter
    def GridStyle(self, value: int):
        self._GridStyle = value

    @property
    def GridColor(self):
        return self._GridColor

    @GridColor.setter
    def GridColor(self, value: str):
        self._GridColor = value

    @property
    def BackGroundColor(self):
        return self._BackGroundColor

    @BackGroundColor.setter
    def BackGroundColor(self, value: str):
        self._BackGroundColor = value

    @property
    def BorderColor(self):
        return self._BorderColor

    @BorderColor.setter
    def BorderColor(self, value: str):
        self._BorderColor = value

    @property
    def BorderWidth(self):
        return self._BorderWidth

    @BorderWidth.setter
    def BorderWidth(self, value: int):
        self._BorderWidth = value

    @property
    def ShowLegendItem(self):
        return self._ShowLegendItem

    @ShowLegendItem.setter
    def ShowLegendItem(self, value: bool):
        self._ShowLegendItem = value

    @property
    def GridXStyle(self):
        return self._GridXStyle

    @GridXStyle.setter
    def GridXStyle(self, value: int):
        self._GridXStyle = value

    @property
    def GridXColor(self):
        return self._GridXColor

    @GridXColor.setter
    def GridXColor(self, value: str):
        self._GridXColor = value

    @property
    def Visible(self):
        return self._Visible

    @Visible.setter
    def Visible(self, value: bool):
        self._Visible = value

    @property
    def ShowTitleCheck(self):
        return self._ShowTitleCheck

    @ShowTitleCheck.setter
    def ShowTitleCheck(self, value: bool):
        self._ShowTitleCheck = value
