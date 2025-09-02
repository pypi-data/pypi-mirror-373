import logging

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages"""
    
    COLORS = {
        'DEBUG': '\033[0;36m',    # Cyan
        'INFO': '\033[0;32m',     # Green
        'WARNING': '\033[0;33m',  # Yellow
        'ERROR': '\033[0;31m',    # Red
        'CRITICAL': '\033[0;37;41m', # White on Red
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logger():
    """Set up and configure the logger with color formatting.
    
    This should be called once at the start of the application.
    """
    # Create handler
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter('%(levelname)s: %(message)s'))
    
    # Configure root logger
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    
    # Remove any existing handlers to avoid duplicate messages
    for h in logging.root.handlers[:-1]:
        logging.root.removeHandler(h)

# Initialize logger when module is imported
setup_logger() 