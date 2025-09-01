from typing import Optional
from ...interface import IData
from ..market.ohlc_data import OHLCData
from ...packer.chart.ohlc_value_data_packer import OHLCValueDataPacker


class OHLCValueData(IData):
    def __init__(self, graph_id: str = '', ohlc_data: Optional[OHLCData] = None):
        super().__init__(OHLCValueDataPacker(self))
        self._GraphID: str = graph_id
        self._OHLC: Optional[OHLCData] = ohlc_data

    @property
    def GraphID(self):
        return self._GraphID

    @GraphID.setter
    def GraphID(self, value: str):
        self._GraphID = value

    @property
    def OHLC(self):
        return self._OHLC

    @OHLC.setter
    def OHLC(self, value: OHLCData):
        self._OHLC = value
