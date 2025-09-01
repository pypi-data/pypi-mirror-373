from typing import List, Optional
from ...interface import IData
from ...packer.market.fin_persist_read_param_data_packer import FinPersistReadParamDataPacker
from .fin_persist_filed_data import FinPersistFiledData


class FinPersistReadParamData(IData):
    def __init__(self, instrument_id: str = '', period: str = '',
                 start_date: int = 0, end_date: int = 99999999,
                 base_path: str = '', is_read_byte: bool = False,
                 type_mark: str = "MarketData"):
        super().__init__(FinPersistReadParamDataPacker(self))
        self._InstrumentID: str = instrument_id
        self._Period: str = period
        self._StartDate: int = start_date
        self._EndDate: int = end_date
        self._DataFileds: List[FinPersistFiledData] = []
        self._BasePath: str = base_path
        self._IsReadByte: bool = is_read_byte
        self._TypeMark: str = type_mark

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, value: str):
        self._Period = value

    @property
    def StartDate(self):
        return self._StartDate

    @StartDate.setter
    def StartDate(self, value: int):
        self._StartDate = value

    @property
    def EndDate(self):
        return self._EndDate

    @EndDate.setter
    def EndDate(self, value: int):
        self._EndDate = value

    @property
    def DataFileds(self):
        return self._DataFileds

    @DataFileds.setter
    def DataFileds(self, value: List[FinPersistFiledData]):
        self._DataFileds = value

    @property
    def BasePath(self):
        return self._BasePath

    @BasePath.setter
    def BasePath(self, value: str):
        self._BasePath = value

    @property
    def IsReadByte(self):
        return self._IsReadByte

    @IsReadByte.setter
    def IsReadByte(self, value: bool):
        self._IsReadByte = value

    @property
    def TypeMark(self):
        return self._TypeMark

    @TypeMark.setter
    def TypeMark(self, value: str):
        self._TypeMark = value
