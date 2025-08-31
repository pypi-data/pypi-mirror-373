from http import HTTPStatus

import jwt
from aioresponses import aioresponses
from yarl import URL


class SpypointServerForTest:
    base_url = 'https://restapi.spypoint.com/api/v3'

    def __init__(self):
        self.server = aioresponses()

    def __enter__(self):
        self.server.__enter__()
        return self

    def __exit__(self, *args):
        self.server.__exit__(*args)

    def prepare_login_response(self, body=None, status=HTTPStatus.OK, repeat=True) -> str:
        if body is None:
            body = {'token': jwt.encode({'exp': 1627417600}, 'secret')}
        self.server.post(f'{self.base_url}/user/login', status=status, payload=body, repeat=repeat)
        return body.get('token')

    def prepare_cameras_response(self, body=None, status=HTTPStatus.OK, repeat=True):
        if body is None:
            body = []
        self.server.get(f'{self.base_url}/camera/all', status=status, payload=body, repeat=repeat)

    def prepare_shared_cameras_response(self, body=None, status=HTTPStatus.OK, repeat=True):
        if body is None:
            body = []
        self.server.get(f'{self.base_url}/shared-cameras/all', status=status, payload=body, repeat=repeat)

    def prepare_shared_camera_response(self, id, body=None, status=HTTPStatus.OK, repeat=True):
        if body is None:
            body = []
        self.server.get(f'{self.base_url}/shared-cameras/{id}', status=status, payload=body, repeat=repeat)

    def assert_called_with(self, url, method, *args, **kwargs):
        self.server.assert_called_with(f'{self.base_url}{url}', method, *args, **kwargs)

    def assert_called_n_times_with(self, times, url, method, headers, json):
        key = (method, URL(f'{self.base_url}{url}'))
        assert len(self.server.requests[key]) == times
        self.assert_called_with(url, method, headers=headers, json=json)
