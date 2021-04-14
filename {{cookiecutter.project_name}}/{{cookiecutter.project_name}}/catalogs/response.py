#!/usr/bin/env python
# -*- coding: utf-8 -*-

RESPONSES = {
    'hello_world': {
        'status': 400,
        'type': 'error',
        'code': '-1',
        'detail': 'json_format_error',
        'description': 'JSON\'s request format is not valid'
    },
    'json_format_error': {
        'status': 400,
        'type': 'error',
        'code': '-1',
        'detail': 'json_format_error',
        'description': 'JSON\'s request format is not valid'
    },
}
