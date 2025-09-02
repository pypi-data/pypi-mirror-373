from typing import Tuple, Optional, Union
from .req_rsp import ReqRspDict, ReqRsp
from ..interface import IData, MsgID
from ..tsocket import TSocket
from ..data.message_data import MessageData
from ..listener import IListener
from ..data.trade.order_data import OrderData
from ..data.trade.tradeorder_data import TradeOrderData
from ..data.trade.read_history_order_param_data import ReadHistoryOrderParamData
from ..data.trade.read_history_tradeorder_param_data import ReadHistoryTradeOrderParamData
from ..data.trade.trade_param_data import TradeParamData
from ..data.trade.get_account_param_data import GetAccountParamData
from ..data.trade.get_orders_param_data import GetOrdersParamData
from ..data.trade.get_tradeorders_param_data import GetTradeOrdersParamData
from ..data.trade.get_positions_param_data import GetPositionsParamData
from ..data.trade.read_exc_product_param_data import ReadExcProductParamData
import numpy as np
import pandas as pd


class TradeHandle():
    def __init__(self, tsocket: TSocket):
        self.__ReqID: int = 0
        self.__Listener: Optional[IListener] = None
        self.__ReqRspDict: ReqRspDict = ReqRspDict()
        self.__TSocket = tsocket
        self.__TSocket.set_trade_callback(self.__recv_msg)
        self.__ExcProduct_Columns_Types = {"ExchangeID": str, "ProductID": str, "ProductName": str,
                                           "VolumeMultiple": np.float32, "PriceTick": np.float32,
                                           "MaxMarketOrderVolume": np.int32, "MaxLimitOrderVolume": np.int32, "Times": {}}
        self.__ExcProductTime_Columns_Types = {"StartTime": str, "EndTime": str, "AddDay": np.int32, "InstrumentStatusKind": np.int32}

    def __del__(self):
        self.__TSocket.set_trade_callback(None)

    def set_callback(self, **kwargs):
        if kwargs is None:
            return
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_listener(self, listener: IListener):
        self.__Listener = listener

    def set_trade_params(self, params: TradeParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Trade_SetParams.value), params)

    def insert_order(self, order: OrderData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Trade_InsertOrder.value), order)

    def cancel_order(self, order: OrderData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Trade_CancelOrder.value), order)

    def get_orders(self, params: GetOrdersParamData) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        return self.wait_read_datas(int(MsgID.Trade_GetOrders.value), params, '读取委托单', self.__unpack_get_order_list)

    def get_tradeorders(self, params: GetTradeOrdersParamData) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        return self.wait_read_datas(int(MsgID.Trade_GetTradeOrders.value), params, '读取成交单', self.__unpack_get_tradeorder_list)

    def get_positions(self, params: GetPositionsParamData) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        return self.wait_read_datas(int(MsgID.Trade_GetPositions.value), params, '读取持仓单', self.__unpack_position_list)

    def get_account(self, params: GetAccountParamData):
        return self.wait_read_datas(int(MsgID.Trade_GetAccount.value), params, '读取账户', self.__unpack_account_list)

    def read_history_orders(self, params: ReadHistoryOrderParamData) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        return self.wait_read_datas(int(MsgID.Trade_ReadHistoryOrders.value), params, '读取历史委托单', self.__unpack_order_list)

    def read_exc_products(self, params: ReadExcProductParamData) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        return self.wait_read_datas(int(MsgID.Trade_ReadExcProducts.value), params, '读取品种信息', self.__unpack_excproduct_list)

    def read_history_tradeorders(self, params: ReadHistoryTradeOrderParamData) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        return self.wait_read_datas(int(MsgID.Trade_ReadHistoryTradeOrders.value), params, '读取历史成交单', self.__unpack_tradeorder_list)

    def __notify_order_update(self, msg: MessageData):
        hason = hasattr(self, 'on_order_update')
        if hason is False and self.__Listener is None:
            print('未定义任何on_order_update回调方法')
            return
        order = OrderData()
        if order.un_pack(msg.UData) is True:
            if hason is True:
                self.on_order_update(order)  # type: ignore
            if self.__Listener is not None:
                self.__Listener.on_order_update(order)

    def __notify_tradeorder_update(self, msg: MessageData):
        hason = hasattr(self, 'on_tradeorder_update')
        if hason is False and self.__Listener is None:
            print('未定义任何on_tradeorder_update回调方法')
            return
        tradeorder = TradeOrderData()
        if tradeorder.un_pack(msg.UData) is True:
            if hason is True:
                self.on_tradeorder_update(tradeorder)  # type: ignore
            if self.__Listener is not None:
                self.__Listener.on_tradeorder_update(tradeorder)

    def __unpack_get_order_list(self, reqrsp: ReqRsp) -> list:
        os = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams = GetOrdersParamData()
                if rspparams.un_pack(r.UData) is False:
                    continue
                for ot in rspparams.DataList:
                    os.append(ot)
        return os

    def __unpack_get_tradeorder_list(self, reqrsp: ReqRsp):
        os = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams = GetTradeOrdersParamData()
                if rspparams.un_pack(r.UData) is False:
                    continue
                for ot in rspparams.DataList:
                    os.append(ot)
        return os

    def __unpack_order_list(self, reqrsp: ReqRsp):
        os = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams = ReadHistoryOrderParamData()
                if rspparams.un_pack(r.UData) is False:
                    continue
                for ot in rspparams.DataList:
                    os.append(ot)
        return os

    def __unpack_tradeorder_list(self, reqrsp: ReqRsp):
        os = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams = ReadHistoryTradeOrderParamData()
                rspparams.un_pack(r.UData)
                for ot in rspparams.DataList:
                    os.append(ot)
        return os

    def __unpack_excproduct_list(self, reqrsp: ReqRsp):
        os = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams = ReadExcProductParamData()
                rspparams.un_pack(r.UData)
                for ot in rspparams.DataList:
                    if len(ot) >= 7 and isinstance(ot[7], list):
                        df_pts = pd.DataFrame(ot[7], columns=list(self.__ExcProductTime_Columns_Types.keys()))
                        ot[7] = df_pts
                    os.append(ot)
        df = pd.DataFrame(os, columns=list(self.__ExcProduct_Columns_Types.keys()))
        return df

    def __unpack_position_list(self, reqrsp: ReqRsp):
        ps = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams = GetPositionsParamData()
                rspparams.un_pack(r.UData)
                for ot in rspparams.DataList:
                    ps.append(ot)
        return ps

    def __unpack_account_list(self, reqrsp: ReqRsp):
        rsp_last = reqrsp.get_rsp_last()
        if rsp_last is not None and len(rsp_last.UData) > 0:
            acc = GetAccountParamData()
            acc.un_pack(rsp_last.UData)
            return acc.Account

        return None

    def wait_read_datas(self, mid, params: IData, fun_name: str, unpack_func) -> Tuple[bool, str, Union[list, pd.DataFrame, None]]:
        self.__ReqID = self.__ReqID + 1
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()  # type: ignore

        key = '%s_%s' % (mid, self.__ReqID)
        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return (False, '发送%s失败' % fun_name, None)

        rsp = req_rsp.wait_last_rsp(10)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return (False, '获取%s数据超时' % fun_name, None)

        return (True, '%s读取成功' % fun_name, unpack_func(req_rsp))

    def __recv_msg(self, msg: MessageData):
        if msg.MID == int(MsgID.Trade_OrderUpdate.value):
            self.__notify_order_update(msg)
            return

        elif msg.MID == int(MsgID.Trade_TradeOrderUpdate.value):
            self.__notify_tradeorder_update(msg)
            return

        key = '%s_%s' % (msg.MID, msg.RequestID)
        reqrsp: Optional[ReqRsp] = self.__ReqRspDict.get_reqrsp(key)
        if reqrsp is not None:
            reqrsp.append_rsp(msg)

    def __wait_send_msg(self, mid, params: IData) -> Tuple[bool, str]:
        self.__ReqID = self.__ReqID + 1
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()  # type: ignore

        key = '%s_%s' % (mid, self.__ReqID)

        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return (False, '发送命令失败')

        rsp = req_rsp.wait_last_rsp(10)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return (False, '发送命令超时')
        return (rsp.RspSuccess, rsp.RspMsg)
