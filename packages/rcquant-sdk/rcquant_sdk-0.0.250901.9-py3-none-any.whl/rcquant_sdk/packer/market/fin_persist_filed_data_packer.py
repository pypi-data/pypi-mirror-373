from ...interface import IPacker


class FinPersistFiledDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (int(self._obj.Day), str(self._obj.Mark), int(self._obj.Offset), bytes(self._obj.Buffer))

    def tuple_to_obj(self, t):
        if len(t) >= 4:
            self._obj.Day = t[0]
            self._obj.Mark = t[1]
            self._obj.Offset = t[2]
            self._obj.Buffer = t[3]

            return True
        return False
