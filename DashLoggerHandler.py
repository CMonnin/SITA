# source: https://stackoverflow.com/questions/52057540/redirecting-pythons-console-output-to-dash

import logging


class DashLoggerHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.queue = []

    def emit(self, record):
        msg = self.format(record)
        self.queue.append(msg)
