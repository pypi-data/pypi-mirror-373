import logging, logging.handlers, os
import datetime, sys, re

from etiket_client.settings.folders import get_log_dir

def set_up_logging(name, etiket_client_version):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    logger.propagate = True

    log_file = os.path.join(get_log_dir(), f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}_etiket_client.{os.getpid()}.log')
    handler = FileSizeLimitedTimedRotatingFileHandler(log_file, when="midnight", backupCount=14)
    handler.suffix = "%Y%m%d"
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s \n\n')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.warning("Logging started, using with the following versions : python: %s, etiket_client %s", sys.version, etiket_client_version)

    cleanup_old_logs(handler.baseFilename)

def set_up_sync_logger(name):
    log_file = os.path.join(get_log_dir(), f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}_etiket_sync.{os.getpid()}.log')
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    logger.propagate = True

    # little bit hackey but it works...
    if len(logger.handlers) == 1:
        f_name = logger.handlers[0].baseFilename
        logger.handlers[0].flush()
        logger.handlers[0].close()
        logger.handlers.clear()

        os.rename(os.path.join(get_log_dir(), f_name), log_file)
    else:
        logger.handlers.clear()
    
    handler = FileSizeLimitedTimedRotatingFileHandler(log_file, when="midnight", backupCount=10)
    handler.suffix = "%Y%m%d"
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s \n\n')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    cleanup_old_logs(handler.baseFilename)
    return logger

def cleanup_old_logs(baseFilename : str):
    try:
        log_dir = os.path.dirname(baseFilename)
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=14)

        file_name_pattern_1 = re.compile(r"^(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})_(.+)\.(\d+)\.log$")
        file_name_pattern_2 = re.compile(r"^(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})_(.+)\.(\d+)\.log.(\d{8})$")

        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            if not os.path.isfile(file_path):
                continue
            
            match_1 = file_name_pattern_1.match(filename)
            match_2 = file_name_pattern_2.match(filename)

            if match_1:
                file_time = datetime.datetime.strptime(match_1.group(1), "%Y_%m_%d_%H_%M_%S")
            elif match_2:
                file_time = datetime.datetime.strptime(match_2.group(4), "%Y%m%d")
            else:
                continue
            
            if file_time < cutoff:
                os.remove(file_path)
    except Exception:
        logging.getLogger(__name__).exception("Failed to clean up old log files")

class FileSizeLimitedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None, maxLines=10000):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        self.maxSize = 1024 * 1024 * 10 # 10 MB
        self.currentSize = 0

    def emit(self, record : logging.LogRecord):
        try:
            if self.currentSize < self.maxSize:
                log_entry = self.format(record) + '\n'
                self.currentSize += len(log_entry.encode('utf-8'))
                super().emit(record)
            else:
                pass
        except Exception:
            self.handleError(record)

    def doRollover(self) -> None:
        self.currentSize = 0
        return super().doRollover()
