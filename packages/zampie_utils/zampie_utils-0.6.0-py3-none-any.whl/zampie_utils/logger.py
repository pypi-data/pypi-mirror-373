import logging
from rich.logging import RichHandler
from .singleton import Singleton


class Logger(metaclass=Singleton):
    """"""

    def __init__(
        self, log_level=logging.INFO):
        """
        description: 初始化日志记录器
        param:
            log_level: 日志级别
            logfile: 日志文件路径
            enable_file_handler: 是否启用文件处理器
        return:
        """
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)

        # 控制台处理器 - 使用 Rich
        self.console_handler = RichHandler()
        # Rich 自带格式化，无需额外设置 formatter
        self.logger.addHandler(self.console_handler)


        # 直接指向方法，避免间接调用，无法定位到文件
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.debug = self.logger.debug

        self.file_handler_dict = {}
        self.file_handler_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

    def add_file_handler(self, logfile="log.txt", log_level=None):
        """
        description: 启用文件处理器
        param:
            logfile: 日志文件路径
            log_level: 文件处理器的日志级别，默认使用全局日志级别
        return:
            bool: 是否成功添加文件处理器
        """
        try:
            # 检查是否已经存在该文件的处理器
            if logfile in self.file_handler_dict:
                self.logger.warning(f"文件处理器 {logfile} 已经存在，跳过添加")
                return False
            
            file_handler = logging.FileHandler(logfile, encoding='utf-8')
            
            # 设置日志级别
            if log_level is not None:
                file_handler.setLevel(log_level)
            
            file_handler.setFormatter(self.file_handler_formatter)
            self.logger.addHandler(file_handler)
            self.file_handler_dict[logfile] = file_handler
            
            self.logger.info(f"成功添加文件处理器: {logfile}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加文件处理器失败 {logfile}: {str(e)}")
            return False

    def disable_file_handler(self, logfile="log.txt"):
        """
        description: 禁用文件处理器
        param:
            logfile: 日志文件路径
        return:
            bool: 是否成功禁用文件处理器
        """
        if logfile in self.file_handler_dict:
            try:
                self.logger.removeHandler(self.file_handler_dict[logfile])
                self.file_handler_dict.pop(logfile)
                self.logger.info(f"成功禁用文件处理器: {logfile}")
                return True
            except Exception as e:
                self.logger.error(f"禁用文件处理器失败 {logfile}: {str(e)}")
                return False
        else:
            self.logger.warning(f"文件处理器 {logfile} 不存在")
            return False

    def set_log_level(self, log_level: str):
        """
        description: 设置日志级别
        param:
            log_level: 日志级别
        return:
        """
        self.logger.setLevel(log_level)

if __name__ == "__main__":
    # 默认不启用文件处理器
    logger = Logger()
    logger.info("this is a log message")
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.debug("this is a debug message")

    # 启用文件处理器
    logger.add_file_handler("test.log")
    logger.info("this will be written to file")

    # 禁用文件处理器
    logger.disable_file_handler("test.log")
    logger.info("this will not be written to file")

    print(f"They are same instance? {id(logger) == id(Logger())}")
