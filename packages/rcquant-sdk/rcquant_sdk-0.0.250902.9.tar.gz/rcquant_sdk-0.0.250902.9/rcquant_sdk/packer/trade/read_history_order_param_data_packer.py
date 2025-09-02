from ...interface import IPacker
from ...data.trade.order_data import OrderData
from typing import Tuple


class ReadHistoryOrderParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self) -> Tuple:
        order_data_list = []
        for od in self._obj.DataList:
            order_data_list.append(od.obj_to_tuple())
        return (str(self._obj.StartDate), str(self._obj.EndDate), order_data_list)

    def tuple_to_obj(self, t) -> bool:
        if len(t) >= 3:
            self._obj.StartDate = t[0]
            self._obj.EndDate = t[1]
            for t in t[2]:
                od = OrderData()
                od.tuple_to_obj(t)
                self._obj.DataList.append(od)

            return True
        return False
