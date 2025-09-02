from ...interface import IData
from ...packer.chart.graph_value_data_packer import GraphValueDataPacker


class GraphValueData(IData):
    def __init__(self, graph_id: str = '', key: float = 0.0, mill_ts: int = -1, value: float = 0.0):
        """图数据

        Args:
            graph_id (str, optional): 图唯一编码. Defaults to ''.
            key (float, optional): 数值格式的X值. Defaults to 0.0.
            mill_ts (int, optional): 时间戳格式的X值. Defaults to -1.
            value (float, optional): Y值. Defaults to 0.0.
        """
        super().__init__(GraphValueDataPacker(self))
        self._GraphID = graph_id
        self._Key = key
        self._MillTimeSpan = mill_ts
        self._Value = value

    @property
    def GraphID(self):
        return self._GraphID

    @GraphID.setter
    def GraphID(self, value):
        self._GraphID = str(value)

    @property
    def Key(self):
        return self._Key

    @Key.setter
    def Key(self, value):
        self._Key = float(value)

    @property
    def MillTimeSpan(self):
        return self._MillTimeSpan

    @MillTimeSpan.setter
    def MillTimeSpan(self, value):
        self._MillTimeSpan = int(value)

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, value):
        self._Value = float(value)
