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

    def get_available_modules(self):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            modules, total_rows = self.manager\
                .get_available_modules(**filters)

            collection = self._entities_to_dict(
                modules, self._get_include_dicts(filters))

            response = {'capability_modules': collection}

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

    def get_selected_modules(self):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            modules, total_rows = self.manager\
                .get_selected_modules(**filters)

            includes = self._get_include_dicts(filters)
            collection = []
            if len(modules) > 0:
                for module in modules:
                    module_aux = module[0].to_dict(includes)
                    module_aux['policy_module_id'] = (
                        module[1])
                    collection.append(module_aux)

            response = {'capability_modules': collection}

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

    def create_policy_modules(self):
        data = flask.request.get_json()
        policy_modules = data.get(
            'policy_modules', [])
        successes = []
        errors = []

        for pm in policy_modules:
            try:
                pm_entity = self.manager.create(**pm)
                successes.append(pm_entity.to_dict())
            except Exception as exc:
                pm['msg_error'] = exc.message
                errors.append(pm)

        response = {'successes': successes, 'errors': errors}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
