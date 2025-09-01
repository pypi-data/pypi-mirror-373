from typing import List
from ...interface import IData
from ...packer.trade.read_instrument_param_data_packer import ReadInstrumentParamDataPacker
from .instrument_data import InstrumentData


class ReadInstrumentParamData(IData):
    def __init__(self, exchange_id: List[str] = [],
                 instrument_id: List[str] = [],
                 unicode: List[str] = [], like_unicode: str = ''):
        super().__init__(ReadInstrumentParamDataPacker(self))
        self._ExchangeID: List[str] = exchange_id.copy()
        self._InstrumentID: List[str] = instrument_id.copy()
        self._UniCode: List[str] = unicode.copy()
        self._LikeUniCode: str = like_unicode
        self._DataList: List[InstrumentData] = []

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: List[str]):
        self._ExchangeID = value

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: List[str]):
        self._InstrumentID = value

    @property
    def UniCode(self):
        return self._UniCode

    @UniCode.setter
    def UniCode(self, value: List[str]):
        self._UniCode = value

    @property
    def LikeUniCode(self):
        return self._LikeUniCode

    @LikeUniCode.setter
    def LikeUniCode(self, value: str):
        self._LikeUniCode = value

    @property
    def DataList(self):
        return self._DataList

    @DataList.setter
    def DataList(self, value: List[InstrumentData]):
        self._DataList = value
