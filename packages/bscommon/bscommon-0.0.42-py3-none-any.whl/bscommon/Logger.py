import logging
import os
import time

class Logger():

    def __init__(self, logger=None):
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        level = 'INFO'
        if level == 'DEBUG' or level == 'debug':
            self.setLev = logging.DEBUG
        elif level == 'INFO' or level == 'info':
            self.setLev = logging.INFO
        elif level == 'WARN' or level == 'warn' or level == 'warning' or level == 'WARNING':
            self.setLev = logging.WARN
        elif level == 'ERROR' or level == 'error':
            self.setLev = logging.ERROR
        self.logger.setLevel(self.setLev)

        # self.log_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.log_time = time.strftime("%Y-%m-%d")
        self.path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.log_path = os.path.join(self.path, 'logs')
        if not os.path.exists(self.log_path): os.mkdir(self.log_path)
        self.log_name = os.path.join(self.log_path, self.log_time + '.log')

        # 创建一个handler用于写入日志文件
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # a的意思是追加，防止每次都覆盖了
        fh.setLevel(self.setLev)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(self.setLev)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(filename)s-> line:%(lineno)d [%(levelname)s]-->%(message)s')
        # formatter = logging.Formatter(
        #     '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]-->%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        fh.close()
        ch.close()

    def getLogger(self):
        return self.logger


current=Logger().getLogger()
