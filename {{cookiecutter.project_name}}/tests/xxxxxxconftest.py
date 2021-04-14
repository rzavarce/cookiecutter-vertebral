import pytest
import aiohttp
from ..coro_logger import CoroLogger
# from sipay_utils.aiohttp.test import cm_fake_request
from unittest.mock import AsyncMock, MagicMock
import configparser
import contextlib
import logging
import uuid


@contextlib.asynccontextmanager
async def cm_fake_request(loop):
    fake_config = configparser.ConfigParser()
    fake_config.add_section('logger')
    fake_config.add_section('mstk_service')
    fake_config['mstk_service']['master_password'] = '123123123'
    fake_config['mstk_service']['url'] = 'http://mstk/{endpoint}'
    request = make_mocked_request(
        'POST',
        '/',
        app=dict(logger=CoroLogger(logging.getLogger(__name__)),
                 name='fake_app_test',
                 raw_version='0.0.0',
                 config=fake_config,
                 http_session=aiohttp.ClientSession()))
    request.uuid = uuid.uuid4().hex
    request['request_id'] = uuid.uuid4().hex
    request._logger = logging.getLogger(__name__)
    request.logger = CoroLogger(request._logger)

    from sipay_utils.aiohttp.logging import APP
    APP.set(request.app)
    yield request


@pytest.fixture
async def fake_request(loop):
    async with cm_fake_request(loop) as fake_req:
        mongo = AsyncMock()
        mongo_db = mongo['trop']
        fake_req.app['mongo_db'] = mongo_db

        yield fake_req
