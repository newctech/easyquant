# coding:utf-8
import sys
import os
import time
import traceback
import pandas as pd


class StrategyTemplate:
    name = 'DefaultStrategyTemplate'

    def __init__(self, user, log_handler, main_engine):
        self.user = user
        self.main_engine = main_engine
        self.clock_engine = main_engine.clock_engine
        # 优先使用自定义 log 句柄, 否则使用主引擎日志句柄
        self.log = self.log_handler() or log_handler
        self.pankou_file = None
        self.detail_file = None
        self.realtime_file = None
        self.kdata_file = None
        self.general_file = None
        self.path_init()
        self.init()

    def init(self):
        # 进行相关的初始化操作
        pass

    def path_init(self):
        stockdata_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"..")) + '/stockdata'
        if not os.path.exists(stockdata_path):
            os.makedirs(stockdata_path)
        self.pankou_file = stockdata_path + '/pankou.hdf5'
        self.detail_file = stockdata_path + '/detail.hdf5'
        self.realtime_file = stockdata_path + '/realtime.hdf5'
        self.kdata_file = stockdata_path + '/kdata.hdf5'
        self.general_file = stockdata_path + '/general.hdf5'

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
        timestamp = str(int(time.mktime(time.strptime(pankou['time'], '%b %d, %Y %H:%M:%S %p')) * 1000))
        pankou_df = pd.DataFrame([pankou], index=[timestamp],
                                 columns=['symbol', 'time', 'current', 'buypct', 'sellpct', 'diff', 'ratio', 'bp1',
                                          'bc1', 'bp2', 'bc2', 'bp3', 'bc3', 'bp4', 'bc4', 'bp5', 'bc5', 'sp1', 'sc1',
                                          'sp2', 'sc2', 'sp3', 'sc3', 'sp4', 'sc4', 'sp5', 'sc5'])
        if os.path.exists(self.pankou_file):
            with pd.HDFStore(self.pankou_file) as store:
                store.append(pankou['symbol'], pankou_df, format="table", append=True)
        else:
            with pd.HDFStore(self.pankou_file) as store:
                store.put(pankou['symbol'], pankou_df, format="table")

    def pankou_read_hdf5(self, symbol):
        with pd.HDFStore(self.pankou_file) as store:
            pankou_df = store.select(symbol)
        return pankou_df

    def detail_write_hdf5(self, detail):
        detail_df = pd.DataFrame([detail], index=[str(detail['t'])],
                                 columns=['s', 'ts', 'v', 'type', 'avgPrice', 'c', 'chg', 'pct', 'bp1', 'sp1', 'ttv'])
        if os.path.exists(self.detail_file):
            with pd.HDFStore(self.detail_file) as store:
                store.append(detail['s'], detail_df, format="table", append=True)
        else:
            with pd.HDFStore(self.detail_file) as store:
                store.put(detail['s'], detail_df, format="table")

    def detail_read_hdf5(self, symbol):
        with pd.HDFStore(self.detail_file) as store:
            detail_df = store.select(symbol)
        return detail_df

    def realtime_write_hdf5(self, realtime, symbol):
        timestamp = str(int(time.mktime(time.strptime(realtime['time'], '%a %b %d %H:%M:%S %z %Y')) * 1000))
        realtime_df = pd.DataFrame([realtime], index=[timestamp],
                                   columns=['time', 'avg_price', 'current', 'volume'])
        if os.path.exists(self.realtime_file):
            with pd.HDFStore(self.realtime_file) as store:
                store.append(symbol, realtime_df, format="table", append=True)
        else:
            with pd.HDFStore(self.realtime_file) as store:
                store.put(symbol, realtime_df, format="table")

    def realtime_read_hdf5(self, symbol):
        with pd.HDFStore(self.realtime_file) as store:
            realtime_df = store.select(symbol)
        return realtime_df

    def kdata_write_hdf5(self, kdata, symbol):
        timestamp = str(int(time.mktime(time.strptime(kdata['time'], '%a %b %d %H:%M:%S %z %Y')) * 1000))
        kdata_df = pd.DataFrame([kdata], index=[timestamp],
                                columns=['time', 'open', 'close', 'high', 'low', 'chg', 'percent', 'volume', 'turnrate',
                                         'ma5', 'ma10', 'ma20', 'ma30', 'macd', 'dif', 'dea'])
        if os.path.exists(self.kdata_file):
            with pd.HDFStore(self.kdata_file) as store:
                store.append(symbol, kdata_df, format="table", append=True)
        else:
            with pd.HDFStore(self.kdata_file) as store:
                store.put(symbol, kdata_df, format="table")

    def kldata_read_hdf5(self, symbol):
        with pd.HDFStore(self.kdata_file) as store:
            kdata_df = store.select(symbol)
        return kdata_df

    def general_write_hdf5(self, general):
        timestamp = str(int(time.mktime(time.strptime(general['time'], '%a %b %d %H:%M:%S %z %Y')) * 1000))
        general_df = pd.DataFrame([general], index=[timestamp],
                                  columns=['symbol', 'time', 'open', 'current', 'percentage', 'high', 'low',
                                           'turnover_rate',
                                           'volume', 'amount', 'marketCapital', 'totalShares', 'float_market_capital',
                                           'float_shares', 'last_close', 'amplitude', 'rise_stop', 'fall_stop',
                                           'high52week',
                                           'low52week', 'pe_ttm', 'pe_lyr', 'pb', 'psr', 'net_assets', 'dividend',
                                           'yield',
                                           'change', 'eps', 'type', 'issue_type', 'redeem_type', 'par_value',
                                           'updateAt',
                                           'volumeAverage'])
        if os.path.exists(self.general_file):
            with pd.HDFStore(self.general_file) as store:
                store.append(general['symbol'], general_df, format="table", append=True)
        else:
            with pd.HDFStore(self.general_file) as store:
                store.put(general['symbol'], general_df, format="table")

    def general_read_hdf5(self, symbol):
        with pd.HDFStore(self.general_file) as store:
            general_df = store.select(symbol)
        return general_df

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
        pass
