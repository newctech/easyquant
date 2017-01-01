# coding:utf-8
import sys
import os
import json
import time
import datetime
import traceback
import pandas as pd
import numpy as np
import talib
from functools import reduce
import threading


class StrategyTemplate:
    name = 'DefaultStrategyTemplate'

    def __init__(self, user, log_handler, main_engine, feedback_queue):
        self.user = user
        self.main_engine = main_engine
        self.clock_engine = main_engine.clock_engine
        # 优先使用自定义 log 句柄, 否则使用主引擎日志句柄
        self.log = self.log_handler() or log_handler
        self.feedback_queue = feedback_queue

        self.path_init()
        self.quota_init()
        self.init()



    def init(self):
        # 进行相关的初始化操作
        pass

    def path_init(self):
        self.__init_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) + '/config/init.json'
        self.__init_config = self.file2dict(self.__init_path)
        self.__backups_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"..")) + '/config/backups.json'
        self.__backups_config = self.file2dict(self.__backups_path)

        stockdata_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"..")) + '/stockdata'
        if not os.path.exists(stockdata_path):
            os.makedirs(stockdata_path)
        self.pankou_file = stockdata_path + '/pankou.hdf5'
        self.detail_file = stockdata_path + '/detail.hdf5'
        self.realtime_file = stockdata_path + '/realtime.hdf5'
        self.kdata_file = stockdata_path + '/kdata.hdf5'
        self.general_file = stockdata_path + '/general.hdf5'

        self.__pankou_store = pd.HDFStore(self.pankou_file)
        self.__pankou_lock = threading.Lock()

        self.__detail_store = pd.HDFStore(self.detail_file)
        self.__detail_lock = threading.Lock()

        self.__realtime_store = pd.HDFStore(self.realtime_file)
        self.__realtime_lock = threading.Lock()

        self.__kdata_store = pd.HDFStore(self.kdata_file)
        self.__kdata_lock = threading.Lock()

        self.__general_store = pd.HDFStore(self.general_file)
        self.__general_lock = threading.Lock()

    def quota_init(self):
        self.shbuying = False
        self.szbuying = False

        self.__opentime = datetime.time(9,0,0)
        self.__closetime = datetime.time(15, 0, 0)
        self.__now = datetime.datetime.now().time()

        #特大订单,100万元以上
        if self.__opentime < self.__now < self.__closetime:
            self.__Extralarge_detail = self.__backups_config['detail']['Extralarge_detail']
        else:
            self.__Extralarge_detail = self.__init_config['detail']['Extralarge_detail']
        self.__Extralarge_detail_lock = threading.Lock()

        #大单,50-100万元
        if self.__opentime < self.__now < self.__closetime:
            self.__Big_detail = self.__backups_config['detail']['Big_detail']
        else:
            self.__Big_detail = self.__init_config['detail']['Big_detail']
        self.__Big_detail_lock = threading.Lock()

        #中单,4万元-50万元
        if self.__opentime < self.__now < self.__closetime:
            self.__Medium_detail = self.__backups_config['detail']['Medium_detail']
        else:
            self.__Medium_detail = self.__init_config['detail']['Medium_detail']
        self.__Medium_detail_lock = threading.Lock()

        #小单,4万元以下
        if self.__opentime < self.__now < self.__closetime:
            self.__Small_detail = self.__backups_config['detail']['Small_detail']
        else:
            self.__Small_detail = self.__init_config['detail']['Small_detail']
        self.__Small_detail_lock = threading.Lock()


    def file2dict(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    def dict2file(self, data, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

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

    def run(self, event):
        try:
            self.strategy(event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error(repr(traceback.format_exception(exc_type,
                                                           exc_value,
                                                           exc_traceback)))

    def clock(self, event):
        pass

    def pankou_write_hdf5(self, pankou):
        timestamp = pd.Timestamp(pankou['time'])
        pankou_df = pd.DataFrame([pankou], index=[timestamp],
                                 columns=['symbol', 'current', 'buypct', 'sellpct', 'diff', 'ratio', 'bp1',
                                          'bc1', 'bp2', 'bc2', 'bp3', 'bc3', 'bp4', 'bc4', 'bp5', 'bc5', 'sp1', 'sc1',
                                          'sp2', 'sc2', 'sp3', 'sc3', 'sp4', 'sc4', 'sp5', 'sc5'])
        self.__pankou_lock.acquire()
        self.__pankou_store.put(pankou['symbol'], pankou_df, format="table", append=True)
        self.__pankou_lock.release()

    def pankou_read_hdf5(self, symbol):
        self.__pankou_lock.acquire()
        pankou_df = self.__pankou_store.select(symbol)
        self.__pankou_lock.release()
        return pankou_df

    def detail_write_hdf5(self, detail):
        timeArray = time.localtime(detail['t'] / 1000)
        timestamp = pd.Timestamp(time.strftime("%Y-%m-%d %H:%M:%S", timeArray))
        detail_df = pd.DataFrame([detail], index=[timestamp],
                                 columns=['s', 'v', 'type', 'avgPrice', 'c', 'chg', 'pct', 'bp1', 'sp1', 'ttv'])
        self.__detail_lock.acquire()
        self.__detail_store.put(detail['s'], detail_df, format="table", append=True)
        self.__detail_lock.release()

    def detail_read_hdf5(self, symbol):
        self.__detail_lock.acquire()
        detail_df = self.__detail_store.select(symbol)
        self.__detail_lock.release()
        return detail_df

    def realtime_write_hdf5(self, realtime, symbol):
        timeArray = time.strptime(realtime['time'], "%a %b %d %H:%M:%S %z %Y")
        timestamp = pd.Timestamp(time.strftime("%Y-%m-%d %H:%M:%S", timeArray))
        realtime_df = pd.DataFrame([realtime], index=[timestamp],
                                   columns=['avg_price', 'current', 'volume'])
        self.__realtime_lock.acquire()
        self.__realtime_store.put(symbol, realtime_df, format="table", append=True)
        self.__realtime_lock.release()

    def realtime_read_hdf5(self, symbol):
        self.__realtime_lock.acquire()
        realtime_df = self.__realtime_store.select(symbol)
        self.__realtime_lock.release()
        return realtime_df

    def kdata_write_hdf5(self, kdata, symbol):
        timeArray = time.strptime(kdata['time'], "%a %b %d %H:%M:%S %z %Y")
        timestamp = pd.Timestamp(time.strftime("%Y-%m-%d %H:%M:%S", timeArray))
        kdata_df = pd.DataFrame([kdata], index=[timestamp],
                                columns=['open', 'close', 'high', 'low', 'chg', 'percent', 'volume', 'turnrate',
                                         'ma5', 'ma10', 'ma20', 'ma30', 'macd', 'dif', 'dea'])
        self.__kdata_lock.acquire()
        self.__kdata_store.put(symbol, kdata_df, format="table", append=True)
        self.__kdata_lock.release()

    def kdata_read_hdf5(self, symbol):
        self.__kdata_lock.acquire()
        kdata_df = self.__kdata_store.select(symbol)
        self.__kdata_lock.release()
        return kdata_df

    def general_write_hdf5(self, general):
        timeArray = time.strptime(general['time'], "%a %b %d %H:%M:%S %z %Y")
        timestamp = pd.Timestamp(time.strftime("%Y-%m-%d %H:%M:%S", timeArray))
        general_df = pd.DataFrame([general], index=[timestamp],
                                  columns=['symbol', 'open', 'current', 'percentage', 'high', 'low',
                                           'turnover_rate',
                                           'volume', 'amount', 'marketCapital', 'totalShares', 'float_market_capital',
                                           'float_shares', 'last_close', 'amplitude', 'rise_stop', 'fall_stop',
                                           'high52week',
                                           'low52week', 'pe_ttm', 'pe_lyr', 'pb', 'psr', 'net_assets', 'dividend',
                                           'yield',
                                           'change', 'eps', 'type', 'issue_type', 'redeem_type', 'par_value',
                                           'updateAt',
                                           'volumeAverage'])
        self.__general_lock.acquire()
        self.__general_store.put(general['symbol'], general_df, format="table", append=True)
        self.__general_lock.release()

    def general_read_hdf5(self, symbol):
        self.__general_lock.acquire()
        general_df = self.__general_store.select(symbol)
        self.__general_lock.release()
        return general_df


    def set_Extralarge_detail(self, value):
        self.__Extralarge_detail_lock.acquire()
        self.__Extralarge_detail = value
        self.__Extralarge_detail_lock.release()

    def get_Extralarge_detail(self):
        self.__Extralarge_detail_lock.acquire()
        value = self.__Extralarge_detail
        self.__Extralarge_detail_lock.release()
        return value

    def set_Big_detail(self, value):
        self.__Big_detail_lock.acquire()
        self.__Big_detail = value
        self.__Big_detail_lock.release()

    def get_Big_detail(self):
        self.__Big_detail_lock.acquire()
        value = self.__Big_detail
        self.__Big_detail_lock.release()
        return value

    def set_Medium_detail(self, value):
        self.__Medium_detail_lock.acquire()
        self.__Medium_detail = value
        self.__Medium_detail_lock.release()

    def get_Medium_detail(self):
        self.__Medium_detail_lock.acquire()
        value = self.__Medium_detail
        self.__Medium_detail_lock.release()
        return value

    def set_Small_detail(self, value):
        self.__Small_detail_lock.acquire()
        self.__Small_detail = value
        self.__Small_detail_lock.release()

    def get_Small_detail(self):
        self.__Small_detail_lock.acquire()
        value = self.__Small_detail
        self.__Small_detail_lock.release()
        return value

    #获取RSI指标
    def Get_RSI(self, df, timeperiod):
        close = np.array(df['close'])
        rsi = pd.Series(talib.RSI(close, timeperiod), index=df.index, name='RSI%d' % timeperiod)
        dfrsi = df.join(rsi)
        return dfrsi

    #获取成交量移动平均值
    def Get_Volume_MA(self, df, timeperiod):
        volume = pd.Series(pd.rolling_mean(df['volume'], timeperiod), index=df.index, name='Vol_MA%d' % timeperiod)
        dfvol = df.join(volume)
        return dfvol

    # 同花顺和通达信等软件中的SMA
    def SMA_CN(self, close, timeperiod):
        close = np.nan_to_num(close)
        return reduce(lambda x, y: ((timeperiod - 1) * x + y) / timeperiod, close)

    # 同花顺和通达信等软件中的KDJ
    def KDJ_CN(self, df, fastk_period, slowk_period, fastd_period):
        high = np.nan_to_num(df['high'])
        low = np.nan_to_num(df['low'])
        close = np.nan_to_num(df['close'])
        kValue, dValue = talib.STOCHF(high, low, close, fastk_period, fastd_period=1, fastd_matype=0)

        kValue = np.array(list(map(lambda x: self.SMA_CN(kValue[:x], slowk_period), range(1, len(kValue) + 1))))
        dValue = np.array(list(map(lambda x: self.SMA_CN(kValue[:x], fastd_period), range(1, len(kValue) + 1))))

        jValue = 3 * kValue - 2 * dValue

        func = lambda arr: np.array([0 if x < 0 else (100 if x > 100 else x) for x in arr])

        kValue = pd.Series(func(kValue), index=df.index, name='K')
        dValue = pd.Series(func(dValue), index=df.index, name='D')
        jValue = pd.Series(func(jValue), index=df.index, name='J')

        dfk = df.join(kValue)
        dfkd = dfk.join(dValue)
        dfkdj = dfkd.join(jValue)
        return dfkdj

    # 同花顺和通达信等软件中的MACD
    def MACD_CN(self, df, fastperiod, slowperiod, signalperiod):
        close = np.nan_to_num(df['close'])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod,
                                                slowmatype=1, signalperiod=signalperiod, signalmatype=1)
        macd = macd * 2
        macdDIFF = pd.Series(macdDIFF, index=df.index, name='DIF')
        macdDEA = pd.Series(macdDEA, index=df.index, name='DEA')
        macd = pd.Series(macd, index=df.index, name='MACD')

        dfmacd = df.join(macd)
        dfmacddiff = dfmacd.join(macdDIFF)
        df = dfmacddiff.join(macdDEA)
        return df

    def Check_Vol_Buy(self, df, timeperiod, ratio):
        if df['volume'][-1] > df['Vol_MA%s' % timeperiod][-1] * ratio:
            return True

    def Check_KDJ_Buy(self, df):
        if self.Is_Down_Going(df['D'], 2):
            return False
        else:
            if df['K'][-1] >= (df['D'][-1] * 1.05):
                return True

    def Check_KDJ_Sell(self, df):
        if self.Is_Down_Going(df['J'], 3):
            return True

    def Check_MACD_Buy(self, df):
        if self.Is_Down_Going(df['macd'], 4) or self.Is_Down_Going(df['dea'], 1):
            return False
        else:
            if df['macd'][-1] >= 0.02 and df['macd'][-2] <= 0.01:
                return True

    def Check_MACD_Sell(self, df):
        if df['macd'][-1] < 0:
            return True

    def Check_Rise_Stop(self, numpy_percent, n):
        if len(numpy_percent) < n:
            return False
        for i in range(n-1):
            if numpy_percent[-1-i] >= 9.95:
                return True
        return False

    def Check_Fall_Stop(self, numpy_percent, n):
        if len(numpy_percent) < n:
            return False
        for i in range(n-1):
            if numpy_percent[-1-i] <= -9.95:
                return True
        return False

    def Is_Up_Going(self, numpy_data, n):
        if len(numpy_data) < n+1:
            return False
        for i in range(n-1):
            if numpy_data[-1-i] <= numpy_data[-2-i]:
                return False
        return True

    def Is_Down_Going(self, numpy_data, n):
        if len(numpy_data) < n+1:
            return False
        for i in range(n):
            if numpy_data[-1-i] >= numpy_data[-2-i]:
                return False
        return True

    def log_handler(self):
        """
        优先使用在此自定义 log 句柄, 否则返回None, 并使用主引擎日志句柄
        :return: log_handler or None
        """
        return None

    def shutdown(self):
        """
        关闭进程前调用该函数
        :return:
        """

        self.__pankou_store.close()
        self.__detail_store.close()
        self.__realtime_store.close()
        self.__kdata_store.close()
        self.__general_store.close()

        self.shutdown_strategy()

    def shutdown_strategy(self):
        pass
