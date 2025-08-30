import logging
import os

from dotenv import load_dotenv


load_dotenv()

def to_bool(value: any) -> bool:
    if value is None:
        return False

    return str(value).lower() == "true"


def setup_logging(log_file: str=None, log_level: str="INFO") :
    import colorlog

    logging_level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    }

    console_formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(white)s%(message)s',
        log_colors=log_colors,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        else:
            os.remove(log_file)

        file_formatter = logging.Formatter(
            '%(asctime)s -%(levelname)-8s  %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    logger.setLevel(logging_level)

    logging.info(f"🛠️ XGA_LOGGING is initialized, log_level={log_level}, log_file={log_file}")

def setup_env_logging():
    log_enable = to_bool(os.getenv("LOG_ENABLE", True))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "log/xgatools.log")
    if log_enable :
        setup_logging(log_file, log_level)

