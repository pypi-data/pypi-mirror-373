from ...interface import IData
from ...packer.chart.value_axis_param_data_packer import ValueAxisParamDataPacker


class ValueAxisParamData(IData):
    def __init__(self, plot_index: int = 0, value_axis_id: int = -1, max_tick_num: int = 6, steps: float = -1.0,
                 format: str = '', label_text_len: int = 6, valid_mul: float = -1.0, price_tick: float = 1.0,
                 max_value: float = 9 * 1e18, min_value: float = -9 * 1e18,):
        """value (y) 轴配置参数

        Args:
            plot_index (int, optional): 所属区块. Defaults to 0.
            value_axis_id (int, optional): 左侧第一个Y轴. Defaults to -1.
            max_tick_num (int, optional): 最大刻度标签数. Defaults to 6.
            steps (float, optional): 刻度固定间隔. Defaults to -1.0.
            format (str, optional): 标签格式化. Defaults to ''.
            label_text_len (int, optional): 标签最大数字宽度. Defaults to 6.
            valid_mul (float, optional): 有效倍数. Defaults to -1.0.
            price_tick (float, optional): 最小刻度变动值. Defaults to 1.0.
            max_value (float, optional): 最大有效值. Defaults to 9999999.99.
            min_value (float, optional): 最小有效值. Defaults to -9999999.99.

        """
        super().__init__(ValueAxisParamDataPacker(self))

        self._PlotIndex: int = plot_index
        self._ValueAxisID: int = value_axis_id
        self._MaxTickNum: int = max_tick_num
        self._Steps: float = steps
        self._Format: str = format
        self._LabelTextLen: int = label_text_len
        self._ValidMul: float = valid_mul
        self._PriceTick: float = price_tick
        self._MaxValue: float = max_value
        self._MinValue: float = min_value

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
    def MaxTickNum(self):
        return self._MaxTickNum

    @MaxTickNum.setter
    def MaxTickNum(self, value: int):
        self._MaxTickNum = value

    @property
    def Steps(self):
        return self._Steps

    @Steps.setter
    def Steps(self, value: float):
        self._Steps = value

    @property
    def Format(self):
        return self._Format

    @Format.setter
    def Format(self, value: str):
        self._Format = value

    @property
    def LabelTextLen(self):
        return self._LabelTextLen

    @LabelTextLen.setter
    def LabelTextLen(self, value: int):
        self._LabelTextLen = value

    @property
    def ValidMul(self):
        return self._ValidMul

    @ValidMul.setter
    def ValidMul(self, value: float):
        self._ValidMul = value

    @property
    def PriceTick(self):
        return self._PriceTick

    @PriceTick.setter
    def PriceTick(self, value: float):
        self._PriceTick = value

    @property
    def MaxValue(self):
        return self._MaxValue

    @MaxValue.setter
    def MaxValue(self, value: float):
        self._MaxValue = value

    @property
    def MinValue(self):
        return self._MinValue

    @MinValue.setter
    def MinValue(self, value: float):
        self._MinValue = value
