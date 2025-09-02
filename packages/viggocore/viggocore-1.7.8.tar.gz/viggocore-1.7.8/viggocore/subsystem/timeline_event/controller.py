import flask

from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class Controller(controller.Controller):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def _get_user_from_token(self):
        if flask.has_request_context():
            token_id = flask.request.headers.get('token')
            if token_id is not None:
                self.token = self.manager.api.tokens().get(id=token_id)
                return self.token.user_id
        return None

    # TODO descobrir alguma forma de reaproveitar o list do viggocore
    def list(self):
        filters = self._filters_parse()
        filters = self._filters_cleanup(filters)

        try:
            user_id = self._get_user_from_token()
            filters = self._parse_list_options(filters)

            if user_id is not None:
                filters['user_id'] = user_id
            else:
                return flask.Response("user_id not found",
                                      status=403)

            timeline_events = self.manager.list(**filters)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        timeline_events_dict = self._entities_to_dict(
                timeline_events, self._get_include_dicts())
        response = {self.collection_wrap: timeline_events_dict}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
