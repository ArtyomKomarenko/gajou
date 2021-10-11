from requests import PreparedRequest


def to_curl(request: PreparedRequest, compressed: bool = False, verify: bool = True, skip_headers: bool = True) -> str:
    """Return string with curl command by provided request object. Based on https://github.com/ofw/curlify.

    Parameters
    ----------
        :param request: PreparedRequest object from requests.Response
        :param compressed: If `True` then `--compressed` argument will be added to result
        :param verify: If `True` then `--insecure` argument will be added to result
        :param skip_headers: If 'True' then headers [Accept, Accept-Encoding, Connection, User-Agent] will be skipped
    """
    curl = f'curl -X {request.method}'

    sys_headers = ['Accept', 'Accept-Encoding', 'Connection', 'User-Agent', 'Content-Length']
    for k, v in request.headers.items():
        if skip_headers and k in sys_headers:
            continue
        curl += f" -H '{k}: {v}'"

    if request.body:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        curl += f" -d '{body}'"

    curl += f' {request.url}'

    if compressed:
        curl += ' --compressed'
    if not verify:
        curl += ' --insecure'

    return curl
