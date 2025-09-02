from typing import List
from ...interface import IData
from ...packer.market.fin_persist_save_param_data_packer import FinPersistSaveParamDataPacker
from .fin_persist_filed_data import FinPersistFiledData


class FinPersistSaveParamData(IData):
    def __init__(self, instrument_id: str = '', period: str = '',
                 append: bool = False, vacuum: bool = False,
                 base_path: str = '', type_mark: str = "MarketData"):
        super().__init__(FinPersistSaveParamDataPacker(self))
        self._InstrumentID: str = instrument_id
        self._Period: str = period
        self._Fileds: List[FinPersistFiledData] = []
        self._Append: bool = append
        self._Vacuum: bool = vacuum
        self._BasePath: str = base_path
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
    def Fileds(self):
        return self._Fileds

    @Fileds.setter
    def Fileds(self, value: List[FinPersistFiledData]):
        self._Fileds = value

    @property
    def Append(self):
        return self._Append

    @Append.setter
    def Append(self, value: bool):
        self._Append = value

    @property
    def Vacuum(self):
        return self._Vacuum

    @Vacuum.setter
    def Vacuum(self, value: bool):
        self._Vacuum = value

    @property
    def BasePath(self):
        return self._BasePath

    @BasePath.setter
    def BasePath(self, value: str):
        self._BasePath = value

    @property
    def TypeMark(self):
        return self._TypeMark

    @TypeMark.setter
    def TypeMark(self, value: str):
        self._TypeMark = value
