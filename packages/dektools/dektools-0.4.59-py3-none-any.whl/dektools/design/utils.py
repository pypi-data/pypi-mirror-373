def split_function(body, a='$', p='$$'):
    if body is None:
        body = {}
    body = body.copy()
    args = body.pop(a, None) or []
    params = body.pop(p, None) or {}
    return args, params, body
