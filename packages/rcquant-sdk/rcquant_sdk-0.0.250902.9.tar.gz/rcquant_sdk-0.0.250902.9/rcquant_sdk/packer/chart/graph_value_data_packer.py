from ...interface import IPacker


class GraphValueDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.GraphID), float(self._obj.Key), int(self._obj.MillTimeSpan), float(self._obj.Value))

    def tuple_to_obj(self, t):
        if len(t) >= 4:
            self._obj.GraphID = t[0]
            self._obj.Key = t[1]
            self._obj.MillTimeSpan = t[2]
            self._obj.Value = t[3]

            return True
        return False
