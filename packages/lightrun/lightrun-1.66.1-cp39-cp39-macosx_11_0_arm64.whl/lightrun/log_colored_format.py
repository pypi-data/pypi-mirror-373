import logging

from . import lightrun_config


class ColoredDynamicConsoleFormatter(logging.Formatter):
    def __init__(self):
        super(logging.Formatter, self).__init__()
        self.is_colored_console = lightrun_config.GetBooleanConfigValue("dynamic_log_is_colored_console")
        self.base_format = lightrun_config.config.get("dynamic_log_console_handler_format")

        # These are ansi colors
        # You can look it up here:
        # https://gist.github.com/vicenteguerra/e81189c7242631cd0832ccbc6f1976f9
        blue = "\x1b[94m"
        green = "\x1b[32m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        reset = "\x1b[0m"

        self.FORMATS = {
            logging.DEBUG: blue + self.base_format + reset,
            logging.INFO: green + self.base_format + reset,
            logging.WARNING: yellow + self.base_format + reset,
            logging.ERROR: red + self.base_format + reset,
        }

    def format(self, record):
        if self.is_colored_console:
            log_fmt = self.FORMATS.get(record.levelno)
        else:
            log_fmt = self.base_format

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
