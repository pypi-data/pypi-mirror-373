import logging


class ConsoleHandler(logging.Handler):
    def __init__(self, print_function):
        super().__init__()
        self.print_function = print_function

    def emit(self, record):
        msg = self.format(record)
        self.print_function(msg)


def configure_logging(print_function, level):

    if level.lower() == "debug":
        level = logging.DEBUG
    elif level.lower() == "info":
        level = logging.INFO
    elif level.lower() == "warning":
        level = logging.WARNING
    elif level.lower() == "error":
        level = logging.ERROR

     # Define ANSI escape sequences for colors
    COLORS = {
        'CRITICAL': '\033[91m',  # Red
        'ERROR': '\033[91m',     # Red
        'WARNING': '\033[93m',   # Yellow
        'INFO': '\033[92m',      # Green
        'DEBUG': '\033[94m',     # Blue
        'RESET': '\033[0m'       # Reset to default color
    }

        # Set up the logging configuration with color formatting
    class ColorFormatter(logging.Formatter):
        def format(self, record):
            levelname = record.levelname
            name = record.name
            message = super().format(record)
            color = COLORS.get(levelname, COLORS['RESET'])
            name = f"{color}[{name}]{COLORS['RESET']}:"
            pre = f"{color}{levelname}{COLORS['RESET']}:"
            return f"{pre:17}{name:20}{message}"

        # Get root logger
    root_logger = logging.getLogger()
    
    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set level for all logging
    root_logger.setLevel(level)
    
    # Add our custom handler
    handler = ConsoleHandler(print_function)
    formatter = ColorFormatter()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)