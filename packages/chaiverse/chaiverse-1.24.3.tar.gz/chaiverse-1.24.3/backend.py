import contextlib
from mock import patch, Mock
import pkgutil
from typing import List, Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from chaiverse.chaiverse_server import _resolve_fastapi_app, _install_prometheus_instrumentator
from chaiverse.database import MockDatabase


class BackendService(BaseModel):
    path: str
    url_patches: Optional[List] = []
    database_patches: Optional[List] = []
    code_patches: Optional[List] = []
    client_patches: Optional[List] = []

    @property
    def name(self):
        return self.path.split(".")[0]


# Mock background tasks as it can cause end to end tests
# to finish early (due to async behaviour)
class MockBackgroundTasks:
    def add_task(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class MockThreadPoolExecutor():
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def submit(self, func, *args, **kwargs):
        return func(*args, **kwargs)


@contextlib.contextmanager
def run_servers(backend_services, mock_database=True, raise_server_exceptions=True, config=None):
    backend = FastAPI()
    # Mount all the microservices as subapps on the main fastapi app
    backend = mount_backends(backend, backend_services, config)
    # Patches to point to the launched backend
    client_patches = []
    mock_database = MockDatabase() if mock_database else None
    # Patches to install before launching the backend
    patches = get_backend_patches(backend_services, mock_database)
    with install_patches(patches), TestClient(backend, raise_server_exceptions=raise_server_exceptions) as client:
    # Patches to install that point to the test client
        client_patches = get_client_patches(backend_services, client)
        with install_patches(client_patches):
            yield client


def mount_backends(backend, backend_services, config):
    for service in backend_services:
        fastapi_app = _resolve_fastapi_app(service.path)
        fastapi_app.state.chaiverse_server_config = config
        _install_prometheus_instrumentator(fastapi_app, service.name)
        backend.mount(f"/{service.name}", fastapi_app)
    return backend


def get_client_patches(backend_services, client):
    client_patches = []
    for service in backend_services:
        service_client_patches = []
        for client_patch in service.client_patches:
            obj = pkgutil.resolve_name(client_patch)
            if callable(obj):
                client_patch = patch(client_patch, return_value=client)
            else:
                client_patch = patch(client_patch, client)
            client_patches.append(client_patch)
    return client_patches


def get_backend_patches(backend_services, mock_database):
    patches = []
    for service in backend_services:
        patches += get_service_patches(service, mock_database)
    return patches


def get_service_patches(service, mock_database):
    patches = []
    for url_patch in service.url_patches:
        url_patch = patch(url_patch, f"/{service.name}")
        patches.append(url_patch)
    if mock_database:
        for database_patch in service.database_patches:
            database_patch = patch(database_patch, mock_database)
            patches.append(database_patch)

    for code_patch in service.code_patches:
        patches.append(code_patch)
    return patches


@contextlib.contextmanager
def install_patches(patches):
    with contextlib.ExitStack() as stack:
        for mock_patch in patches:
            stack.enter_context(mock_patch)
        yield
