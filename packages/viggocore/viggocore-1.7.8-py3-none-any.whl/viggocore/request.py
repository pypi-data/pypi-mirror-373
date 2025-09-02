import flask
import uuid

from viggocore.common import exception
from viggocore.common.subsystem.apihandler import Api, ApiHandler


class Request(flask.Request):

    # TODO(samueldmq): find a better place to put this utility method
    def _check_uuid4(self, uuid_str):
        if len(uuid_str) != 32:
            return False
        try:
            return uuid.UUID(uuid_str, version=4)
        except ValueError:
            return False

    @property
    def url(self):
        path_info = flask.request.environ['PATH_INFO'].rstrip('/')
        path_bits = [
            '<id>' if self._check_uuid4(i) else i for i in path_info.split('/')
        ]

        if path_bits.count('<id>') > 1:
            pos = 0
            qty_id = 1
            for bit in path_bits:
                if bit == '<id>':
                    path_bits[pos] = '<id' + str(qty_id) + '>'
                    qty_id += 1
                pos += 1
        return '/'.join(path_bits)

    @property
    def token(self):
        return flask.request.headers.get('token')


class RequestManager(object):

    def __init__(self, api_handler: ApiHandler):
        self.api_handler = api_handler

    def before_request(self):
        api: Api = self.api_handler.api()
        if flask.request.method == 'OPTIONS':
            return

        # Short-circuit if accessing the root URL,
        # which will just return the version
        # TODO(samueldmq): Do we need to create a subsystem just for this ?
        if not flask.request.url:
            return

        routes = api.routes().list(url=flask.request.url,
                                   method=flask.request.method)
        if not routes:
            msg = 'Route not found'
            return flask.Response(response=msg, status=404)
        route = routes[0]

        if not route.active:
            msg = 'Route is inactive'
            return flask.Response(response=msg, status=410)

        if route.bypass:
            return

        token_id = flask.request.token

        if not token_id:
            msg = 'Token is required'
            return flask.Response(response=msg, status=401)

        try:
            token = api.tokens().get(id=token_id)
        except exception.NotFound:
            msg = 'Token not found'
            return flask.Response(response=msg, status=401)

        can_access = api.users().authorize(user_id=token.user_id, route=route)

        if not can_access:
            msg = 'You do not have permission'
            return flask.Response(response=msg, status=403)
        return
