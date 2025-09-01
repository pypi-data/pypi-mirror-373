from typing import Dict, List, Optional
import threading
from ..data.message_data import MessageData


class ReqRspDict():
    def __init__(self):
        self.__Lock = threading.Lock()
        self.__req_rsp_dict: Dict[str, ReqRsp] = {}

    def remove(self, key: str):
        self.__Lock.acquire()
        del self.__req_rsp_dict[key]
        self.__Lock.release()

    def new_reqrsp(self, key: str, req_msg: MessageData):
        self.__Lock.acquire()
        req_rsp = ReqRsp(req_msg)
        self.__req_rsp_dict[key] = req_rsp
        self.__Lock.release()

        return req_rsp

    def get_reqrsp(self, key: str):
        self.__Lock.acquire()
        reqrsp = self.__req_rsp_dict.get(key)
        self.__Lock.release()
        return reqrsp


class ReqRsp():
    def __init__(self, req_msg: MessageData):
        self.__Event = threading.Event()
        self.__req_message: MessageData = req_msg
        self.__rsp_last_msg: Optional[MessageData] = None
        self.__rsp_msg_list: List[MessageData] = []

    def append_rsp(self, rsp_msg: MessageData):
        if rsp_msg.MID != self.__req_message.MID or rsp_msg.RequestID != self.__req_message.RequestID:
            return False

        self.__rsp_msg_list.append(rsp_msg)
        if rsp_msg.IsLast is True:
            self.__rsp_last_msg = rsp_msg
            self.__Event.set()
        return True

    def wait_last_rsp(self, timeout: int):
        self.__Event.wait(timeout)
        self.__Event.clear()
        return self.__rsp_last_msg

    def get_rsp_last(self):
        return self.__rsp_last_msg

    def get_rsp_list(self):
        return self.__rsp_msg_list
