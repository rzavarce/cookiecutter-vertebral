from aiohttp import web


async def StatusHandler(request: web.Request) -> web.Response:
    """
    This hanler allow to test if the service is up.
    ---
    summary: Monitor System Handler
    tags:
      - Status Systems
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

    data = await request.json()

    print()
    print(data)
    print()

    response = {
        "key": "json_test",
        "payload": {
            "test": "All Systems are ready...",
        }
    }

    return web.json_response(response)


async def test_handler(request: web.Request) -> web.Response:
    """
    This hanler allow to test if the service is up.
    ---
    summary: Monitor System Handler
    tags:
      - Status Systems
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              payload:
                type: object
                additionalProperties: false
                required:
                  - test
                properties:
                  test:
                    type: string
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
      '400':
        description: Unknown exception xxxxxxxxxxxxxxx
    """

    response = {
        "key": "json_test",
        "payload": {
            "test": "esta es una prueba, y ha salido bien",
        }
    }

    return web.json_response(response)


