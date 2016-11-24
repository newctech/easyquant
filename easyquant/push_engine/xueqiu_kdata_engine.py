# coding: utf-8

import easyquotation
import time
import datetime

from .base_engine import BaseEngine
from easyquant.event_engine import Event

class XueqiuKdataEngine(BaseEngine):
    """雪球k线行情推送引擎"""
    EventType = 'kdata'
    PushInterval = 5

    def init(self):
        self.source = easyquotation.use('xq')
        self.pause = 0.001

    def fetch_quotation(self):
        yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
        yest_time = yesterday.strftime('%Y-%m-%d') + ' 15:00:00'
        today_time = time.strftime('%Y-%m-%d',time.localtime(time.time())) + ' 15:00:00'
        return self.source.get_k_data(self.stocks, yest_time, today_time)

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
