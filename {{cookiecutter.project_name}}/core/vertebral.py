import re
import json
import logging
import hmac
import base64
import hashlib

import jsonschema
from uuid import uuid4
from aiohttp import web

from pathlib import Path
from yaml import safe_load
from http import HTTPStatus
from datetime import datetime, timezone

from {{cookiecutter.project_name}}.routes import setup_routes, EXCLUDED_ROUTES
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings
from .models.auth import Auth

from .catalogs.response import CATALOG

METHODS_ALLOWED = ["post", "get"]

RESERVED = frozenset(
    (
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "id",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    )
)


class Vertebral:

    def __init__(self):
        self.config: dict = {}
        self.reserved: frozenset = RESERVED
        self.logger = logging
        self.exclude_routes: list = EXCLUDED_ROUTES
        self.methods_allowed: list = METHODS_ALLOWED
        self.catalog = CATALOG
        self.prefix: str = ""

    def load_config(self, config_path: Path) -> dict:
        """
        Load config file  from a given path.

        -----------------
        Args:
            config_path (Parh): Path to config YAML file.
        Returns:
            config (dict):  Config file loaded
        """

        try:
            with config_path.open() as config_file:
                self.config: dict = safe_load(config_file)
            self.logger.info(f'Config File has been loaded')
        except:
            self.logger.error("Config file no exist, please check config path",
                              extra={"config_path": config_path})
        self.set_logger_in_file()
        return self.config

    def set_swagger_config(self, app):
        """
        Swagger configuration parameters loader

        -----------------
        Args:
            app (web.app): Aiohhtp web app.
        Returns:
            SwaggerDocs:  SwaggerDocs configuration loaded

        """

        swagger_config = self.config['swagger']

        return SwaggerDocs(
            app,
            title=swagger_config["title"],
            version=swagger_config["version"],
            swagger_ui_settings=SwaggerUiSettings(
                path=swagger_config["path"],
                layout=swagger_config["layout"],
                deepLinking=swagger_config["deepLinking"],
                displayOperationId=swagger_config["displayOperationId"],
                defaultModelsExpandDepth=swagger_config[
                    "defaultModelsExpandDepth"],
                defaultModelExpandDepth=swagger_config[
                    "defaultModelExpandDepth"],
                defaultModelRendering=swagger_config["defaultModelRendering"],
                displayRequestDuration=swagger_config["displayRequestDuration"],
                docExpansion=swagger_config["docExpansion"],
                filter=swagger_config["filter"],
                showExtensions=swagger_config["showExtensions"],
                showCommonExtensions=swagger_config["showCommonExtensions"],
                supportedSubmitMethods=swagger_config["test"].split(","),
                validatorUrl=swagger_config["validatorUrl"],
                withCredentials=swagger_config["withCredentials"],
            ),
        )

    def load_routes(self, app):
        """
        Register existing routes in the app instance.

        -----------------
        Args:
            app (web.app) : application instance
        Returns:
            No return anythings
        """
        routes = setup_routes()
        final_routes = []

        for route in routes:
            if route[0].lower() in self.methods_allowed:
                final_routes.append(
                    web.post(self.prefix + route[1], route[2]))
            else:
                self.logger.error('Method is not allowed, route no setted',
                                  extra={"route": {
                                      "method": route[0].lower(),
                                      "path": self.prefix + route[1]}})
        app.add_routes(final_routes)


    async def load_initial_auth_data(self, clientdb):
        """
        Register existing routes in the app instance.

        -----------------
        Args:
            clientdb (web.app) : application instance
        Returns:
            No return anythings
        """
        auth = Auth(clientdb)
        print()
        print("Entro para chequear los datos en la bbdd")
        print()
        load = await auth.load_initial_data()
        if load:
            print()
            print("cargo la da data inicial")
            print()
            self.logger.error('Load Initial authentication Data')

        del auth

    def set_path_prefix(self):
        """
        Set path prefix atributte

        -----------------
        Args:
            No accept anythins
        Return:
            prefix (str): Set and retunr path prefix
        """
        app_name = self.config["app_name"]
        version = self.config["version"]
        self.prefix = f'/{app_name}/api/v{version}/'
        return self.prefix

    def is_exclude(self, request):
        """Check if a request is inside in path exclude list.

        Its validate if path request is out of autentification

        -----------------
        Args:
            request (objc): Aiohttp Web Request
        Returns:
            status (bool):  Path Validation status
        """
        for pattern in self.exclude_routes:
            if re.fullmatch(pattern, request.path):
                return True
        return False

    def set_response(self, data: dict):
        """ Take a response data, search a key inside Response schema and set
        response data

        -----------------
        Args:
            data (dict): Data Dictionary to set in response
        Returns:
            response (dict):  Response data serializered
        """
        key = data['key']
        response = self.catalog.get(key, False)
        if response:
            response["payload"] = data["payload"]
            response["uuid"] = str(uuid4())

        return response

    def set_error_response(self, data: dict):
        """ Take a error data, search a key inside Response schema and set
        response data

        -----------------
        Args:
            data (dict): Data Dictionary to set in response
        Returns:
            response (dict):  Response data serializered
        """
        key = data['key']
        response = self.catalog.get(key, False)
        if response:
            response["payload"] = data["payload"]
            response["uuid"] = str(uuid4())

        self.logger.error(response["detail"], extra=response)

        return web.json_response(
            response,
            status=HTTPStatus.UNPROCESSABLE_ENTITY.value)

    async def validate_schema(self, data, schema):
        """Schemas Request/Response validator

        -----------------
        Args:
            data (json): Json Request/Response object to check.
            schema (dict): Schema Object definition
        Returns:
            status (bool):  Schema Validation status
            error_list (list): Errors List if any
        """
        v = jsonschema.Draft7Validator(schema)
        errors = sorted(v.iter_errors(data), key=lambda e: e.path)
        error_list = []
        if errors:
            status = False
            for error in errors:
                error_list.append(error.message)
        else:
            status = True

        return status, error_list

    async def verify_signature(self, signature, api_secret, body_encoded):
        """Schemas Request/Response validator

        -----------------
        Args:
            signature (str): Headre content signature
            api_secret (str): Token session registered
            body_encoded (str): Body request econded
        Returns:
            status (bool):  Status signature
        """

        signature_hash = hmac.new(api_secret, body_encoded,
                                  hashlib.sha512).digest()
        base64_signature_hash = base64.b64encode(signature_hash).decode()

        if signature == base64_signature_hash:
            return True
        return False

    def verify_token_timeout(self, time_out: int, last_request: datetime):
        """ Check if token is valid, take a time_out and compare delta time of
        last requeste date and return status

        -----------------
        Args:
            time_out (int): Token time out in seconds
            last_request (datetime): Date of the last request from session
        Returns:
            status (bool):  Path Validation status
        """
        now = datetime.now(tz=timezone.utc)
        dt_object = datetime.fromtimestamp(last_request, tz=timezone.utc)
        delta = now - dt_object
        status = False
        if time_out > delta.total_seconds():
            status = True
        return status

    def set_logger_in_file(self, level=logging.DEBUG):
        """
        Set logger with a alternative handles (StackloggingHandler
        Class)

        -----------------
        Args:
            Its no necesary
        Return:
            logger: Logger instance loaded
        """
        logger_enable = self.config['logger']['enable']

        if logger_enable:
            logger_file_path = self.config['logger']['logs_file_path']
            logger_handler = StackFileHandler(logger_file_path)
            logger_handler.setLevel(level)
            self.logger.addHandler(logger_handler)

    def getLogger(self, name=None, level=logging.DEBUG, formatter=None):
        """
        Set logger with a alternative handles (StackloggingHandler Class)

        -----------------
        Args:
            Its no necesary
        Return:
            logger: Logger instance loaded
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        logger_handler = StackloggingHandler()
        logger_handler.setLevel(level)
        if formatter:
            logger_handler.setFormatter(formatter)

        logger.addHandler(logger_handler)

        self.logger = logger
        logger.info(f'Log Utility has been setting')
        return logger

    def get_extra_keys(self, record):
        """
        Take a logger record and clean it, only Extra parameters are returned

        -----------------
        Args:
            record (logger.record): Logger record to clean
        Return:
            extra_keys (list): Extra parameter list
        """
        extra_keys = []
        for key, value in record.__dict__.items():
            if key not in self.reserved and not key.startswith("_"):
                extra_keys.append(key)
        return extra_keys

    def format_stackdriver_json(self, record, message):
        """
        Take a string message and format the new logger record with the correct
        logger format to show

        -----------------
        Args:
            message (str): Logger message string
            record (logger.record): Logger record to clean
        Return:
            extra_keys (list): Extra parameter list
        """
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        dt = datetime.utcfromtimestamp(record.created).strftime(date_format)

        log_text = f'[{dt}] [{record.process}] [{record.levelname}] ' \
                   f'[{record.filename}:{record.lineno}] ' \
                   f'- Msg: {message} - Extra: '

        payload = {}
        extra_keys = self.get_extra_keys(record)

        for key in extra_keys:
            try:
                # serialization/type error check
                json.dumps(record.__dict__[key])
                payload[key] = record.__dict__[key]
            except TypeError:
                payload[key] = str(record.__dict__[key])

        dumps = json.dumps(payload)
        return log_text + dumps


class StackloggingHandler(logging.StreamHandler):
    """
    Handler class localed in logging.handler to support alternative formats and
    add extra data in the logger record

    """

    def __init__(self, stream=None):
        super(StackloggingHandler, self).__init__()

    def format(self, record):
        """
        Add logger format to record

        -----------------
        Args:
            record (logger.record): Logger record to formatter
        Return:
            record (logger.record): Logger record formatted

        """
        message = super(StackloggingHandler, self).format(record)
        return Vertebral().format_stackdriver_json(record, message)


class StackFileHandler(logging.FileHandler):
    """
    Handler class to support alternative formats and add extra data in
    the logger record

    """
    def format(self, record):
        """
        Add logger format to record

        -----------------
        Args:
            record (logger.record): Logger record to formatter
        Return:
            record (logger.record): Logger record formatted

        """
        message = super(StackFileHandler, self).format(record)
        return Vertebral().format_stackdriver_json(record, message)

