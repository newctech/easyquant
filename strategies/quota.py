import os
import time
import datetime as dt
from dateutil import tz
from easyquant import DefaultLogHandler
from easyquant import StrategyTemplate
import easyquotation


class Strategy(StrategyTemplate):
    name = 'Quota'

    def init(self):
        # 通过下面的方式来获取时间戳
        now_dt = self.clock_engine.now_dt
        now = self.clock_engine.now
        now = time.time()

        # 注册时钟事件
        clock_type = "closing" #尾盘
        moment = dt.time(14, 56, 30, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment)

        # 注册时钟事件
        clock_type = "closed" #存储K线数据
        moment = dt.time(15, 10, 0, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment)

        # 注册时钟间隔事件, 不在交易阶段也会触发, clock_type == minute_interval
        minute_interval = 0.5
        self.clock_engine.register_interval(minute_interval, trading=False)

        self.source = easyquotation.use('xq')
        self.symbol = 'SH601211'

        self.__backups_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) + '/easyquant/config/backups.json'

    def strategy(self, event):
        """:param event event.data 为所有股票的信息，结构如下
        {'162411':
        {'ask1': '0.493',
         'ask1_volume': '75500',
         'ask2': '0.494',
         'ask2_volume': '7699281',
         'ask3': '0.495',
         'ask3_volume': '2262666',
         'ask4': '0.496',
         'ask4_volume': '1579300',
         'ask5': '0.497',
         'ask5_volume': '901600',
         'bid1': '0.492',
         'bid1_volume': '10765200',
         'bid2': '0.491',
         'bid2_volume': '9031600',
         'bid3': '0.490',
         'bid3_volume': '16784100',
         'bid4': '0.489',
         'bid4_volume': '10049000',
         'bid5': '0.488',
         'bid5_volume': '3572800',
         'buy': '0.492',
         'close': '0.499',
         'high': '0.494',
         'low': '0.489',
         'name': '华宝油气',
         'now': '0.493',
         'open': '0.490',
         'sell': '0.493',
         'turnover': '420004912',
         'volume': '206390073.351'}}
        """
        # 使用 self.user 来操作账户，用法同 easytrader 用法
        # 使用 self.log.info('message') 来打印你所需要的 log
        #print('demo1 的 log 使用自定义 log 的方式记录在 demo1.log')
        #self.log.info('数据存储策略触发')
        if event.event_type == 'pankou':
            #self.log.info('quota_Extralarge(: %s' % event.data)
            pass
        elif event.event_type == 'detail':
            if int(event.data['v']) * int(event.data['c']) > 1000000:
                self.set_Extralarge_detail(int(event.data['type']) * int(event.data['v']) + self.get_Extralarge_detail())
            elif 1000000 > int(event.data['v']) * int(event.data['c']) > 500000:
                self.set_Big_detail(int(event.data['type']) * int(event.data['v']) + self.get_Big_detail())
            elif 500000 > int(event.data['v']) * int(event.data['c']) > 40000:
                self.set_Medium_detail(int(event.data['type']) * int(event.data['v']) + self.get_Medium_detail())
            elif 40000 > int(event.data['v']) * int(event.data['c']):
                self.set_Small_detail(int(event.data['type']) * int(event.data['v']) + self.get_Small_detail())

            value = self.get_Extralarge_detail()
            self.log.info('Quota_Extralarge_Detail: %d' % value)
            value = self.get_Big_detail()
            self.log.info('Quota_Big_Detail: %d' % value)
            valuel = self.get_Medium_detail()
            self.log.info('Quota_Medium_Detail: %d' % valuel)
            valuel = self.get_Small_detail()
            self.log.info('Quota_Small_Detail: %d' % valuel)

        elif event.event_type == 'realtime':
            #self.log.info('StoreData_Realtime: %s' % event.data)
            #self.realtime_write_hdf5(event.data, self.symbol)
            pass
        elif event.event_type == 'kdata':
        #    self.log.info('xueqiu_kdata: %s' % event.data)
        #    self.kdata_write_hdf5(event.data, self.symbol)
            pass
        elif event.event_type == 'general':
            #self.log.info('StoreData_General: %s' % event.data)
            #self.general_write_hdf5(event.data)
            pass
        #self.log.info('行情数据: 万科价格: %s' % event.data['000002'])
        #self.log.info('检查持仓')
        #self.log.info(self.user.balance)
        #self.log.info('\n')

    def clock(self, event):
        """在交易时间会定时推送 clock 事件
        :param event: event.data.clock_event 为 [0.5, 1, 3, 5, 15, 30, 60] 单位为分钟,  ['open', 'close'] 为开市、收市
            event.data.trading_state  bool 是否处于交易时间
        """
        if event.data.clock_event == 'open':
            # 开市了
            self.set_Extralarge_detail(0)
            self.set_Big_detail(0)
            self.set_Medium_detail(0)
            self.set_Small_detail(0)
            self.log.info('Detail_Orders_Statistics init')
        elif event.data.clock_event == 'close':
            # 收市了
            #self.log.info('StoreData_Close')
            pass
        elif event.data.clock_event == 1:
            # 5 分钟的 clock
            #self.log.info("StoreData_5min")
            pass

    def log_handler(self):
        """自定义 log 记录方式"""
        log = self.name + '.log'
        return DefaultLogHandler(self.name, log_type='file', filepath=log)

    def shutdown_strategy(self):
        """
        关闭进程前的调用
        :return:
        """
        __bakeups = {'detail': {}}
        __bakeups['detail']['Extralarge_detail'] = self.get_Extralarge_detail()
        __bakeups['detail']['Big_detail'] = self.get_Big_detail()
        __bakeups['detail']['Medium_detail'] = self.get_Medium_detail()
        __bakeups['detail']['Small_detail'] = self.get_Small_detail()
        self.dict2file(__bakeups, self.__backups_path)

        self.log.info("%s 在关闭前保存了策略数据" % self.name)
