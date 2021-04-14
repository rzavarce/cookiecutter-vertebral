
from aiohttp import web


async def MonitorHandler(request: web.Request) -> web.Response:
    """
    This hanler allow to test if the service is up.
    ---
    summary: Monitor System Handler
    tags:
      - Monitor Systems
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
                    - state
                    - message
                  properties:
                    state:
                      type: boolean
                    message:
                      type: string
      '500':
        description: Unknown exception
    """

    payload = request['data']['body']['payload']

    print()
    # print(request["user_data"])
    # print(request["identity"])
    print("pasoooo")
    print()

    response = {"systems": {"state": True,
                            "message": "All Systems are ready...",
                            "payload": payload
                            }
                }
    return web.json_response(response)
