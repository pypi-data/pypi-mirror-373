from ...interface import IPacker
from ...data.market.fin_persist_filed_data import FinPersistFiledData


class FinPersistReadParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        tempfileds = []
        for filed in self._obj.DataFileds:
            tempfileds.append(filed.obj_to_tuple())

        return (str(self._obj.InstrumentID), str(self._obj.Period), int(self._obj.StartDate),
                int(self._obj.EndDate), tempfileds, str(self._obj.BasePath),
                bool(self._obj.IsReadByte), str(self._obj.TypeMark))

    def tuple_to_obj(self, t):
        if len(t) >= 8:
            self._obj.InstrumentID = t[0]
            self._obj.Period = t[1]
            self._obj.StartDate = t[2]
            self._obj.EndDate = t[3]
            for temp in t[4]:
                fd = FinPersistFiledData()
                fd.tuple_to_obj(temp)
                self._obj.DataFileds.append(fd)
            self._obj.BathPath = t[5]
            self._obj.IsReadByte = t[6]
            self._obj.TypeMark = t[7]

            return True
        return False
