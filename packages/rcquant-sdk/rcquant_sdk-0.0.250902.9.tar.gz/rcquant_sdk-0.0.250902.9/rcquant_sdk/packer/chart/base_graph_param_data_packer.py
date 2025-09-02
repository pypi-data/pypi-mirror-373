from ...interface import IPacker


class BaseGraphParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return (str(self._obj.ID), str(self._obj.Name), int(self._obj.PlotIndex), int(self._obj.ValueAxisID),
                bool(self._obj.Visible), self._obj.UserData)

    def tuple_to_obj(self, t):
        if len(t) >= 6:
            self._obj.ID = t[0]
            self._obj.Name = t[1]
            self._obj.PlotIndex = t[2]
            self._obj.ValueAxisID = t[3]
            self._obj.Visible = t[4]
            self._obj.UserData = t[5]

            return True
        return False
