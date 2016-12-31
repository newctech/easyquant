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
        self.source = easyquotation.use('xq')
        self.pause = 0.001

    def fetch_quotation(self):
        return self.source.get_general_data(self.stocks)

    def push_quotation(self):
        while self.is_active:
            try:
                self.stocks = self.feedback_queue.get(block=True, timeout=1)
                response_lists = self.fetch_quotation()
            except Empty:
                continue
            for response in response_lists:
                event = Event(event_type=self.EventType, data=response)
                self.event_engine.put(event)
                time.sleep(self.pause)
