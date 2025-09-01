from ...interface import IData
from ...packer.market.fin_persist_filed_data_packer import FinPersistFiledDataPacker


class FinPersistFiledData(IData):
    def __init__(self, day: int = 0, mark: str = '', offset: int = 0, buffer: bytes = b''):
        super().__init__(FinPersistFiledDataPacker(self))
        self._Day: int = day
        self._Mark: str = mark
        self._Offset: int = offset
        self._Buffer: bytes = buffer

    @property
    def Day(self):
        return self._Day

    @Day.setter
    def Day(self, value: int):
        self._Day = value

    @property
    def Mark(self):
        return self._Mark

    @Mark.setter
    def Mark(self, value: str):
        self._Mark = value

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, value: int):
        self._Offset = value

    @property
    def Buffer(self):
        return self._Buffer

    @Buffer.setter
    def Buffer(self, value: bytes):
        self._Buffer = value
