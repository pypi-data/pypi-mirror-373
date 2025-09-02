import flask
from viggocore.common import exception


def import_capabilities_and_policies(self, id):
    try:
        # recupera o arquivo à partir da requisição flask
        file = flask.request.files.get('file', None)

        # valida se arquivo foi enviado e envia BadRequest
        if not file:
            raise exception.BadRequest(
                'ERRO! Arquivo não enviado na requisição')

        # adiciona arquivo ao dicionário
        data = {'file': file}

        self.manager.import_capabilities_and_policies(id=id, **data)
    except exception.ViggoCoreException as exc:
        # retorna uma exceção no caso de falha
        return flask.Response(response=exc.message,
                              status=exc.status)

    # retorna um status 204 no sucesso
    return flask.Response(status=204,
                          mimetype=self.MIMETYPE_JSON)
