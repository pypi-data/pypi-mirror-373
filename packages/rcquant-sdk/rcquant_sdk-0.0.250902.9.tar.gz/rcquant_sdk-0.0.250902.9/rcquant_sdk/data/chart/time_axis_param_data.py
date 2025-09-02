from ...interface import IData
from ...packer.chart.time_axis_param_data_packer import TimeAxisParamDataPacker


class TimeAxisParamData(IData):
    def __init__(self, show_labels: str = '', format: str = ''):
        """时间轴配置参数

        Args:
            show_labels (str, optional): x轴显示的标签例如 09:00:00;15:00:00 表示时间标签只显示9点和15点. Defaults to ''.
            format (str, optional): 时间显示格式. Defaults to ''.
        """
        super().__init__(TimeAxisParamDataPacker(self))
        self._ShowLabels: str = show_labels
        self._Format: str = format

    @property
    def ShowLabels(self):
        return self._ShowLabels

    @ShowLabels.setter
    def ShowLabels(self, value: str):
        self._ShowLabels = value

    @property
    def Format(self):
        return self._Format

    @Format.setter
    def Format(self, value: str):
        self._Format = value
