import flask

from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class Controller(controller.Controller):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def get_nextval(self, id):
        data = flask.request.get_json()

        try:
            if 'name' not in data or 'table_id' not in data:
                raise exception.BadRequest(
                    'ERROR! "name" or "table_id" not defined')

            response = self.manager.get_nextval(
                id=id,
                table_id=data['table_id'],
                name=data['name'])
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {'nextval': response}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
