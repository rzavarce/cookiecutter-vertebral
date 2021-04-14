"""Schemas Core Vertebral"""

RequestSchema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "title": "RequestSchema",
    "properties": {
        "key": {"type": "string"},
        "resource": {"type": "string"},
        "nonce": {"type": "string"},
        "mode": {"type": "string"},
        "payload": {
            "type": "object",
            "properties": {

            }
        },

    },
    "required": ["key", "resource", "nonce", "mode", "payload"],
    "additionalProperties": False
}

ResponseSchema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "title": "ResponseSchema",
    "properties": {
        "code": {"type": "string"},
        "type": {"type": "string"},
        "status": {"type": "integer"},
        "detail": {"type": "string"},
        "payload": {
            "type": "object",
            "properties": {

            }
        },
        "uuid": {"type": "string"},

    },
    "required": ["code", "status", "detail", "payload", "uuid"],
    "additionalProperties": False
}
