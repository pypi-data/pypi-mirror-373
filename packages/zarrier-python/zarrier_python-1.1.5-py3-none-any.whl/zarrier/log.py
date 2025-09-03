import logging
from .string import zjoin, rjoin
from .timer import ZTimer


class Log:

    is_inited = False
    handers_std = {}
    handers_file = {}

    @classmethod
    def init(cls, logs_dir=None, fname=None):
        if cls.is_inited:
            return

        fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s : %(message)s")
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        names = ["debug", "info", "warning", "error", "critical"]

        logs_dir = logs_dir or rjoin("logs")

        for level, name in zip(levels, names):
            _hander_std = logging.StreamHandler()
            _hander_std.setLevel(level)
            _hander_std.setFormatter(fmt)
            cls.handers_std[level] = _hander_std

            log_file_path = zjoin(logs_dir, ZTimer.str2day(), f"{ZTimer.str_hmsms()}_{name}.txt", makedirs=True)

            _hander_file = logging.FileHandler(log_file_path, encoding="utf-8")
            _hander_file.setLevel(level)
            _hander_file.setFormatter(fmt)
            cls.handers_file[level] = _hander_file
        
        # 清除其他handler
        for handler in list(logging.root.handlers):
            logging.root.removeHandler(handler)

        logging.root.addHandler(cls.handers_std[logging.INFO])

        for level in levels:
            logging.root.addHandler(cls.handers_file[level])
            
        logging.root.level = logging.DEBUG

        cls.is_inited = True

    @classmethod
    def get_logger(cls, name="default", std_level=logging.INFO, file_level=logging.DEBUG):
        if not cls.is_inited:
            cls.init()
        logger = logging.getLogger(name)
        logger.addHandler(cls.handers_std[std_level])
        logger.addHandler(cls.handers_file[file_level])
        return logger

