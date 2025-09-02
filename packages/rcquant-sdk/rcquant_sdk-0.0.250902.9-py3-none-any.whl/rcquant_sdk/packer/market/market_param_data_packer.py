from ...interface import IPacker


class MarketParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return tuple([str(self._obj.MarketNames)])

    def tuple_to_obj(self, t):
        if len(t) >= 1:
            self._obj.MarketNames = t[0]
            return True
        return False
