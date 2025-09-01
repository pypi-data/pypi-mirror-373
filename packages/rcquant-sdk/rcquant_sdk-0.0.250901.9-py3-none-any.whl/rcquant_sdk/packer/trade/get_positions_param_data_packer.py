from ...interface import IPacker
from ...data.trade.position_data import PositionData
from typing import Tuple


class GetPositionsParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        order_data_list = []
        for od in self._obj.DataList:
            order_data_list.append(od.obj_to_tuple())
        return (str(self._obj.TradeName), str(self._obj.ExchangeID), str(self._obj.InstrumentID), order_data_list)

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 4:
            self._obj.TradeName = t[0]
            self._obj.ExchangeID = t[1]
            self._obj.InstrumentID = t[2]
            for t in t[3]:
                od = PositionData()
                od.tuple_to_obj(t)
                self._obj.DataList.append(od)

            return True
        return False
