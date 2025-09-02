from ...interface import IData
from ...packer.chart.legend_item_param_data_packer import LegendItemParamDataPacker


class LegendItemParamData(IData):
    def __init__(self, plot_index: int = 0, type: int = 0, h_algin: int = 1, v_algin: int = 1, item_margin: int = 2,
                 item_space: int = 2, h_offset: int = 2, v_offset: int = 2, max_columns: int = 8, border_width: int = 1,
                 border_color: str = "", border_radius: int = 4, back_ground_alpha: int = 240, back_ground_color: str = ''):
        """图例标签配置项

        Args:
            plot_index (int, optional): 所属图块. Defaults to 0.
            type (int, optional): 类型 0 独占一块区域显示,1 与其他图叠加显示. Defaults to 0.
            h_algin (int, optional): 水平间距. Defaults to 1.
            v_algin (int, optional): 垂直间距. Defaults to 1.
            item_margin (int, optional): 项目间距. Defaults to 2.
            item_space (int, optional): 项目间空格. Defaults to 2.
            h_offset (int, optional): 水平偏移量. Defaults to 2.
            v_offset (int, optional): 垂直偏移量. Defaults to 2.
            max_columns (int, optional): 每行最大项目数. Defaults to 8.
            border_width (int, optional): 边框宽度. Defaults to 1.
            border_color (str, optional): 边框颜色. Defaults to "".
            border_radius (int, optional): 边框角弧度. Defaults to 4.
            back_ground_alpha (int, optional): 背景透明度. Defaults to 240.
            back_ground_color (str, optional): 背景色. Defaults to ''.
        """
        super().__init__(LegendItemParamDataPacker(self))
        self._PlotIndex: int = plot_index
        self._Type: int = type
        self._HAlgin: int = h_algin
        self._VAlgin: int = v_algin
        self._ItemMargin: int = item_margin
        self._ItemSpace: int = item_space
        self._HOffset: int = h_offset
        self._VOffset: int = v_offset
        self._MaxColumns: int = max_columns
        self._BorderWidth: int = border_width
        self._BorderColor: str = border_color
        self._BorderRadius: int = border_radius
        self._BackGroundAlpha: int = back_ground_alpha
        self._BackGroundColor: str = back_ground_color

    @property
    def PlotIndex(self):
        return self._PlotIndex

    @PlotIndex.setter
    def PlotIndex(self, value: int):
        self._PlotIndex = value

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, value: int):
        self._Type = value

    @property
    def HAlgin(self):
        return self._HAlgin

    @HAlgin.setter
    def HAlgin(self, value: int):
        self._HAlgin = value

    @property
    def VAlgin(self):
        return self._VAlgin

    @VAlgin.setter
    def VAlgin(self, value: int):
        self._VAlgin = value

    @property
    def ItemMargin(self):
        return self._ItemMargin

    @ItemMargin.setter
    def ItemMargin(self, value: int):
        self._ItemMargin = value

    @property
    def ItemSpace(self):
        return self._ItemSpace

    @ItemSpace.setter
    def ItemSpace(self, value: int):
        self._ItemSpace = value

    @property
    def HOffset(self):
        return self._HOffset

    @HOffset.setter
    def HOffset(self, value: int):
        self._HOffset = value

    @property
    def VOffset(self):
        return self._VOffset

    @VOffset.setter
    def VOffset(self, value: int):
        self._VOffset = value

    @property
    def MaxColumns(self):
        return self._MaxColumns

    @MaxColumns.setter
    def MaxColumns(self, value: int):
        self._MaxColumns = value

    @property
    def BorderWidth(self):
        return self._BorderWidth

    @BorderWidth.setter
    def BorderWidth(self, value: int):
        self._BorderWidth = value

    @property
    def BorderColor(self):
        return self._BorderColor

    @BorderColor.setter
    def BorderColor(self, value: str):
        self._BorderColor = value

    @property
    def BorderRadius(self):
        return self._BorderRadius

    @BorderRadius.setter
    def BorderRadius(self, value: int):
        self._BorderRadius = value

    @property
    def BackGroundAlpha(self):
        return self._BackGroundAlpha

    @BackGroundAlpha.setter
    def BackGroundAlpha(self, value: int):
        self._BackGroundAlpha = value

    @property
    def BackGroundColor(self):
        return self._BackGroundColor

    @BackGroundColor.setter
    def BackGroundColor(self, value: str):
        self._BackGroundColor = value
