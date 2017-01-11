# -*- coding: utf-8 -*-
import os
import time
import datetime as dt
from dateutil import tz
#from easyquant import DefaultLogHandler
from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    name = 'storeData'

    def init(self):
        # 通过下面的方式来获取时间戳
        now_dt = self.clock_engine.now_dt
        now = self.clock_engine.now
        now = time.time()

        # 注册时钟间隔事件, 不在交易阶段也会触发, clock_type == minute_interval
        minute_interval = 1.5
        self.clock_engine.register_interval(minute_interval, trading=False)

        self.symbol = 'SH601211'

    def strategy(self, event):
        # 使用 self.user 来操作账户，用法同 easytrader 用法
        # 使用 self.log.info('message') 来打印你所需要的 log
        #print('demo1 的 log 使用自定义 log 的方式记录在 demo1.log')
        #self.log.info('数据存储策略触发')
        if event.event_type == 'pankou':
            self.log.info('StoreData_Pankou: %s' % event.data)
            self.pankou_write_hdf5(event.data)
        elif event.event_type == 'detail':
            self.log.info('StoreData_Detail: %s' % event.data)
            self.detail_write_hdf5(event.data)
        elif event.event_type == 'realtime':
            self.log.info('StoreData_Realtime: %s' % event.data)
            self.realtime_write_hdf5(event.data, self.symbol)
        elif event.event_type == 'general':
            self.log.info('StoreData_General: %s' % event.data)
            self.general_write_hdf5(event.data)

        elif event.event_type == 'all':
        #初始化,可通过引擎客户端,存储行情
        #    for stock in event.data:
        #        symbol_key = stock['stock']['symbol']
        #        for data in stock['chartlist']:
        #            self.kdata_write_hdf5(data, symbol_key)
            self.log.info('StoreData_all: %d' % len(event.data))

    def clock(self, event):
        """在交易时间会定时推送 clock 事件
        :param event: event.data.clock_event 为 [0.5, 1, 3, 5, 15, 30, 60] 单位为分钟,  ['open', 'close'] 为开市、收市
            event.data.trading_state  bool 是否处于交易时间
        """
        if event.data.clock_event == 'open':
            # 开市了
            self.log.info('StoreData_Open')
        elif event.data.clock_event == 'close':
            # 收市了
            self.log.info('StoreData_Close')

        elif event.data.clock_event == 5:
            # 5 分钟的 clock
            self.log.info("StoreData_5min")

#    def log_handler(self):
#        """自定义 log 记录方式"""
#        log = self.name + '.log'
#        return DefaultLogHandler(self.name, log_type='file', filepath=log)

    def shutdown_strategy(self):
        """
        关闭进程前的调用
        :return:
        """
        self.log.info("%s 在关闭前保存了策略数据" % self.name)
