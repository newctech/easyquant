# coding: utf-8

import easyquotation
import time

from .base_engine import BaseEngine


class XueqiuRealtimeEngine(BaseEngine):
    """雪球分时行情推送引擎"""
    EventType = 'realtime'

    def init(self):
        self.source = easyquotation.use('xq')
        self.pause = 0.001

    def fetch_quotation(self):
        return self.source.get_realtime_data('XXXXXXX')

    def push_quotation(self):
        while self.is_active:
            try:
                response_lists = self.fetch_quotation()
            except:
                self.wait()
                continue
            for response in response_lists:
                event = Event(event_type=self.EventType, data=response)
                self.event_engine.put(event)
                time.sleep(self.pause)
            self.wait()
