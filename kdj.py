# coding:utf-8
import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine, XueqiuAllEngine, XueqiuPankouEngine, XueqiuDetailEngine, XueqiuRealtimeEngine, XueqiuKdataEngine, XueqiuGeneralEngine

print('开始启动......')
broker = 'xq'
need_data = 'xq.json'

#quotation_engine = [XueqiuPankouEngine, XueqiuDetailEngine, XueqiuRealtimeEngine, XueqiuKdataEngine, XueqiuGeneralEngi]
quotation_engine = [XueqiuAllEngine]

log_type_choose = input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
log_type = 'stdout' if log_type_choose == '1' else 'file'

log_filepath = input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''

log_handler = DefaultLogHandler(name='日志引擎', log_type=log_type, filepath=log_filepath)

m = easyquant.MainEngine(broker, need_data, quotation_engines=quotation_engine, log_handler=log_handler)
m.is_watch_strategy = True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
m.load_strategy()
m.start()
