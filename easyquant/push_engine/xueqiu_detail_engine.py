# -*- coding: utf-8 -*-

import easyquotation
import time

from .base_engine import BaseEngine
from easyquant.event_engine import Event

class XueqiuDetailEngine(BaseEngine):
    """雪球分笔行情推送引擎"""
    EventType = 'detail'
    PushInterval = 0

    def init(self):
        self.source = easyquotation.use('xq')
        self.pause = 0.2

    def fetch_quotation(self):
        return self.source.get_detail_data(self.stocks)

    def push_quotation(self):
        while self.is_active:
            try:
                response_lists = self.fetch_quotation()
            except:
                self.wait()
                continue
            for index in range(len(response_lists)):
                event = Event(event_type=self.EventType, data=response_lists[-1 - index])
                self.event_engine.put(event)
                time.sleep(self.pause)
            self.wait()
