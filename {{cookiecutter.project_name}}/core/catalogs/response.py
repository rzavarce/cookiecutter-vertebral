RESPONSES = {
    'auth_response': {
        'status': 200,
        'type': 'success',
        'code': 'R-0000',
        'detail': 'Authentification is success'
    },
    'json_test': {
        'status': 200,
        'type': 'success',
        'code': 'R-0001',
        'detail': 'Json test is correct'
    },

}

ERRORS = {
    'authentification_error': {
        'status': 401,
        'type': 'error',
        'code': 'E-0000',
        'detail': 'Key and Resource are not valid',
    },
    'json_format_error': {
        'status': 400,
        'type': 'error',
        'code': 'E-0001',
        'detail': 'Json request is not valid',
    },
    'openapi3_error': {
        'status': 400,
        'type': 'error',
        'code': 'E-0002',
        'detail': 'Json payload is not valid',
    },
    'session_error': {
        'status': 403,
        'type': 'error',
        'code': 'E-0003',
        'detail': 'Session is not valid',
    },
    'signature_error': {
        'status': 401,
        'type': 'error',
        'code': 'E-0004',
        'detail': 'Signature is not valid',
    },
    'signature_header_not_found': {
        'status': 401,
        'type': 'error',
        'code': 'E-0005',
        'detail': 'Content-Signature header error',
    },
}

CATALOG = {
    **RESPONSES,
    **ERRORS
}
