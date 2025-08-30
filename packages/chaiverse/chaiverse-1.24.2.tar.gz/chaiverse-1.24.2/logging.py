from functools import partial
from multiprocessing import Queue
import requests

import logging_loki
from uvicorn.logging import DefaultFormatter


class LokiHeaderSessionCreator():
    session = requests.Session()

    def post(self, url, json):
        return self.session.post(url=url, json=json, headers={
            'X-Scope-OrgID': 'guanaco'
        })

    def close(self):
        self.session.close()

logging_loki.emitter.LokiEmitterV1.session_class = LokiHeaderSessionCreator


def get_service_logger_config(service_name, loki_base_url):
    class LokiLogHandler(logging_loki.LokiQueueHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                url=f"{loki_base_url}/loki/api/v1/push",
                tags={"service_name": service_name},
                version="1",
            )

        def emit(self, record):
            if "Exception in ASGI application" in record.message:
                exception = record.exc_info[1]
                if getattr(exception, "exceptions", None):
                    exception = exception.exceptions[0]
                record.message = repr(exception)
                record.msg = repr(exception)
            super().emit(record)


    logging_config  = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
            "nocarets": {
                "()": "chaiverse.logging.NoCaretsExceptionFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            }
        },
        "handlers": {
            "default": {
                "formatter": "nocarets",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }
    if loki_base_url:
        logging_config["handlers"]["loki"] = {
            "formatter": "nocarets",
            "()": partial(LokiLogHandler, Queue(1)),
            "stream": "ext://sys.stderr",
            # Must specify this to avoid weird logging library error
            # on Python 3.12.0 (but not later versions)
            #"handlers": {}
        }
        logging_config["loggers"]["uvicorn"]["handlers"].append("loki")
        logging_config["loggers"]["uvicorn.access"]["handlers"].append("loki")
    return logging_config


class NoCaretsExceptionFormatter(DefaultFormatter):
    # This is necessary, as GCP cannot parse Python stacktraces with carets
    def formatException(self, exc_info):
        stack_trace = super(NoCaretsExceptionFormatter, self).formatException(exc_info)
        split_trace = stack_trace.split("\n")
        split_trace = [line for line in split_trace if "^" not in line]
        stack_trace = "\n".join(split_trace)
        return stack_trace
