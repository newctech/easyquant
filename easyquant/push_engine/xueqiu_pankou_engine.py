# coding: utf-8

import easyquotation

from .base_engine import BaseEngine


class XueqiuPankouEngine(BaseEngine):
    """雪球盘口行情推送引擎"""
    EventType = 'pankou'

    def init(self):
        self.source = easyquotation.use('xq')

    def fetch_quotation(self):
        return self.source.get_pankou_data('XXXXXXX')
