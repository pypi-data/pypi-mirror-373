import os
import sys
import time
import logging
import datetime
from pathlib import Path

_DEFAULT_FLAG = "_nxva_default_handler"

class _SilenceIfRootConfigured(logging.Filter):
    def filter(self, record):
        # Once an external handler is later attached to the root logger, silence the default handler.
        return not bool(logging.getLogger().handlers)


def ensure_default_logging(pkg_name='nxva', level=logging.INFO, env_switch='NXVA_DEFAULT_LOG'):
    """    
    This function sets up a default logging handler for the package if it does not already exist.
    It checks an environment variable to determine whether to enable or disable the default logging.
    Args:
        pkg_name (str): The name of the package for which to set up logging.
        level (int): The logging level for the default handler.
        env_switch (str): The environment variable that controls whether the default logging is enabled or disabled.
    """
    # You can disable the default output via an environment variable 
    # e.g. in CI/testing: NXVA_DEFAULT_LOG=0.
    if os.getenv(env_switch, '1') in ('0', 'false', 'False'):
        return

    pkg_logger = logging.getLogger(pkg_name)

    # If nxva or root already has a handler, do not interfere to avoid duplication.
    if pkg_logger.handlers or logging.getLogger().handlers:
        return

    h = logging.StreamHandler()
    h.setLevel(level)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    h.setFormatter(fmt)
    h.addFilter(_SilenceIfRootConfigured())
    setattr(h, _DEFAULT_FLAG, True)

    pkg_logger.addHandler(h)
    # Set the logging level for the package logger
    # This prevents to propagate to the root logger which sets the default level to WARNING
    pkg_logger.setLevel(level)
    # Default to propagate to the root logger.
    # This allows the default logger to be used in other modules without needing to set it up externally.
    pkg_logger.propagate = True


def disable_default_logging(pkg_name='nxva'):
    pkg_logger = logging.getLogger(pkg_name)
    for h in list(pkg_logger.handlers):
        if getattr(h, _DEFAULT_FLAG, False):
            pkg_logger.removeHandler(h)
            h.close()


def bridge_namespace(from_ns, to_ns_list):
    """
    Bridges log handlers from one namespace to another.
    This allows logs from one namespace to be captured by another, useful for
    consolidating logs from multiple modules or packages.
    Args:
        from_ns (str): The source namespace from which to copy handlers.
        to_ns_list (str or list): The target namespace(s) to which handlers should be copied.
    """
    if isinstance(to_ns_list, str):
        to_ns_list = [to_ns_list]

    src = logging.getLogger(from_ns)

    if not src.handlers:
        print(f"Warning: No handlers found for logger '{from_ns}'. Cannot bridge namespaces.", flush=True)
        return

    for ns in to_ns_list:
        lg = logging.getLogger(ns)
        for h in list(lg.handlers):
            try:
                h.close()
            except Exception:
                pass
            lg.removeHandler(h)
        for h in src.handlers:
            lg.addHandler(h)
        lg.setLevel(src.level)
        lg.propagate = False


class Logger():
    """
    A custom logger class that handles log creation, daily log rotation,
    and automatic deletion of expired log files based on a defined expiration.

    Attributes:
        level (str): The logging level for the logger (e.g., 'DEBUG', 'INFO').
        console (str): The logging level for console output.
        file (str): The logging level for file output.
        root (str): The root directory where log files are stored.
        file_prefix (str): Prefix for log files.
        expired (int): Number of days after which log files are considered expired and deleted.
        namespace (str): Namespace for the logger, useful for differentiating logs in larger applications.
        location (str): Specifies whether to log the filename or pathname in the logs.
        style (str): Style of the log format, can be '[', '-', or ':'.

    Example:
        logger = Logger(level='DEBUG', console='INFO', file='ERROR', root='logs', file_prefix='app')
        logger.info("This is an info message.")
    """

    VALID_LOG_LEVELS = ['debug', 'info', 'warning', 'error', 'critical', 'exception']

    def __init__(
            self,
            level='DEBUG',
            console='',
            file='',
            root='logs',
            file_prefix='',
            expired=-1,
            namespace='',
            location='',  # 'filename' or 'pathname' or ''
            style='-'  # '[' or '-' or ':'
        ):
        self.level = level
        self.console = console.upper() if console else ''
        self.file = file.upper() if file else ''
        if file:
            self.root = root
            self.file_prefix = file_prefix + '_' if file_prefix != '' else ''
            self.expired = expired
            self.delete_expired_log()

        self.namespace = namespace

        if location and sys.version_info < (3, 8):
            # stacklevel is only supported in Python 3.8 and above
            print("Warning: 'location' parameter is only supported in Python 3.8 and above. Setting location to False.")
            self.location = ''
        elif location not in ['filename', 'pathname', '']:
            self.location = ''
        else:
            self.location = location
        
        self.style = style
        if self.style not in ['[', '-', ':']:
            print(f"Warning: Invalid style '{self.style}' provided. Defaulting to '['.")
            self.style = '['

        self.day = time.strftime('%Y-%m-%d')
        self.setup()

    def __getattr__(self, name):
        """
        Allows dynamic access to standard logging methods like debug, info, etc.
        
        Raises:
            AttributeError: If the attribute is not a recognized log level.
        """
        if name in self.VALID_LOG_LEVELS:
            def log_method(msg, *args, **kwargs):
                self.check()
                if self.location and 'stacklevel' not in kwargs:
                    # Since now the logger is a class attribute, 
                    # we need to set stacklevel to 2
                    # in order to point to the caller of the log method.
                    kwargs['stacklevel'] = 2
                getattr(self.logger, name)(msg, *args, **kwargs)
            return log_method
        raise AttributeError(f"'{name}' is not a valid logging level. Valid levels are: {', '.join(self.VALID_LOG_LEVELS)}")
 
    def setup(self):
        """
        Create or recreate the logging handlers based on the current configuration.
        This is called internally to handle log rotation.
        """
        # clear handlers if existing logger
        self.shutdown()

        # create a logger obj and set level
        # use __name__ to avoid use root logger
        if self.namespace:
            if self.namespace == 'root':
                self.logger = logging.getLogger()
            else:
                self.logger = logging.getLogger(self.namespace)
        else:
            self.logger = logging.getLogger(__name__)
        
        # remove all existing handlers to prevent duplicates
        # including the default handler from ensure_default_logging 
        for h in list(self.logger.handlers):
            h.close()
            self.logger.removeHandler(h)

        self.logger.setLevel(getattr(logging, self.level))
        
        # create a formatter obj and add it into the handlers
        self.formatter = logging.Formatter(self.get_format())
        # self.formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        
        # create a console handler
        if self.console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.console))
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
            
        # create a file handler
        if self.file:
            if not os.path.isdir(self.root):
                os.mkdir(self.root)
            file_handler = logging.FileHandler(f"{self.root}/{self.file_prefix}{self.day}.log")
            file_handler.setLevel(getattr(logging, self.file))
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

        self.logger.propagate = False  # prevent log messages from propagating to the root logger

    def get_format(self):
        """
        Returns the log format string based on the logger's configuration.
        """
        _format = []
        _format.append('%(asctime)s')
        _format.append('%(levelname)s')
        if self.location:
            # location can be 'filename', 'pathname', or ''
            # %(filename)s is the name of the file without the path
            # %(pathname)s is the full path of the file
            # %(lineno)d is the line number in the file where the log was called
            _format.append(f'%({self.location})s:%(lineno)d')
        _format.append('%(message)s')

        if self.style == '[':
            _format = [f'[{part}]' for part in _format[:-1]] + [_format[-1]]
            return ' '.join(_format)
        elif self.style == '-':
            return ' - '.join(_format)
        elif self.style == ':':
            return ':'.join(_format)
    
    def delete_expired_log(self):
        """
        Delete log files that are older than the 'expired' days setting.
        """
        if not self.file:
            return
        
        if self.expired < 0:
            return
        
        today = datetime.date.today()
        log_dir = Path(self.root)
        if not log_dir.exists():
            return

        for file_path in log_dir.iterdir():
            if file_path.suffix == '.log':
                try:
                    file_date_str = file_path.stem.split('_')[-1]
                    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    if (today - file_date).days > self.expired:
                        file_path.unlink()
                        print(f'delete expired log: {file_path}', flush=True)
                except ValueError:
                    print(f"Skipped invalid log file: {file_path}", flush=True)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}", flush=True)

    def check(self):
        """
        Check if the log file needs to be rotated based on the current date.
        """
        if time.strftime('%Y-%m-%d') != self.day:
            self.day = time.strftime('%Y-%m-%d')
            self.setup()
            self.delete_expired_log()
        
    def shutdown(self):
        """
        Properly close and remove all handlers from the logger.
        """
        if not hasattr(self, 'logger'):
            return
        for handler in self.logger.handlers:
            print(handler, flush=True)
            handler.close()
            self.logger.removeHandler(handler)