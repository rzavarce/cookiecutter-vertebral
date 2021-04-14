import pathlib
import aioreloader
from aiohttp import web

from .vertebral import Vertebral

from core.models.mongodb import MongoModel

from .middlewares import vertebral_middelware

from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config/config.yml"

MIDDLEWARES = [
    vertebral_middelware,
]


def start():
    """Start Service."""
    main()


def main():
    """
    Initialize and Create an application instance.

    During initialization an application is created, set it with config object,
    initialize a mongo db and register routes

    Function is called when the module is run directly
    """

    vertebra = Vertebral()
    logger = vertebra.getLogger()
    config = vertebra.load_config(DEFAULT_CONFIG_PATH)

    app = web.Application(middlewares=MIDDLEWARES, logger=logger)
    aioreloader.start()

    setup(app,
          EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))

    app["config"] = config
    app["logger"] = logger  # TODO Probar bien queo que no hace falta

    app['prefix'] = vertebra.set_path_prefix()

    # Set Swagger and Openapi3
    swagger = vertebra.set_swagger_config(app)
    swagger.validate = config['swagger']["enabled"]

    # Load Routes, Match Endpoint with Handller
    vertebra.load_routes(swagger)

    # Setup Mongo Client
    app["mongo"] = \
        MongoModel().setup_client(config['mongo']['uri'],
                                  config['mongo']['db_name'])

    # Load Load Initial authentication Data if is necesary
    # await vertebra.load_initial_auth_data(app["mongo"])

    # Set vertebra
    app["vertebra"] = vertebra

    logger.info(f'All Systems are ready')
    web.run_app(app, host=config["host"], port=config['port'])
