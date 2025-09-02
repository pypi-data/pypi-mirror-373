import flask

from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class Controller(controller.Controller):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def get_token_id(self):
        return flask.request.headers.get('token')

    def get_token(self, token_id):
        return self.manager.api.tokens().get(id=token_id)

    def add_routes(self, id):
        try:
            data = flask.request.get_json()

            functionality = self.manager.add_routes(id=id, **data)

            response = {'functionality': functionality.to_dict({'routes': {}})}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")

    def rm_routes(self, id):
        try:
            data = flask.request.get_json()

            functionality = self.manager.rm_routes(id=id, **data)

            response = {'functionality': functionality.to_dict({'routes': {}})}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")

    def get_available_routes(self, id):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            routes, total_rows = self.manager.get_available_routes(
                id=id, **filters)

            collection = self._entities_to_dict(
                routes, self._get_include_dicts(filters))

            response = {
                'functionality': {
                    'id': id,
                    'routes': collection
                }
            }

            page = filters.get('page', None)
            page_size = filters.get('page_size', None)

            if total_rows is not None:
                response.update(
                    {'pagination': {'page': int(page),
                                    'page_size': int(page_size),
                                    'total': total_rows}})
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def get_selected_routes(self, id):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            routes, total_rows = self.manager.get_selected_routes(
                id=id, **filters)

            collection = self._entities_to_dict(
                routes, self._get_include_dicts(filters))

            response = {
                'functionality': {
                    'id': id,
                    'routes': collection
                }
            }

            page = filters.get('page', None)
            page_size = filters.get('page_size', None)

            if total_rows is not None:
                response.update(
                    {'pagination': {'page': int(page),
                                    'page_size': int(page_size),
                                    'total': total_rows}})
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
