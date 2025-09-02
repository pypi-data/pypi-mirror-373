from abc import abstractmethod
from enum import Enum
import msgpack
from typing import Tuple, Any


class MsgID(Enum):
    MSGID_Base_Heart = 1000
    MSGID_Base_SessionInit = 1001
    MSGID_Base_Login = 1002

    MSGID_Market_SetParams = 200001
    MSGID_Market_Open = 200002
    MSGID_Market_Close = 200003
    MSGID_Market_Sub = 200004
    MSGID_Market_UnSub = 200005
    MSGID_Market_Tick = 200006
    MSGID_Market_OHLC = 200007
    MSGID_Market_SubOHLC = 200008
    MSGID_Market_UnSubOHLC = 200009
    MSGID_Market_GetHistoryOHLC = 200010
    MSGID_Market_SaveOHLC = 200011
    MSGID_Market_SaveOHLCList = 200012
    MSGID_Market_SaveTickList = 200013
    MSGID_Market_GetHistoryTick = 200014
    MSGID_Market_FinSaveOHLCList = 200015
    MSGID_Market_FinReadOHLCList = 200016
    MSGID_Market_FinSaveTickList = 200017
    MSGID_Market_FinReadTickList = 200018
    MSGID_Market_FinSaveDayList = 200019
    MSGID_Market_FinReadDayList = 200020
    MSGID_Market_FinDeleteList = 200021

    Trade_SetParams = 300010
    Trade_Open = 300011
    Trade_Close = 300012
    Trade_Inited = 300013
    Trade_InsertOrder = 300021
    Trade_CancelOrder = 300022
    Trade_OrderUpdate = 300023
    Trade_TradeOrderUpdate = 300024
    Trade_QueryOrders = 300025
    Trade_QueryTradeOrders = 300026
    Trade_ReadHistoryOrders = 300100
    Trade_ReadHistoryTradeOrders = 300101
    Trade_ReadExcProducts = 300102
    Trade_GetOrders = 300201
    Trade_GetTradeOrders = 300202
    Trade_GetPositions = 300203
    Trade_GetAccount = 300204

    Chart_Set_Init_Param = 400000
    Chart_Set_Chart_Param = 400001
    Chart_Init_Show = 400002
    Chart_AddLineGraph = 400011
    Chart_AddFinancialGraph = 400012
    Chart_AddTextGraph = 400013
    Chart_AddMarkerGraph = 400014
    Chart_AddBarGraph = 400015
    Chart_AddGraphValue = 400026
    Chart_AddOHLCValue = 400027
    Chart_AddOHLCValueList = 400028
    Chart_AddGraphValueList = 400029
    Chart_AddTimeSpanGVList = 400030
    Chart_SaveChartData = 400031
    Chart_LoadChartData = 400032
    Chart_SelectRect = 400033

    FinData_FinSaveOHLCList = 500001
    FinData_FinReadOHLCList = 500002
    FinData_FinSaveTickList = 500003
    FinData_FinReadTickList = 500004
    FinData_FinSaveDayList = 500005
    FinData_FinReadDayList = 500006
    FinData_FinDeleteList = 500007
    FinData_ReadExcProducts = 500008
    FinData_FinReadInstrument = 500009
    FinData_FinSaveInstrument = 500010
    FinData_FinReadDBList = 500011
    FinData_FinDeleteInstrument = 500012
    FinData_FinReadPeriods = 500013
    FinData_FinDBVacuum = 500014
    FinData_FinReadInsDateRange = 500015
    FinData_FinSaveFinancial = 500016
    FinData_FinReadFinancial = 500017
    FinData_FinDeleteFinancial = 500018


class IPacker(object):
    def __init__(self, obj) -> None:
        super().__init__()
        self._obj = obj
        if self._obj is None:
            raise Exception("packer data is none")

    def pack(self):
        return msgpack.packb(self.obj_to_tuple())

    @abstractmethod
    def obj_to_tuple(self) -> Tuple[Any, ...]:
        return ()

    def un_pack(self, data_bytes):
        try:
            t = msgpack.unpackb(data_bytes)
            return self.tuple_to_obj(t)
        except Exception as e:
            print(e)
            return False

    @abstractmethod
    def tuple_to_obj(self, t) -> bool:
        return False


class IData(object):
    def __init__(self, packer: IPacker) -> None:
        super().__init__()
        self.__packer = packer

    def pack(self):
        return self.__packer.pack()

    def obj_to_tuple(self):
        return self.__packer.obj_to_tuple()

    def un_pack(self, bytes_data):
        return self.__packer.un_pack(bytes_data)

    def tuple_to_obj(self, t):
        self.__packer.tuple_to_obj(t)
