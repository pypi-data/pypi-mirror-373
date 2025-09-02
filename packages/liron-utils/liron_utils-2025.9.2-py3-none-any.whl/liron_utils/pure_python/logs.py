import sys
import atexit
import logging
import time
import inspect
from colorama import Fore, Back, Style

from .dicts import dict_


class Logger:
    NAME2LEVEL = dict_(logging._nameToLevel)
    LEVEL2NAME_OLD = dict_(logging._levelToName)
    LEVEL2NAME = dict_({
        logging.CRITICAL: 'Fatal',
        logging.ERROR:    'Error',
        logging.WARNING:  'Warn',
        logging.INFO:     'Info',
        logging.DEBUG:    'Debug',
        logging.NOTSET:   'Notset',
    })
    ENTER_MSG = "STARTING LOGGER\t------------------------------------"
    EXIT_MSG = "CLOSING LOGGER\t------------------------------------"

    ENTER_CALLED = False

    def __init__(self,
            file_name: str = "./logs.log",
            min_level_file: int = logging.INFO,
            min_level_console: int = None,
            default_level: int = logging.INFO,
            log_message_format: str = '%(asctime)s | %(levelname)-14s | %(filename)-15s:%(lineno)4d | %(class_func)-30s >> %(message)s',
    ):
        """
        Initialize logger.

        Examples
        --------
        >>> with Logger(min_level_console=Logger.NAME2LEVEL["WARNING"]) as logger:
        >>>      logger.log("Hello")  # Will not be printed
        >>>      logger.log("World", logging.ERROR)  # Will be printed

        >>> logger = Logger()  # __enter__ is called automatically
        >>> logger.log("Hello")  # __exit__ will be called automatically upon code completion

        >>> logger = Logger()
        >>> raise ValueError("This is an error.")  # Uncaught exception will be logged and the logger will be closed

        Parameters
        ----------
        file_name :                 str, optional
            Logger file path. Default is "./logs.log"
        min_level_file              str, optional
            Level of messages to print to file. Default is INFO
        min_level_console :         int, optional
            Level of messages to print to console. If None, will not print
        default_level :             int, optional
            Default logging level, if no level is provided. Default is INFO
        log_message_format :        str, optional
            Default string format of a message
        """
        if not file_name.endswith(".log"):
            file_name += ".log"

        with open(file_name, 'a'):  # Create the file if it doesn't exist
            pass
        self.logger = logging.getLogger(file_name)
        self.default_level = default_level
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler to write log messages to a file
        class _Formatter(logging.Formatter):
            # Formatter that changes the level name to a shorthand version (e.g., WARNING->Warn).
            def format(self, record):
                record.levelname = record.levelname.replace(Logger.LEVEL2NAME_OLD[record.levelno],
                        Logger.LEVEL2NAME[record.levelno])

                record.class_func = self._get_class_func(record)

                return super().format(record)

            @staticmethod
            def _get_class_func(record):
                frame = inspect.currentframe()
                while frame:
                    if frame.f_code.co_name == record.funcName:
                        # Look for 'self' or 'cls' in the frame's local variables
                        local_self = frame.f_locals.get('self', None) or frame.f_locals.get('cls', None)
                        if local_self:
                            return f'{local_self.__class__.__name__}.{record.funcName}'
                    frame = frame.f_back
                return record.funcName  # Fallback

        self.file_handler = logging.FileHandler(file_name)
        if min_level_file is not None:
            self.file_handler.setLevel(min_level_file)
            formatter = _Formatter(log_message_format)
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)

        # Create a console handler to write log messages to the console
        class _FormatterColored(_Formatter):
            # Formatter that adds colors to log messages based on their level.
            COLORS = {
                logging.CRITICAL: Fore.LIGHTWHITE_EX + Back.LIGHTRED_EX,
                logging.ERROR:    Fore.RED,
                logging.WARNING:  Fore.YELLOW,
                logging.INFO:     Fore.BLUE,
                logging.DEBUG:    Fore.MAGENTA,
                logging.NOTSET:   Fore.BLACK
            }

            def format(self, record):
                color = self.COLORS.get(record.levelno, "")
                record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
                return super().format(record)

        self.console_handler = logging.StreamHandler(sys.stdout)
        if min_level_console is not None:
            self.console_handler.setLevel(min_level_console)
            formatter = _FormatterColored(log_message_format)
            self.console_handler.setFormatter(formatter)
            self.logger.addHandler(self.console_handler)

        atexit.register(self.__exit__, None, None, None)  # Register exit function

        excepthook_old = sys.excepthook  # Save the old exception hook

        def excepthook_new(exc_type, exc_value, exc_traceback):
            self.__exit__(exc_type, exc_value, exc_traceback)
            excepthook_old(exc_type, exc_value, exc_traceback)

        sys.excepthook = excepthook_new  # Set the new exception hook

        self.__enter__()

    def __enter__(self):
        if self.ENTER_CALLED:
            return self

        self.info(self.ENTER_MSG)
        self.ENTER_CALLED = True
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            if not issubclass(exc_type, KeyboardInterrupt):  # Ignore keyboard interrupts
                self.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

        self.info(self.EXIT_MSG)
        self.logger.removeHandler(self.file_handler)
        self.file_handler.close()
        self.logger.removeHandler(self.console_handler)
        self.console_handler.close()

    def log(self,
            msg: str,
            level: int = None,
            exc_info: bool = False,
            time_log: float = None,
            f: str = ':.3f',
            stacklevel: int = 2,
            *args, **kwargs):
        """
        Send a log message to the log file.

        Parameters
        ----------
        msg :               str
            Message string
        level :             int
            Logging level (one of self.LEVELS)
        exc_info :          bool
            Error info
        time_log :          float
            Time log
        f :                 str
            Format string for time log
        stacklevel :        int
            Stack level for the log message
        *args, **kwargs :   Passed to Logger.log

        **kwargs :      dict
            Passed to Logger.log

        Returns
        -------

        """

        if level is None:
            level = self.default_level

        kwargs = dict(stacklevel=stacklevel) | kwargs

        tm = time.time()
        if time_log is not None:
            msg = msg.replace('{}', '{' + f + '}')
            msg = msg.format(tm - time_log)

        self.logger.log(
                level=level,
                msg=msg,
                exc_info=exc_info,
                *args, **kwargs)

        return tm

    def debug(self, msg: str, *args, **kwargs):
        kwargs = dict(stacklevel=3) | kwargs
        return self.log(msg, level=logging.DEBUG, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        kwargs = dict(stacklevel=3) | kwargs
        return self.log(msg, level=logging.INFO, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        kwargs = dict(stacklevel=3) | kwargs
        return self.log(msg, level=logging.WARNING, *args, **kwargs)

    warn = warning

    def error(self, msg: str, *args, **kwargs):
        kwargs = dict(stacklevel=3) | kwargs
        return self.log(msg, level=logging.ERROR, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        kwargs = dict(stacklevel=3) | kwargs
        return self.log(msg, level=logging.CRITICAL, *args, **kwargs)

    fatal = critical
