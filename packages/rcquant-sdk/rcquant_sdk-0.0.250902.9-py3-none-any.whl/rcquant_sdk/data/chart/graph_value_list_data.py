from typing import List
from ...interface import IData
from .graph_value_data import GraphValueData
from ...packer.chart.graph_value_list_data_packer import GraphValueListDataPacker


class GraphValueListData(IData):
    def __init__(self, gv_list: List[GraphValueData]):
        super().__init__(GraphValueListDataPacker(self))
        self._GVList: List[GraphValueData] = gv_list

    @property
    def GVList(self):
        return self._GVList

    @GVList.setter
    def GVList(self, value: List[GraphValueData]):
        self._GVList = value
