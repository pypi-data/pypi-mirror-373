from typing import List
from ...interface import IData
from ...packer.trade.read_ins_date_range_data_packer import ReadInsDateRangeDataPacker


class ReadInsDateRangeData(IData):
    def __init__(self, instrument_id: str = '', period: str = '', start_date: int = 0, end_date: int = 99999999):
        super().__init__(ReadInsDateRangeDataPacker(self))
        self._InstrumentID: str = instrument_id
        self._Period: str = period
        self._StartDate: int = start_date
        self._EndDate: int = end_date
        self._RangeBegin: str = ''
        self._RangeEnd: str = ''

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
    def RangeBegin(self):
        return self._RangeBegin

    @RangeBegin.setter
    def RangeBegin(self, value: str):
        self._RangeBegin = value

    @property
    def RangeEnd(self):
        return self._RangeEnd

    @RangeEnd.setter
    def RangeEnd(self, value: str):
        self._RangeEnd = value
