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

    def get_available_functionalities(self):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            functionalities, total_rows = self.manager\
                .get_available_functionalities(**filters)

            collection = self._entities_to_dict(
                functionalities, self._get_include_dicts(filters))

            response = {'functionalities': collection}

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

    def get_selected_functionalities(self):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            functionalities, total_rows = self.manager\
                .get_selected_functionalities(**filters)

            includes = self._get_include_dicts(filters)
            collection = []
            if len(functionalities) > 0:
                for funcionality in functionalities:
                    funcionality_aux = funcionality[0].to_dict(includes)
                    funcionality_aux['capability_functionality_id'] = (
                        funcionality[1])
                    collection.append(funcionality_aux)

            response = {'functionalities': collection}

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

    def create_capability_functionalities(self):
        data = flask.request.get_json()
        capability_functionalities = data.get(
            'capability_functionalities', [])
        successes = []
        errors = []

        for cf in capability_functionalities:
            try:
                cf_entity = self.manager.create(**cf)
                successes.append(cf_entity.to_dict())
            except Exception as exc:
                cf['msg_error'] = exc.message
                errors.append(cf)

        response = {'successes': successes, 'errors': errors}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
