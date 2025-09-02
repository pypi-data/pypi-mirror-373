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

    def add_functionalities(self, id):
        try:
            data = flask.request.get_json()

            module = self.manager.add_functionalities(id=id, **data)

            response = {'module': module.to_dict({'functionalities': {}})}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")

    def rm_functionalities(self, id):
        try:
            data = flask.request.get_json()

            module = self.manager.rm_functionalities(id=id, **data)

            response = {'module': module.to_dict({'functionalities': {}})}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")

    def get_available_functionalities(self, id):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            functionalities, total_rows = self.manager\
                .get_available_functionalities(id=id, **filters)

            collection = self._entities_to_dict(
                functionalities, self._get_include_dicts(filters))

            response = {
                'module': {
                    'id': id,
                    'functionalities': collection
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

    def get_selected_functionalities(self, id):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            functionalities, total_rows = self.manager\
                .get_selected_functionalities(id=id, **filters)

            collection = self._entities_to_dict(
                functionalities, self._get_include_dicts(filters))

            response = {
                'module': {
                    'id': id,
                    'functionalities': collection
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
