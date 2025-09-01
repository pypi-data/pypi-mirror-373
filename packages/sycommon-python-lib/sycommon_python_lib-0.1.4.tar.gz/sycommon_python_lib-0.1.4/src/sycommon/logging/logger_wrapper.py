from sycommon.logging.kafka_log import SYLogger


class LoggerWrapper:
    def __init__(self):
        self.logger = SYLogger

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)


def get_logger_wrapper():
    return LoggerWrapper()
