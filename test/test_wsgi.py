# динамический wsgi для теста


from urllib.parse import parse_qs


def parse_get_params(environ):
    query_string = environ.get('QUERY_STRING', '')
    return parse_qs(query_string)


def parse_post_params(environ):
    if environ['REQUEST_METHOD'].upper() != 'POST':
        return {}

    content_length = int(environ.get('CONTENT_LENGTH', 0))
    request_body = environ['wsgi.input'].read(content_length)
    return parse_qs(request_body.decode('utf-8'))


def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    get_params = parse_get_params(environ)
    post_params = parse_post_params(environ)

    response_body = f"GET parameters: {get_params}\nPOST parameters: {post_params}"
    return [response_body.encode('utf-8')]