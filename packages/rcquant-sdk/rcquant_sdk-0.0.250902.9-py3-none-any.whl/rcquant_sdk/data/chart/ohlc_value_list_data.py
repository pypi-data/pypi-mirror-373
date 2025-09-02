from typing import List
from ...interface import IData
from ..market.ohlc_data import OHLCData
from ...packer.chart.ohlc_value_list_data_packer import OHLCValueListDataPacker
from ..chart.ohlc_value_data import OHLCValueData


class OHLCValueListData(IData):
    def __init__(self, ohlc_value_list: List[OHLCValueData]):
        super().__init__(OHLCValueListDataPacker(self))
        self._OHLCList: List[OHLCValueData] = ohlc_value_list

    @property
    def OHLCList(self):
        return self._OHLCList

    @OHLCList.setter
    def OHLCList(self, value: List[OHLCValueData]):
        self._OHLCList = value
