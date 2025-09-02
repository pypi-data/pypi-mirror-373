from ...interface import IData
from ...packer.chart.select_rect_param_data_packer import SelectRectParamDataPacker


class SelectRectParamData(IData):
    def __init__(self, chartid: str = '', plot_index: int = 0,
                 action_key: str = '', x_min: float = 0.0, x_max: float = 0.0,):
        super().__init__(SelectRectParamDataPacker(self))
        self._ChartID: str = chartid
        self._PlotIndex: int = plot_index
        self._ActionKey: str = action_key
        self._XMin: float = x_min
        self._XMax: float = x_max
        self._GraphParams = []

    @property
    def ChartID(self):
        return self._ChartID

    @ChartID.setter
    def ChartID(self, value: str):
        self._ChartID = value

    @property
    def PlotIndex(self):
        return self._PlotIndex

    @PlotIndex.setter
    def PlotIndex(self, value: int):
        self._PlotIndex = value

    @property
    def ActionKey(self):
        return self._ActionKey

    @ActionKey.setter
    def ActionKey(self, value: str):
        self._ActionKey = value

    @property
    def XMin(self):
        return self._XMin

    @XMin.setter
    def XMin(self, value: float):
        self._XMin = value

    @property
    def XMax(self):
        return self._XMax

    @XMax.setter
    def XMax(self, value: float):
        self._XMax = value

    @property
    def GraphParams(self):
        return self._GraphParams

    @GraphParams.setter
    def GraphParams(self, value):
        self._GraphParams = value
