import logging

from requests import Response, Session, PreparedRequest

from .errors.access_error import AccessError
from .errors.auth_error import AuthError
from .errors.bad_request_error import BadRequestError
from .errors.base_http_error import BaseApiError
from .errors.not_found_error import NotFoundError
from .errors.server_error import ServerError
from .errors.unprocessable_entity_error import UnprocessableEntityError


class BaseHTTP:
    def __init__(self, session: Session, base_url, allure=None):
        self.session = session
        self.base_url = base_url
        self.allure = allure
        self.log = logging.getLogger(__name__)

    def get(self, url, **kwargs):
        callback = self.session.get
        return self._send(url, callback, 'GET', **kwargs)

    def post(self, url, **kwargs):
        callback = self.session.post
        return self._send(url, callback, 'POST', **kwargs)

    def put(self, url, **kwargs):
        callback = self.session.put
        return self._send(url, callback, 'PUT', **kwargs)

    def patch(self, url, **kwargs):
        callback = self.session.patch
        return self._send(url, callback, 'PATCH', **kwargs)

    def delete(self, url, **kwargs):
        callback = self.session.delete
        return self._send(url, callback, 'DELETE', **kwargs)

    def _send(self, url, callback, method, **kwargs):
        skip_body = kwargs.pop('skip_body', False)  # Need to pop this parameter before callback
        self._log_request(url, method, **kwargs)
        response = callback(self._path(url), **kwargs)
        self._log_response(response, skip_body)
        try:
            curl = to_curl(response.request, skip_headers=True)
            self._attach_to_allure(curl, 'curl')
            self.log.info(f'curl: {curl}')  # noqa: E800
        except UnicodeDecodeError:  # curlify can fall when decoding request body
            self.log.info('Cannot curlify request :(')

        self._raise_for_status(response)
        try:
            return response.json()
        except ValueError:
            return response.text

    def _log_request(self, url, method, **kwargs):
        request_message = f'{method} {self._path(url)}'
        if method == 'GET' and 'params' in kwargs:
            request_message += f'?{kwargs["params"]}'
        headers = {**self.session.headers, **kwargs.get('headers')} if kwargs.get('headers') else self.session.headers
        request_message += f'\nHeaders: {headers}'
        request_message += f'\nCookies: {self.session.cookies.get_dict()}'
        if kwargs.get('json'):
            request_message += f'\nBody: {kwargs.get("json")}'
        if kwargs.get('data'):
            request_message += f'\nData: {kwargs.get("data")}'
        if kwargs.get('files'):
            if isinstance(kwargs.get('files'), dict):  # single file uploading
                request_message += f'\nFiles: {kwargs.get("files")["file"][0]}'
            elif isinstance(kwargs.get('files'), list):  # multiple files uploading
                request_message += f'\nFiles: {[f[1][0] for f in kwargs.get("files")]}'
        self._attach_to_allure(request_message.replace('\n', '\n\n'), 'Request')
        self.log.info(request_message)

    def _log_response(self, response: Response, skip_body: bool):
        response_message = f'Response status: {response.status_code}, elapsed: {response.elapsed.seconds}s'
        response_message += f'\nResponse headers: {response.headers}'
        response_body = ''
        if skip_body:
            response_body = 'Response body was skipped'
        elif response.text != '':
            response_body = f'Response body: {self._decode(response.text)}'
        if response_body:
            response_message += f'\n{response_body}'
        self._attach_to_allure(response_message, 'Response')
        self.log.info(response_message)

    def _path(self, url):
        return f'{self.base_url}{url}'

    def _attach_to_allure(self, text, label):
        if self.allure:
            self.allure.attach(text, label, self.allure.attachment_type.TEXT)

    def _decode(self, text):
        return (text.encode('utf-8')).decode('utf-8')

    def _raise_for_status(self, response):
        if 400 <= response.status_code < 500:
            if response.status_code == 400:
                raise BadRequestError(response)
            elif response.status_code == 401:
                raise AuthError(response)
            elif response.status_code == 403:
                raise AccessError(response)
            elif response.status_code in [404, 410]:
                raise NotFoundError(response)
            elif response.status_code == 422:
                raise UnprocessableEntityError(response)
            else:
                raise BaseApiError('Client', response)
        elif 500 <= response.status_code < 600:
            raise ServerError(response)


def to_curl(request: PreparedRequest, compressed: bool = False, verify: bool = True, skip_headers: bool = True) -> str:
    """ Inner implementation of curlify until new version with https://github.com/ofw/curlify/pull/27

    Parameters
    ----------
        :param request: PreparedRequest object from requests.Response
        :param compressed: If `True` then `--compressed` argument will be added to result
        :param verify: If `True` then `--insecure` argument will be added to result
        :param skip_headers: If 'True' then headers [Accept, Accept-Encoding, Connection, User-Agent] will be skipped
    """
    curl = f'curl -X {request.method}'

    sys_headers = ['accept', 'accept-encoding', 'connection', 'user-agent', 'content-length']
    for k, v in request.headers.items():
        if skip_headers and k.lower() in sys_headers:
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
