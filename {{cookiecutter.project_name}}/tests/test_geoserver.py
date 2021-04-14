import json
import pytest
import pathlib
from aiohttp import web


from geoserver import __version__

from core.models.mongodb import MongoModel
from core.auth import SignOnHandler
from core.vertebral import Vertebral
from core.middlewares import vertebral_middelware

import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage


PREFIX = "/geoserver/api/v1/"
BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config/config.yml"

MIDDLEWARES = [
    vertebral_middelware,
]


@pytest.fixture
def cli(loop, aiohttp_client):
    vertebra = Vertebral()
    logger = vertebra.getLogger()

    app = web.Application(middlewares=MIDDLEWARES, logger=logger)
    # app = web.Application(logger=logger)

    aiohttp_session.setup(app=app, storage=EncryptedCookieStorage(
        b'Thirty  two  length  bytes  key.'))

    app.router.add_post(PREFIX+'signon', SignOnHandler)

    app['config'] = vertebra.load_config(DEFAULT_CONFIG_PATH)

    app['mongo'] = MongoModel().setup_client(app['config']['mongo']['uri'])

    app['vertebra'] = vertebra

    return loop.run_until_complete(aiohttp_client(app))


async def test_auth_signon_ok(cli):
    data = {
        "key": "xxx",
        "resource": "yyy",
        "mode": "sha256",
        "nonce": "1234567890",
        "payload": {
        }
    }

    resp = await cli.post(PREFIX+'signon', data=json.dumps(data),
                          headers={"Content-Type": "application/json"},)

    json_response = await resp.json()

    assert resp.status == 200 and json_response['type'] == \
           "success" and json_response['status'] == 200


async def test_auth_signon_fail(cli):
    data = {
        "key": "FAKE_xxx",
        "resource": "yyy",
        "mode": "sha256",
        "nonce": "1234567890",
        "payload": {
        }
    }

    resp = await cli.post(PREFIX+'signon', data=json.dumps(data),
                          headers={"Content-Type": "application/json"},)

    json_response = await resp.json()

    assert resp.status == 200 and json_response['type'] == \
           "error" and json_response['status'] == 401


async def test_auth_signon_bad_request(cli):
    data = {
        "FAKE_key": "xxx",
        "resource": "yyy",
        "mode": "sha256",
        "nonce": "1234567890",
        "payload": {
        }
    }

    resp = await cli.post(PREFIX+'signon', data=json.dumps(data),
                          headers={"Content-Type": "application/json"},)

    json_response = await resp.json()

    assert resp.status == 422 and json_response['type'] == \
           "error" and json_response['status'] == 400


async def test_auth_signon_bad_response(cli):
    data = {
        "key": "xxx",
        "resource": "yyy",
        "mode": "sha256",
        "nonce": "1234567890",
        "payload": {
        }
    }

    # TODO SE TIENE QUE MOCKEAR Y DEVOLVER UN RESPONSE MALO
    resp = await cli.post(PREFIX + 'signon', data=json.dumps(data),
                          headers={"Content-Type": "application/json"}, )

    json_response = await resp.json()

    json_response['FAKE_status'] = "XXXXXXX"

    # assert resp.status == 200 and json_response['type'] ==
    # "error" and json_response['status'] == 403

    assert resp.status == 200 and json_response['type'] == \
           "success" and json_response['status'] == 200


'''
def test_validation_exception_middleware(swagger_docs, aiohttp_client):
    @web.middleware
    async def middleware(request, handler):
        try:
            return await handler(request)
        except RequestValidationFailed as exc:
            assert exc.errors == {"query": "value should be type of int"}
            raise exc

    async def handler(request):
        """
        ---
        parameters:

          - name: query
            in: query
            required: true
            schema:
              type: integer

        responses:
          '200':
            description: OK.
        """
        return web.json_response()

    swagger = swagger_docs()
    swagger._app.middlewares.append(middleware)
    swagger.add_get("/r", handler)

    client = await aiohttp_client(swagger._app)

    params = {"query": "abc"}
    resp = await client.get("/r", params=params)
    assert resp.status == 400
'''


def test_version():
    assert __version__ == '0.1.0'

