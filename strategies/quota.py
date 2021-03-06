# -*- coding: utf-8 -*-
import os
import time
import datetime as dt
from dateutil import tz
from easyquant import DefaultLogHandler
from easyquant import StrategyTemplate
import pandas as pd
import numpy as np


class Strategy(StrategyTemplate):
    name = 'quota'

    def init(self):
        #买入时间前符合条件的股票列表, 并不会按照此列表买入
        self.try_buy_stock_list = []
        #买入时间,要买入的股票列表
        self.buy_stock_list = []
        #持有股票列表, 目前持有的股票
        self.hold_stock_list = []
        for stock in self.user.position:
            self.hold_stock_list.append(stock['stock_code'])
        #持有股票的最大值
        self.hold_stock_countMax = 10
        #卖出股票列表, 记录卖出的股票, 此列表中的股票会立即被卖出
        self.sell_stock_list = []
        #每天卖出股票的最大值
        self.sell_stock_countMax = 10

        #股票黑名单
        self.blacklist = []

        # 通过下面的方式来获取时间戳
        now_dt = self.clock_engine.now_dt
        now = self.clock_engine.now
        now = time.time()

        # 注册时钟事件
        clock_type = "buying" #尾盘
        moment = dt.time(14, 55, 00, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment, makeup=True)

        # 注册时钟事件
        clock_type = "update" #存储K线数据
        moment = dt.time(15, 15, 0, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment(clock_type, moment, makeup=False)

        # 注册时钟间隔事件, 不在交易阶段也会触发, clock_type == minute_interval
        minute_interval = 0.5
        self.clock_engine.register_interval(minute_interval, trading=False)

        self.buying_time = False
        self.selling_time = False
        self.updatetime = False

        self.__backups_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) + '/easyquant/config/backups.json'

    def strategy(self, event):
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
            pass
        elif event.event_type == 'kdata':
        #    self.log.info('xueqiu_kdata: %s' % event.data)
            pass
        elif event.event_type == 'general':
            #self.log.info('StoreData_General: %s' % event.data)
            #self.general_write_hdf5(event.data)
            pass


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


        elif event.event_type == 'all':
            if self.updatetime == True:
                self.update(event.data)
            for stock_data in event.data:
                symbol = stock_data['stock']['symbol']
                stock = stock_data['chartlist']
                if len(stock) == 0:
                    continue
                if symbol in self.blacklist:
                    continue
                try:
                    cal_quota = self.Calquota_base(symbol, stock[-1])
                    if cal_quota == None:
                        continue
                    elif cal_quota == 'Calquota_buy':
                        df = self.Caldata(symbol, stock[-1])
                        self.Calquota_buy(symbol, df)
                    elif cal_quota == 'Calquota_sell':
                        df = self.Caldata(symbol, stock[-1])
                        self.Calquota_sell(symbol, df)
                except KeyError:
                    self.log.info("Add %s to blacklist : %s" % (symbol, self.blacklist))
                    continue

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

            self.selling_time = True
            self.log.info('Quota_Open')
            self.log.info('Selling_Time Start !!!')
        elif event.data.clock_event == 'close':
            # 收市了
            self.buying_time = False
            self.selling_time = False
            self.log.info('Buying_Time End !!!')
            self.log.info('Selling_Time End !!!')
            self.log.info('Quota_Close')
        elif event.data.clock_event == 'buying':
            self.buying_time = True
            self.log.info('Buying_Time Start !!!')
        elif event.data.clock_event == 'update':
            self.updatetime = True
            self.log.info('Update_Time Start !!!')

        elif event.data.clock_event == 1:
            # 1 分钟的 clock
            #self.log.info("StoreData_5min")
            pass

    def update(self, stocks):
        self.updatetime = False
        for stock in stocks:
            symbol_key = stock['stock']['symbol']
            for data in stock['chartlist']:
                self.kdata_write_hdf5(data, symbol_key)
        self.log.info('Update_Time End !!!')

        #数据计算
    def Caldata(self, symbol, stock):
        basedf = self.kdata_read_hdf5(symbol)[-40:]
        stock.pop('time')
        timestamp = pd.Timestamp('1970-01-01')
        series = pd.DataFrame(stock, index=[timestamp])
        dfdata = basedf.append(series)
        dfdatavol = self.Get_Volume_MA(dfdata, 5)
        dfdatavol = self.Get_Volume_MA(dfdatavol, 30)
        df = self.KDJ_CN(dfdatavol, 9, 3, 3)
        return df

        #初始化调用策略入口
    def Calquota_base(self, symbol, stock):
        if symbol in self.hold_stock_list:
            return 'Calquota_sell'
        if stock['close'] > stock['ma5'] * 1.2 or stock['close'] > stock['ma10'] * 1.2:
            return None
        if stock['macd'] > 0 and stock['ma5'] > stock['ma10'] and \
                        stock['close'] > stock['open'] + (stock['high'] - stock['open']) * 0.7:
            return 'Calquota_buy'
        return None

        #买入策略
    def Calquota_buy(self, symbol, df):
        if self.Is_Down_Going(df['ma10'], 3):
            return False
        else:
            #排除空头排列
            if self.Is_Down_Going(df['ma20'], 6) and self.Is_Down_Going(df['ma30'], 6):
                return False
            if self.Check_MACD_Buy(df) and self.Check_KDJ_Buy(df):
                if self.buying_time:
                    if self.Check_Vol_Buy(df, 5, 1.25) and self.Check_Vol_Buy(df, 30, 1):
                        self.Add_list_buy(symbol)
                else:
                    self.Add_list_try_buy(symbol)
                return True
            return False

        #加入视图买入列表
    def Add_list_try_buy(self, symbol):
        if symbol not in self.try_buy_stock_list:
            self.try_buy_stock_list.append(symbol)
            self.log.info("Add try stock : %s , try_buy_stock_list: %s" % (symbol, self.try_buy_stock_list))

        #加入买入列表
    def Add_list_buy(self, symbol):
        if symbol not in self.buy_stock_list:
            self.buy_stock_list.append(symbol)
            self.feedback_queue.put(symbol)
            self.log.info("Add stock : %s , buy_stock_list: %s" % (symbol, self.buy_stock_list))

        #卖出策略
    def Calquota_sell(self, symbol, df):
        if self.selling_time:
            if self.Check_MACD_Sell(df):
                self.Add_list_sell(symbol)
                self.log.info("Sell stock for MACD : %s , sell_stock_list: %s" % (symbol, self.buy_stock_list))
            if self.Check_KDJ_Sell(df):
                self.Add_list_sell(symbol)
                self.log.info("Sell stock for KDJ : %s , sell_stock_list: %s" % (symbol, self.buy_stock_list))
        else:
            pass

        #加入卖出列表
    def Add_list_sell(self, symbol):
        if self.sell_stock_countMax > 0:
            if symbol not in self.sell_stock_list:
                self.sell_stock_list.append(symbol)
            self.user.adjust_weight(symbol, 0)
            self.hold_stock_list.remove(symbol)
            self.sell_stock_countMax -= 1
        else:
            self.log.info("Not sell stock for countMax : %s , sell_stock_countMax <= 0 : %s" % (symbol, self.buy_stock_list))


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
