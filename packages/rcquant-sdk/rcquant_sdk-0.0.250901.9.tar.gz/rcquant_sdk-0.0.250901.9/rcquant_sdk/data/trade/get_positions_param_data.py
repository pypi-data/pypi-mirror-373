from typing import List
from ...interface import IData
from .position_data import PositionData
from ...packer.trade.get_positions_param_data_packer import GetPositionsParamDataPacker


class GetPositionsParamData(IData):
    def __init__(self, trade_name: str = '', exchange_id: str = '', instrument_id: str = ''):
        super().__init__(GetPositionsParamDataPacker(self))
        self._TradeName = trade_name
        self._ExchangeID = exchange_id
        self._InstrumentID = instrument_id
        self._DataList: List[PositionData] = []

    @property
    def TradeName(self):
        return self._TradeName

    @TradeName.setter
    def TradeName(self, value: str):
        self._TradeName = value

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[PositionData]):
        self._DataList: List[PositionData] = value
