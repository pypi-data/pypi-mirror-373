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

            response = {'capability_functionality': collection}

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
                for functionality in functionalities:
                    functionality_aux = functionality[0].to_dict(includes)
                    functionality_aux['policy_functionality_id'] = (
                        functionality[1])
                    collection.append(functionality_aux)

            response = {'capability_functionality': collection}

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

    def create_policy_functionalities(self):
        data = flask.request.get_json()
        policy_functionalities = data.get(
            'policy_functionalities', [])
        successes = []
        errors = []

        for pf in policy_functionalities:
            try:
                pf_entity = self.manager.create(**pf)
                successes.append(pf_entity.to_dict())
            except Exception as exc:
                pf['msg_error'] = exc.message
                errors.append(pf)

        response = {'successes': successes, 'errors': errors}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
