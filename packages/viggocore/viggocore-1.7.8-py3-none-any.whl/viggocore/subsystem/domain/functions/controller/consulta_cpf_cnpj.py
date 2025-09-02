import flask
from viggocore.common import exception, utils


def consulta_cpf_cnpj(self):
    filters = self._filters_parse()

    try:
        response = self.manager.consulta_cpf_cnpj(**filters)
    except exception.ViggoCoreException as exc:
        return flask.Response(response=exc.message, status=exc.status)

    return flask.Response(
        response=utils.to_json(response),
        status=200,
        content_type='application/json',
    )
