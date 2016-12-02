from easyquant import StrategyTemplate
#from easyquant import DefaultLogHandler


class Strategy(StrategyTemplate):
    name = 'Strategy2'

    def strategy(self, event):
        self.log.info('Strategy2')
        #self.log.info('行情数据: 华宝油气 %s' % event.data['162411'])
        #self.log.info('检查持仓')
        #self.log.info(self.user.balance)
        #self.log.info('\n')


#    def log_handler(self):
#        """自定义 log 记录方式"""
#        log = self.name + '.log'
#        return DefaultLogHandler(self.name, log_type='stdout', filepath=log)

    def shutdown_strategy(self):
        """
        关闭进程前的调用
        :return:
        """
        self.log.info("%s 在关闭前保存了策略数据" % self.name)
