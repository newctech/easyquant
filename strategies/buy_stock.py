# coding:utf-8
import time
import datetime as dt
from dateutil import tz
from easyquant import DefaultLogHandler
from easyquant import StrategyTemplate


class Strategy(StrategyTemplate):
    name = 'buyStock'

    def init(self):
        #买入股票列表, 已经买入的股票
        self.buy_stock_list = []
        #每天可买入股票的最大值
        self.buy_stock_countMax = 5
        #持有股票列表, 目前持有的股票
        self.hold_stock_list = []
        for stock in self.user.position:
            self.hold_stock_list.append(stock['stock_code'])
        #持有股票的最大值
        self.hold_stock_countMax = 10

        # 通过下面的方式来获取时间戳
        now_dt = self.clock_engine.now_dt
        now = self.clock_engine.now
        now = time.time()

        # 注册时钟事件
        clock_type = "closing" #尾盘
        moment = dt.time(14, 56, 30, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment)

        # 注册时钟间隔事件, 不在交易阶段也会触发, clock_type == minute_interval
        minute_interval = 1.5
        self.clock_engine.register_interval(minute_interval, trading=False)

    def strategy(self, event):
        # 使用 self.user 来操作账户，用法同 easytrader 用法
        # 使用 self.log.info('message') 来打印你所需要的 log
        #print('demo1 的 log 使用自定义 log 的方式记录在 demo1.log')
        #self.log.info('策略1触发')
        if event.event_type == 'pankou':
            self.log.info('buy_stock_Pankou: %s' % event.data)
        elif event.event_type == 'detail':
            self.log.info('buy_stock_Detail: %s' % event.data)
        elif event.event_type == 'realtime':
            self.log.info('buy_stock_Realtime: %s' % event.data)
        elif event.event_type == 'kdata':
            self.log.info('buy_stock_Kdata: %s' % event.data)
        elif event.event_type == 'general':
            self.log.info('buy_stock_General: %s' % event.data)

        elif event.event_type == 'shindex':
            if event.data['macd'] > 0.1:
                self.shbuying = True
            else:
                self.shbuying = False
        elif event.event_type == 'szindex':
            if event.data['macd'] > 0.1:
                self.szbuying = True
            else:
                self.szbuying = False
        elif event.event_type == 'feedback':
            if event.data['xueqiu_general']['name'][:2] == 'ST':
                pass
            else:
                self.Call_buy_pre(event.data)

    def Call_buy_pre(self, data):
        if data['xueqiu_realtime']['current'] > data['xueqiu_realtime']['avg_price']:
            self.Call_buy(data['xueqiu_general']['symbol'])

    def Call_buy(self, symbol):
        if self.buy_stock_countMax > 0 and symbol not in self.buy_stock_list and \
                        len(self.hold_stock_list) < self.hold_stock_countMax and symbol not in self.hold_stock_list:
            self.user.adjust_weight(symbol, 10)
            self.buy_stock_list.append(symbol)
            self.buy_stock_countMax -= 1
            self.hold_stock_list.append(symbol)
            self.log.info("Buy stock %s : buy_stock_list %s" % (symbol, self.buy_stock_list))
        else:
            self.log.info("Not buy %s : buy_stock_list %s" % (symbol, self.buy_stock_list))



    def clock(self, event):
        """在交易时间会定时推送 clock 事件
        :param event: event.data.clock_event 为 [0.5, 1, 3, 5, 15, 30, 60] 单位为分钟,  ['open', 'close'] 为开市、收市
            event.data.trading_state  bool 是否处于交易时间
        """
        if event.data.clock_event == 'open':
            # 开市了
            self.log.info('Strategy1_Open')
        elif event.data.clock_event == 'close':
            # 收市了
            self.log.info('Strategy1_Close')
        elif event.data.clock_event == 5:
            # 5 分钟的 clock
            self.log.info("Strategy1_5min")

    def log_handler(self):
        """自定义 log 记录方式"""
        log = self.name + '.log'
        return DefaultLogHandler(self.name, log_type='file', filepath=log)

    def shutdown_strategy(self):
        """
        关闭进程前的调用
        :return:
        """
        self.log.info("%s 在关闭前保存了策略数据" % self.name)
