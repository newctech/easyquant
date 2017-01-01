# coding: utf-8

import easyquotation
import time
from queue import Queue, Empty

from .base_engine import BaseEngine
from easyquant.event_engine import Event

class XueqiuFeedbackEngine(BaseEngine):
    """雪球股票概要行情反馈推送引擎"""
    EventType = 'feedback'

    def init(self):
        self.source_xq = easyquotation.use('xq')
        self.source_mysina = easyquotation.use('mysina')
        self.pause = 0.001

    def fetch_quotation(self):
        res_dict = {}
        res_dict['xueqiu_general'] = self.source_xq.get_general_data(self.stocks)[-1]
        res_dict['xueqiu_realtime'] = self.source_xq.get_realtime_data(self.stocks)[-1]
        res_dict['mysina_dadan'] = self.source_mysina.get_dadan_data(self.stocks, volume='40000')
        return res_dict

    def push_quotation(self):
        while self.is_active:
            try:
                self.stocks = self.feedback_queue.get(block=True, timeout=1)
                response = self.fetch_quotation()
            except Empty:
                continue
            event = Event(event_type=self.EventType, data=response)
            self.event_engine.put(event)
            time.sleep(self.pause)
