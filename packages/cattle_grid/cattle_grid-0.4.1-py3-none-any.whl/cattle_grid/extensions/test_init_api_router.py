from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from fastapi.responses import HTMLResponse

from . import Extension
from .load import add_routes_to_api


def test_api_router():
    ext = Extension("test", api_prefix="/test", module=__name__)
    result = {"extension": "yes"}

    @ext.get("/")
    async def root_path():
        return result

    ext.configure({})

    app = FastAPI()
    add_routes_to_api(app, [ext])

    test_client = TestClient(app)

    response = test_client.get("/test")

    assert response.status_code == 200

    data = response.json()

    assert data == result


def test_api_router_set_response_class():
    ext = Extension("test", api_prefix="/test", module=__name__)

    @ext.get("/", response_class=HTMLResponse)
    async def root_path():
        return """<html><body>Hi</body></html>"""

    app = FastAPI()
    add_routes_to_api(app, [ext])

    test_client = TestClient(app)

    response = test_client.get("/test")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.text == """<html><body>Hi</body></html>"""


def test_api_router_include_router():
    ext = Extension("test", api_prefix="/test", module=__name__)
    result = {"extension": "yes"}

    router = APIRouter()

    @router.get("/")
    async def root_path():
        return result

    ext.include_router(router)

    ext.configure({})

    app = FastAPI()
    add_routes_to_api(app, [ext])

    test_client = TestClient(app)

    response = test_client.get("/test")

    assert response.status_code == 200

    data = response.json()

    assert data == result
