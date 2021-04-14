import json
import typing
from aiohttp import web

from aiohttp_swagger3 import RequestValidationFailed

from .schemas import RequestSchema, ResponseSchema


@web.middleware  # noqa: Z110
async def vertebral_middelware(
    request: web.Request,
    handler: typing.Callable[[web.Request], typing.Awaitable[web.Response]],
) -> web.Response:
    """
    Deserialize request's json body and schema validatetion, Serialize response
    with schema validation, Check Authentification Criteries, Set logger config,
    and others

    -----------------
    Args:
        request (objct): App request object
        handler (str): Handler function set in route
    Returns:
        token (str): Token generated
    """

    vertebra = request.app["vertebra"]

    if not request.can_read_body:
        return await handler(request)

    if vertebra.is_exclude(request):

        body = await request.json()
        request_status, error_list = \
            await vertebra.validate_schema(body, RequestSchema)

        if request_status:

            try:
                resp = await handler(request)
                json_response = vertebra.set_response(json.loads(resp.text))
                response_status, error_list = \
                    await vertebra.validate_schema(json_response,
                                                   ResponseSchema)

                if response_status:
                    return web.json_response(json_response)
                else:
                    payload = {
                        "error_msgs": error_list
                    }
                    return vertebra.set_error_response(payload)

            except RequestValidationFailed as exc:
                payload = {
                    "key": "openapi3_error",
                    "payload": {
                        "error_msgs": exc.errors['body']
                    }
                }
                return vertebra.set_error_response(payload)

        else:
            payload = {
                "key": "json_format_error",
                "payload": {
                    "error_msgs": error_list
                }
            }
            return vertebra.set_error_response(payload)

    enabled_auth = request.app['config']['auth']['enabled']
    if not enabled_auth:
        body = await request.json()
        request_status, error_list = \
            await vertebra.validate_schema(body, RequestSchema)

        if request_status:
            try:
                resp = await handler(request)
                json_response = vertebra.set_response(json.loads(resp.text))
                response_status, error_list = \
                    await vertebra.validate_schema(json_response,
                                                   ResponseSchema)
                if response_status:
                    return web.json_response(json_response)
                else:
                    payload = {
                        "error_msgs": error_list
                    }
                    return vertebra.set_error_response(payload)

            except RequestValidationFailed as exc:
                payload = {
                    "key": "openapi3_error",
                    "payload": {
                        "error_msgs": exc.errors['body']['payload']
                    }
                }
                return vertebra.set_error_response(payload)
        else:
            payload = {
                "key": "json_format_error",
                "payload": {
                    "error_msgs": error_list
                }
            }
            return vertebra.set_error_response(payload)

    if 'session' in request.app:

        signature = request.headers.get('Content-Signature', "not_found")

        if signature == "not_found":
            payload = {
                "key": "signature_header_not_found",
                "payload": {
                    "error_msgs": "Content-Signature header not found "
                                  "or invalid"
                }
            }
            return vertebra.set_error_response(payload)

        token = request.app['session']['token'].encode()
        body = await request.text()
        body_encoded = body.encode()
        signature_status = await vertebra.verify_signature(signature, token,
                                                           body_encoded)

        if signature_status:
            time_out = request.app['config']['auth']['token_time']
            last_request = request.app['session']['last_request']

            if vertebra.verify_token_timeout(time_out, last_request):

                body = await request.json()
                request_status, error_list = \
                    await vertebra.validate_schema(body, RequestSchema)

                if request_status:

                    try:
                        resp = await handler(request)
                        json_response = vertebra.set_response(
                            json.loads(resp.text))
                        response_status, error_list = \
                            await vertebra.validate_schema(json_response,
                                                           ResponseSchema)

                        if response_status:
                            return web.json_response(json_response)
                        else:
                            payload = {
                                "error_msgs": error_list
                            }
                            return vertebra.set_error_response(payload)

                    except RequestValidationFailed as exc:
                        payload = {
                            "key": "openapi3_error",
                            "payload": {
                                "error_msgs": exc.errors['body']
                            }
                        }
                        return vertebra.set_error_response(payload)

                else:
                    payload = {
                        "key": "json_format_error",
                        "payload": {
                            "error_msgs": error_list
                        }
                    }
                    return vertebra.set_error_response(payload)

            else:
                payload = {
                    "key": "token_error",
                    "payload": {
                        "error_msgs": "Token has expired or not valid"
                    }
                }
                return vertebra.set_error_response(payload)
        else:
            payload = {
                "key": "signature_error",
                "payload": {
                    "error_msgs": "Signature error, signon again pleases"
                }
            }
            return vertebra.set_error_response(payload)
    else:
        payload = {
            "key": "session_error",
            "payload": {
                "error_msgs": "Session error, signon again pleases"
            }
        }
        return vertebra.set_error_response(payload)
