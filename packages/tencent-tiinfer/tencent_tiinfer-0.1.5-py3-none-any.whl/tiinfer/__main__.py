import logging
import sys

from mosec import Server

import tiinfer

logger_formatter = "%(asctime)s %(levelname)s    %(module)s:%(lineno)d    %(message)s"

logging.basicConfig(stream=sys.stdout, format=logger_formatter, level=logging.DEBUG)

if __name__ == "__main__":
    server = Server()
    for worker_args in tiinfer.load_workers():
        server.append_worker(**worker_args)
    server.run()
