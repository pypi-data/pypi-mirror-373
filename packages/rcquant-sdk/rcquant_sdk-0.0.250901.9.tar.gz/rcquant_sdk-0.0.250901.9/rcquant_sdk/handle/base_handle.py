from typing import Tuple, Optional
from .req_rsp import ReqRspDict, ReqRsp
from ..interface import IData, MsgID
from ..tsocket import TSocket
from ..data.message_data import MessageData
from ..data.login_data import LoginData


class BaseHandle():
    def __init__(self, tsocket: TSocket):
        self.__ReqID: int = 0
        self.__ReqRspDict: ReqRspDict = ReqRspDict()
        self.__TSocket = tsocket
        self.__TSocket.set_base_callback(self.__recv_msg)

    def login(self, login_data: LoginData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Base_Login.value), login_data)

    def __send_heart(self):
        msg = MessageData(mid=int(MsgID.MSGID_Base_Heart.value))
        self.__TSocket.send_message(msg)

    def __recv_msg(self, msg: MessageData):
        if msg.MID == int(MsgID.MSGID_Base_Heart.value):
            self.__send_heart()
            return
        elif msg.MID == int(MsgID.MSGID_Base_SessionInit.value):
            return

        key = '%s_%s' % (msg.MID, msg.RequestID)
        reqrsp: Optional[ReqRsp] = self.__ReqRspDict.get_reqrsp(key)
        if reqrsp is not None:
            reqrsp.append_rsp(msg)

    def __wait_send_msg(self, mid, params: IData):
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
            return (False, '发送超时')

        ret = (rsp.RspSuccess, rsp.RspMsg)
        self.__ReqRspDict.remove(key)
        return ret
