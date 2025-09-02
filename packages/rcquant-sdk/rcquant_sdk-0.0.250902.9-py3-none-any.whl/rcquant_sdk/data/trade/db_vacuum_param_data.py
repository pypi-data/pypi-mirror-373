from typing import List
from ...interface import IData
from ...packer.trade.db_vacuum_param_data_packer import DBVacuumParamDataPacker


class DBVacuumParamData(IData):
    def __init__(self, instrument_id: List[str] = [], period: List[str] = []):
        super().__init__(DBVacuumParamDataPacker(self))
        self._InstrumentID: List[str] = instrument_id.copy()
        self._Period: List[str] = period.copy()

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: List[str]):
        self._InstrumentID = value

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, value: List[str]):
        self._Period = value
