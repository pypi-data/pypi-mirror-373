from typing import List, Dict, Tuple
from ...interface import IData
from ...packer.chart.time_span_gvlist_data_packer import TimeSpanGVListDataPacker


class TimeSpanGVListData(IData):
    def __init__(self, time_spans: List[int], graph_values: Dict[str, List[float]] = {},
                 ohlc_values: Dict[str, Tuple[List[float], List[float], List[float], List[float]]] = {}):
        """时间戳图数据

        Args:
            time_spans (List[int]): 时间戳列表
            graph_values (Dict[str, List[float]], optional): 图数据key为图唯一编码,value为值列表. Defaults to {}.
            ohlc_values (Dict[str, Tuple[List[float], List[float], List[float], List[float]]], optional):
            ohlc数据.key为图唯一编码,value 0开盘价列表 1最高价列表 2最低价列表 3收盘价列表 Defaults to {}.
        """
        super().__init__(TimeSpanGVListDataPacker(self))
        if time_spans is None:
            time_spans = []
        self._TimeSpanList: List[int] = time_spans
        if graph_values is None:
            graph_values = {}
        self._GraphValueList: Dict[str, List[float]] = graph_values
        if ohlc_values is None:
            ohlc_values = {}
        self._OHLCValueList: Dict[str, Tuple[List[float], List[float], List[float], List[float]]] = ohlc_values

    @ property
    def TimeSpanList(self):
        return self._TimeSpanList

    @ TimeSpanList.setter
    def TimeSpanList(self, value: List[int]):
        self._TimeSpanList = value

    @ property
    def GraphValueList(self):
        return self._GraphValueList

    @ GraphValueList.setter
    def GraphValueList(self, value: Dict[str, List[float]]):
        self._GraphValueList = value

    @ property
    def OHLCValueList(self):
        return self._OHLCValueList

    @ OHLCValueList.setter
    def OHLCValueList(self, value: Dict[str, Tuple[List[float], List[float], List[float], List[float]]]):
        self._OHLCValueList = value
