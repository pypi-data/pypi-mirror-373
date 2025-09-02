from typing import List, Dict, Tuple, Optional
import datetime
from .req_rsp import ReqRspDict, ReqRsp
from ..interface import IData, MsgID
from ..tsocket import TSocket
from ..data.message_data import MessageData
from ..data.chart.chart_init_param_data import ChartInitParamData
from ..data.chart.line_graph_param_data import LineGraphParamData
from ..data.chart.financial_graph_param_data import FinancialGraphParamData
from ..data.chart.text_graph_param_data import TextGraphParamData
from ..data.chart.marker_graph_param_data import MarkerGraphParamData
from ..data.chart.ohlc_value_list_data import OHLCValueListData
from ..data.chart.ohlc_value_data import OHLCValueData
from ..data.chart.graph_value_list_data import GraphValueListData
from ..data.chart.graph_value_data import GraphValueData
from ..data.chart.bar_graph_param_data import BarGraphParamData
from ..data.chart.time_span_gvlist_data import TimeSpanGVListData
from ..data.chart.select_rect_param_data import SelectRectParamData


class ChartHandle():
    def __init__(self, tsocket: TSocket):
        self.__ReqID: int = 0
        self.__ReqRspDict: ReqRspDict = ReqRspDict()
        self.__TSocket = tsocket
        self.__TSocket.set_chart_callback(self.__recv_msg)

    def set_callback(self, **kwargs):
        if kwargs is None:
            return
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_chart_init_params(self, params: ChartInitParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_Set_Init_Param.value), params)

    def add_line_graph(self, params: LineGraphParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_AddLineGraph.value), params)

    def add_bar_graph(self, params: BarGraphParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_AddBarGraph.value), params)

    def add_financial_graph(self, params: FinancialGraphParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_AddFinancialGraph.value), params)

    def add_marker_graph(self, param: MarkerGraphParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_AddMarkerGraph.value), param)

    def add_text_graph(self, params: TextGraphParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_AddTextGraph.value), params)

    def chart_init_show(self) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_Init_Show.value), None)

    def add_graph_value(self, gvd: GraphValueData) -> Tuple[bool, str]:
        return self.__only_send_msg(int(MsgID.Chart_AddGraphValue.value), gvd)

    def add_ohlc_value(self, ovd: OHLCValueData) -> Tuple[bool, str]:
        return self.__only_send_msg(int(MsgID.Chart_AddOHLCValue.value), ovd)

    def save_chart_data(self, filename: str) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_SaveChartData.value), filename)

    def load_chart_data(self, filename: str) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.Chart_LoadChartData.value), filename)

    def add_graph_value_list(self, gv_value_list: List[GraphValueData]) -> Tuple[bool, str]:
        data = GraphValueListData(gv_list=gv_value_list)
        return self.__only_send_msg(int(MsgID.Chart_AddGraphValueList.value), data)

    def add_timespan_graphvalue_list(self, timespans: List[int], graphvalues: Dict[str, List[float]] = {},
                                     ohlcvalues: Dict[str, Tuple[List[float], List[float], List[float], List[float]]] = {}) -> Tuple[bool, str]:
        data = TimeSpanGVListData(time_spans=timespans, graph_values=graphvalues, ohlc_values=ohlcvalues)
        return self.__only_send_msg(int(MsgID.Chart_AddTimeSpanGVList.value), data)

    def add_ohlc_value_list(self, ohlc_value_list: List[OHLCValueData]) -> Tuple[bool, str]:
        data = OHLCValueListData(ohlc_value_list=ohlc_value_list)
        return self.__only_send_msg(int(MsgID.Chart_AddOHLCValueList.value), data)

    def __notify_on_select_rect(self, msg: MessageData):
        has_select_rect = hasattr(self, 'on_select_rect')
        if has_select_rect is False:
            print('未定义任何on_select_rect回调方法')
            return
        t = SelectRectParamData()
        if t.un_pack(msg.UData) is True:
            self.on_select_rect(t)  # type: ignore

    def __only_send_msg(self, mid, params: IData,) -> Tuple[bool, str]:
        self.__ReqID = self.__ReqID + 1
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()  # type: ignore

        if self.__TSocket.send_message(msg) is False:
            return (False, '发送失败')

        return (True, '发送成功')

    def __recv_msg(self, msg: MessageData):
        if msg.MID == int(MsgID.Chart_SelectRect.value):
            self.__notify_on_select_rect(msg)
            return

        key = '%s_%s' % (msg.MID, msg.RequestID)
        reqrsp: Optional[ReqRsp] = self.__ReqRspDict.get_reqrsp(key)
        if reqrsp is not None:
            reqrsp.append_rsp(msg)

    def __wait_send_msg(self, mid, params) -> Tuple[bool, str]:
        self.__ReqID = self.__ReqID + 1
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            if isinstance(params, IData):
                msg.UData = params.pack()  # type: ignore
            elif isinstance(params, str):
                msg.UData = bytes(params, 'utf-8')

        key = '%s_%s' % (mid, self.__ReqID)

        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return (False, '发送命令失败')

        rsp = req_rsp.wait_last_rsp(30)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return (False, '发送超时')

        ret = (rsp.RspSuccess, rsp.RspMsg)
        self.__ReqRspDict.remove(key)
        return ret
