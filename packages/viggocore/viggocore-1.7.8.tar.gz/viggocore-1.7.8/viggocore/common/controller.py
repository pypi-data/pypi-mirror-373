import flask

from viggocore.common import exception, utils
from viggocore.common.subsystem import controller


class CommonController(controller.Controller):

    # TODO(JorgeSilva): melhorar essa função para diminuir a complexidade da
    # função
    def _get_include_dicts_vex(self, kwargs):  # noqa: C901
        retorno = {}
        includes = kwargs.get('include', None)
        if includes is not None:
            if type(includes) is list:
                includes_splited = includes
            else:
                includes_splited = includes.split(',')
            for include in includes_splited:
                if '.' in include:
                    # Variável aux serve para dar um include em um include.
                    # Exemplo: em uma consulta de pedido eu dou um include em
                    # cliente e quero os campos de parceiro também então o
                    # include de cliente fica: cliente.parceiro assim ele vai
                    # incluir o parceiro em cliente e o cliente em pedido
                    aux = include.split('.')
                    if len(aux) == 2:
                        if aux[0] not in retorno:
                            retorno.update({aux[0]: {aux[1]: {}}})
                        else:
                            retorno[aux[0]].update({aux[1]: {}})
                    elif len(aux) == 3:
                        if aux[0] not in retorno:
                            retorno.update({aux[0]: {aux[1]: {aux[2]: {}}}})
                        elif aux[1] not in retorno[aux[0]]:
                            retorno[aux[0]].update({aux[1]: {aux[2]: {}}})
                        else:
                            retorno[aux[0]][aux[1]].update({aux[2]: {}})
                    elif len(aux) == 4:
                        if aux[0] not in retorno:
                            retorno.update({aux[0]: {aux[1]: {aux[2]: {aux[3]: {}}}}})  # noqa: E501
                        elif aux[1] not in retorno[aux[0]]:
                            retorno[aux[0]].update({aux[1]: {aux[2]: {aux[3]: {}}}})  # noqa: E501
                        elif aux[2] not in retorno[aux[0]][aux[1]]:
                            retorno[aux[0]][aux[1]].update({aux[2]: {aux[3]: {}}})  # noqa: E501
                        else:
                            retorno[aux[0]][aux[1]][aux[2]].update(
                                {aux[3]: {}})
                    elif len(aux) == 5:
                        if aux[0] not in retorno:
                            retorno.update({aux[0]: {aux[1]: {aux[2]: {aux[3]: {aux[4]: {}}}}}})  # noqa: E501
                        elif aux[1] not in retorno[aux[0]]:
                            retorno[aux[0]].update({aux[1]: {aux[2]: {aux[3]: {aux[4]: {}}}}})  # noqa: E501
                        elif aux[2] not in retorno[aux[0]][aux[1]]:
                            retorno[aux[0]][aux[1]].update({aux[2]: {aux[3]: {aux[4]: {}}}})  # noqa: E501
                        elif aux[3] not in retorno[aux[0]][aux[1]][aux[2]]:
                            retorno[aux[0]][aux[1]][aux[2]].update({aux[3]: {aux[4]: {}}})  # noqa: E501
                        else:
                            retorno[aux[0]][aux[1]][aux[2]][aux[3]].update({aux[4]: {}})  # noqa: E501
                    elif len(aux) == 6:
                        if aux[0] not in retorno:
                            retorno.update({aux[0]: {aux[1]: {aux[2]: {aux[3]: {aux[4]: {}}}}}})  # noqa: E501
                        elif aux[1] not in retorno[aux[0]]:
                            retorno[aux[0]].update({aux[1]: {aux[2]: {aux[3]: {aux[4]: {}}}}})  # noqa: E501
                        elif aux[2] not in retorno[aux[0]][aux[1]]:
                            retorno[aux[0]][aux[1]].update({aux[2]: {aux[3]: {aux[4]: {}}}})  # noqa: E501
                        elif aux[3] not in retorno[aux[0]][aux[1]][aux[2]]:
                            retorno[aux[0]][aux[1]][aux[2]].update({aux[3]: {aux[4]: {}}})  # noqa: E501
                        elif aux[4] not in retorno[aux[0]][aux[1]][aux[2]][aux[3]]:  # noqa: E501
                            retorno[aux[0]][aux[1]][aux[2]][aux[3]].update({aux[4]: {aux[5]: {}}})  # noqa: E501
                        else:
                            retorno[aux[0]][aux[1]][aux[2]][aux[3]].update({aux[4]: {}})  # noqa: E501
                else:
                    retorno.update({include: {}})
        return retorno

    def list(self):
        filters = self._filters_parse()

        try:
            filters = self._parse_list_options(filters)
            (entities, total_rows) = self.manager.list(**filters)

            page = filters.get('page', None)
            page_size = filters.get('page_size', None)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        collection = self._entities_to_dict(
            entities, self._get_include_dicts_vex(filters))

        response = {self.collection_wrap: collection}

        if total_rows is not None:
            response.update({'pagination': {'page': int(page),
                                            'page_size': int(page_size),
                                            'total': total_rows}})

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def get(self, id):
        filters = self._filters_parse()

        try:
            entity = self.manager.get(id=id)

            include_dicts = self._get_include_dicts_vex(filters)

            entity_dict = entity.to_dict(include_dict=include_dicts)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {self.resource_wrap: entity_dict}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
