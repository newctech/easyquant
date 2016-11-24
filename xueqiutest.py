import easyquotation

import easyquant
from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine, XueqiuPankouEngine, XueqiuDetailEngine, XueqiuRealtimeEngine, XueqiuKdataEngine, XueqiuGeneralEngine

print('xueqiu测试')
broker = 'xq'
def get_broker_need_data(broker):
    need_data = input('请输入你的帐号配置文件路径(直接回车使用 %s.json)\n:' % broker)
    if need_data == '':
        return '%s.json' % broker
    return need_data
need_data = get_broker_need_data(broker)

quotation_engine = [XueqiuPankouEngine, XueqiuDetailEngine, XueqiuRealtimeEngine, XueqiuKdataEngine, XueqiuGeneralEngine]

log_type_choose = input('请输入 log 记录方式: 1: 显示在屏幕 2: 记录到指定文件\n: ')
log_type = 'stdout' if log_type_choose == '1' else 'file'

log_filepath = input('请输入 log 文件记录路径\n: ') if log_type == 'file' else ''

log_handler = DefaultLogHandler(name='测试xueqiu', log_type=log_type, filepath=log_filepath)

m = easyquant.MainEngine(broker, need_data, quotation_engines=quotation_engine, log_handler=log_handler)
m.is_watch_strategy = True  # 策略文件出现改动时,自动重载,不建议在生产环境下使用
m.load_strategy()
m.start()
