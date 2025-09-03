from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
from functools import partial
import logging
from importlib import import_module
import inspect
from io import UnsupportedOperation
from mock import patch
from multiprocessing import Process, get_context
import os
from random import randrange
import requests
from shutil import rmtree
import signal
import sys
from threading import Thread
from typing import List, Optional
import time
import uuid

import fastapi as fa
from prometheus_client import multiprocess, CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Extra, Field
import uvicorn

from chaiverse.logging import get_service_logger_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Uvicorn uses spawn as the default multiprocessing method for
# compatibility with Windows. But this is slower and requires pickling.
# So we tell it to use fork instead.
uvicorn._subprocess.spawn = get_context("fork")


class ChaiverseServerGracefulShutdown(Exception):
    pass


class UvicornServer(uvicorn.Server):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = kwargs["config"]
        if self.config.workers == 1:
            signal.signal(signal.SIGTERM, self.graceful_shutdown)
            self.process = Thread(target=self.run)
        else:
            self.process = Process(target=self._multiprocess_target)

    def install_signal_handlers(self):
        if self.config.workers > 1:
            super().install_signal_handlers()

    @contextmanager
    def run_in_process(self):
        self.process.start()
        try:
            yield self
        finally:
            self.terminate()

    def terminate(self):
        self.should_exit = True
        if self.config.workers > 1:
            self.process.terminate()
        self.process.join()

    def graceful_shutdown(self, signum, frame):
        raise ChaiverseServerGracefulShutdown

    def _multiprocess_target(self):
        socket = self.config.bind_socket()
        multiprocess = uvicorn.supervisors.Multiprocess(
            config=self.config,
            target=self.run,
            sockets=[socket]
        )
        multiprocess.run()
        return multiprocess


class ChaiverseServerConfig(BaseModel):
    name: str = "chaiverse_server"
    port: int = 8080
    host: str = "0.0.0.0"
    workers: int = 1
    environment_variables: dict = Field(default_factory=dict)
    # Set to a positive number to limit the number of requests the uvicorn
    # process can handle. Used to avoid memory leaks. Random jitter is added
    # to ensure replicas don't shutdown at same time.
    limit_max_requests: int = -1
    log_level: str = "info"
    loki_base_url: str = ""
    # Specify the buckets to use when exporting route latencies to
    # prometheus histogram. This is a configurable option as we want
    # to avoid publishing too many time series to prometheus if we
    # don't need them
    prometheus_latency_buckets: List[float] = [0.1, 0.5, 1]
    prometheus_path: Optional[str] = None

    class Config:
        extra = Extra.allow

    @classmethod
    def from_app(cls, app):
        config = cls._get_config_from_app(app)
        return cls(**config)

    @classmethod
    def from_request(cls, request: fa.Request):
        return cls.from_app(request.app)

    @classmethod
    def _get_config_from_app(cls, app: fa.FastAPI):
        config = getattr(app.state, "chaiverse_server_config", None)
        config = config.dict() if config else {}
        return config


class ChaiverseServer:
    def __init__(self, fastapi_app: fa.FastAPI, config):
        self.config = config
        self.fastapi_app_factory = partial(self._prepare_fastapi, fastapi_app)

    @contextmanager
    def serve(self):
        try:
            logger.info(f"Starting server {self.config.name}.")
            with self._start() as server:
                logger.info(f"Waiting for server {self.config.name} to be ready.")
                start = time.time()
                while not self._server_ready:
                    pass
                duration = round(time.time() - start, 2)
                logger.info(f"Server {self.config.name} ready after {duration}s")
                yield server
        finally:
            logger.info(f"Shutting down server {self.config.name}.")

    @contextmanager
    def _start(self, **kwargs):
        config = {
            "app": self.fastapi_app_factory,
            "factory": True,
            "port": self.config.port,
            "host": self.config.host,
            "workers": self.config.workers,
            "log_config": self.logging_config,
            "log_level": self.config.log_level,
        }
        if self.config.limit_max_requests > 0:
            config.update({"limit_max_requests": self.limit_max_requests})
        config = uvicorn.Config(**config)
        server = UvicornServer(config=config)
        with self._environment_patch(), server.run_in_process():
            yield server

    @property
    def logging_config(self):
        return get_service_logger_config(self.config.name, self.config.loki_base_url)

    @property
    def _server_ready(self):
        try:
            requests.get(f"http://localhost:{self.config.port}/test_endpoint")
            is_ready = True
        except requests.exceptions.ConnectionError:
            logger.info(f"{self.config.name} not yet ready!")
            is_ready = False
        return is_ready

    def _prepare_fastapi(self, fastapi_app):
        # Install dependency solving patch (see comment in function)
        _patch_fastapi_dependency_solver()
        # Allow fastapi app to be passed in as import string
        # to enable specifying app via environment variable
        # in production
        if isinstance(fastapi_app, str):
            fastapi_app = _resolve_fastapi_app(fastapi_app)
        _install_general_exception_handler(fastapi_app)
        _install_prometheus_instrumentator(
            fastapi_app,
            self.config.name,
            self.config.prometheus_latency_buckets,
            self.config.prometheus_path
        )
        fastapi_app.state.chaiverse_server_config = self.config
        return fastapi_app

    def _environment_patch(self):
        environment_patch = (
            patch.dict(os.environ, self.config.environment_variables)
            if self.config.environment_variables
            else nullcontext()
        )
        return environment_patch

    @property
    def limit_max_requests(self):
        base_limit = self.config.limit_max_requests
        adjusted_limit = randrange(base_limit, int(base_limit + 0.25 * base_limit))
        return adjusted_limit


def _install_general_exception_handler(fastapi_app):
    @fastapi_app.exception_handler(Exception)
    def runtime_exception_handler(request: fa.Request, exc: Exception):
        return exception_response(500, exc)


def _install_prometheus_instrumentator(fastapi_app, name, latency_buckets=[0.1, 0.5, 1], path=None):
    if _should_install_prometheus_middleware(fastapi_app):
        prometheus_dir = path if path else f"/tmp/prometheus/{uuid.uuid4()}"
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = prometheus_dir
        if not os.path.exists(prometheus_dir):
            os.mkdir(prometheus_dir)

        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)

        instrumentator = Instrumentator()
        instrumentator.instrument(
            fastapi_app,
            metric_subsystem=name,
            latency_lowr_buckets=latency_buckets
        )
        instrumentator.expose(fastapi_app)

        # Change the behaviour of the instrumentation middleware so that it
        # returns fully interpolated paths in the prometheus labels instead of
        # leaving them uninterpolated
        middleware = [middleware for middleware in fastapi_app.user_middleware if "Prometheus" in middleware.cls.__name__]
        middleware = middleware[0]
        def _get_handler(self, request):
            return request.url.path, True
        middleware.cls._get_handler = _get_handler


def _should_install_prometheus_middleware(fastapi_app):
    # This avoids a bug on later version of fastapi where it crashes
    # if you try to add a middleware more than once (useful in testing)
    should_add_middleware = True
    if fastapi_app.middleware_stack is not None:
        should_add_middleware = False
    return should_add_middleware


def exception_response(status_code, exc):
    if (
        getattr(exc, "message", None)
        and "unhandled errors in a TaskGroup" in exc.message
    ):
        exc = exc.exceptions
    return fa.responses.JSONResponse(
        status_code=status_code, content={"detail": str(exc)}
    )


def _resolve_fastapi_app(fastapi_app):
    import_path, app = fastapi_app.rsplit(".", 1)
    module = import_module(import_path)
    fastapi_app = getattr(module, app)
    return fastapi_app


def _patch_fastapi_dependency_solver():
    # FastAPI will resolve all dependencies that are not coroutines in a
    # separate thread (see solve_depdendencies in fastapi/depdendencies/utils.py)
    # However for low-overhead code such as class instantiation this is incredibly
    # wasteful at best, and at worst can lead to significant overhead in
    # latencies.
    # In particular, class-based views (which we call controllers in this
    # codebase) from fastapi_utils are treated as such dependencies, so
    # everytime a request hits a controller, there is an additional overhead
    # from a new thread being spun.
    # Here we patch fastapi to handle class depdenencies synchronously, and
    # avoid  this overhead.
    # See also https://github.com/fastapi/fastapi/discussions/7546 for
    # benchmarks showing the slowdown.
    from starlette.concurrency import run_in_threadpool as starlette_run_in_threadpool

    async def run_in_threadpool(call, **kwargs):
        if inspect.isclass(call):
            result = call(**kwargs)
        else:
            result = await starlette_run_in_threadpool(call, **kwargs)
        return result

    fa.dependencies.utils.run_in_threadpool = run_in_threadpool
