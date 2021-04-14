import time
from aiohttp import web
from aiohttp_session import new_session

from .models.auth import Auth

# TODO move to app/handlers, is better ...
async def SignOnHandler(request: web.Request) -> web.Response:
    """
    This handler allow loggin/signon and return a valid token.
    ---
    summary: Sign On Authentification Handler
    tags:
      - Authentification Systems
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - payload
            properties:
              payload:
                type: object
    responses:
      '200':
        description: Return a json response with the System Status
        content:
          application/json:
            schema:
              type: object
              required:
                - systems
              properties:
                systems:
                  type: object
                  required:
                    - token
                  properties:
                    token:
                      type: string
      '500':
        description: Unknown exception
    """

    data = await request.json()
    auth = Auth(request.app['mongo'])
    token_length = request.app['config']['auth']['token_length']

    check = await auth.check_credentials(key=data['key'],
                                         resource=data['resource'],
                                         token_length=token_length)
    if check is None:
        response = {
            "key": "authentification_error",
            "payload": {
                "error_msgs": "Token could not be generated"
            }
        }
    else:
        session = await new_session(request)
        session['token'] = check
        session['last_request'] = time.time()
        request.app['session'] = session
        response = {
            "key": "auth_response",
            "payload": {
                "token": check,
            }
        }

    return web.json_response(response)
