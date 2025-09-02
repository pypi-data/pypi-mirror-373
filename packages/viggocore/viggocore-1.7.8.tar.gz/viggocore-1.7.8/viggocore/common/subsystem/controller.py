from viggocore.common.subsystem.manager import Manager
import flask

from enum import Enum
from viggocore.common import exception, utils
# TODO(samueldmq): find a better name to this
# from viggocore.common.subsystem import manager as m


class ListOptions(Enum):
    ACTIVE_ONLY = {'id': 0, 'value': True}
    INACTIVE_ONLY = {'id': 1, 'value': False}
    ACTIVE_AND_INACTIVE = {'id': 2, 'value': None}

    @classmethod
    def new(cls, option):
        if option:
            return ListOptions[option]
        else:
            return ListOptions.ACTIVE_ONLY

    @classmethod
    def invalid_message_error(cls):
        return 'Invalid list_options.\nAvailables options are {}'.\
            format(', '.join(ListOptions. _member_names_))


class Controller(object):

    def __init__(self, manager: Manager,
                 resource_wrap: str,
                 collection_wrap: str) -> None:
        self.manager = manager
        self.resource_wrap = resource_wrap
        self.collection_wrap = collection_wrap

    def _filters_parse(self):
        filters = {
            k: flask.request.args.get(k) for k in flask.request.args.keys()}
        # TODO(samueldmq): fix this to work in a better way
        for k, v in filters.items():
            if v == 'true':
                filters[k] = True
            elif v == 'false':
                filters[k] = False
            elif v == 'null':
                filters[k] = None

        return filters

    def _filter_args(self, filters):
        filter_args = {k: v for k, v in filters.items() if '.' in k}

        return filter_args

    def _filters_cleanup(self, filters):
        _filters_cleanup = filters

        filter_args = self._filter_args(_filters_cleanup)
        # clean up original filters
        for k in filter_args.keys():
            # NOTE(samueldmq): I'm not sure I can pop
            # in the list comprehesion above...
            _filters_cleanup.pop(k)

        return _filters_cleanup

    def _parse_list_options(self, filters):
        _filters = filters.copy()
        options = _filters.pop('list_options', None)
        if 'active' in _filters.keys():
            return _filters
        try:
            options = ListOptions.new(options)
        except KeyError:
            raise exception.BadRequest(ListOptions.invalid_message_error())

        value = options.value['value']
        if value is not None:
            _filters['active'] = value

        return _filters

    def _get_include_dict(self, query_arg, filter_args):
        if type(query_arg) is str:
            includes_splited = query_arg.split(',')
            lists = [li.split('.') for li in includes_splited]
        else:
            lists = [li.split('.') for li in query_arg]
        include_dict = {}
        for list in lists:
            current = include_dict
            for i in range(len(list)):
                if list[i] in current:
                    current[list[i]].update({
                        list[i + 1]: {}} if i < (len(list) - 1) else {})
                else:
                    current[list[i]] = {
                        list[i + 1]: {}} if i < (len(list) - 1) else {}
                current = current[list[i]]

        for k, v in filter_args.items():
            list = k.split('.')
            current = include_dict
            for i in list[:-1]:  # last element is the attribute to filter on
                try:
                    current = current[i]
                except AttributeError:
                    # ignore current filter,
                    # entity to filter on is not included
                    continue
            current[list[-1]] = v

        return include_dict

    # def _get_include_dicts(self):
    #     filters = self._filters_parse()

    #     include_args = filters.pop('include', None)
    #     filter_args = self._filter_args(filters)

    #     include_dict = self._get_include_dict(
    #         include_args, filter_args) if include_args else {}

    #     return include_dict

    # TODO(JorgeSilva): melhorar essa função para diminuir a complexidade da
    # função
    def _get_include_dicts(self, includes_dict=None):  # noqa: C901
        if includes_dict is None:
            includes_dict = self._filters_parse()
            includes = includes_dict.pop('include', None)
        else:
            includes = includes_dict.get('include', None)
        retorno = {}
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
                            retorno[aux[0]][aux[1]][aux[2]].update({aux[3]: {}})
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
                else:
                    retorno.update({include: {}})
        return retorno

    def _entities_to_dict(self, entities, include_dicts=None):
        collection = []
        for entity in entities:
            if isinstance(entity, dict):
                collection.append(entity)
            else:
                try:
                    collection.append(
                        entity.to_dict(include_dict=include_dicts))
                except AssertionError:
                    # ignore current entity, filter mismatch
                    pass

        return collection

    def _clean_filters(self, **kwargs):
        excludes = ['include', 'page', 'page_size', 'order_by',
                    'require_pagination']
        filters_args = dict()
        for arg in kwargs:
            if arg not in excludes:
                filters_args.update({arg: kwargs.get(arg, None)})
        return filters_args

    def create(self):
        data = flask.request.get_json()

        try:
            if data:
                entity = self.manager.create(**data)
            else:
                entity = self.manager.create()
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {self.resource_wrap: entity.to_dict()}

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")

    def get(self, id):
        try:
            entity = self.manager.get(id=id)

            include_dicts = self._get_include_dicts()

            entity_dict = entity.to_dict(include_dict=include_dicts)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {self.resource_wrap: entity_dict}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def list(self):
        filters = self._filters_parse()
        filters = self._filters_cleanup(filters)

        try:
            filters = self._parse_list_options(filters)
            entities = self.manager.list(**filters)

            with_pagination = False
            require_pagination = filters.get('require_pagination', False)
            page = filters.get('page', None)
            page_size = filters.get('page_size', None)

            if (page and page_size is not None) and require_pagination is True:
                with_pagination = True
                count = self.manager.count(**(self._clean_filters(**filters)))
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        collection = self._entities_to_dict(
            entities, self._get_include_dicts(filters))

        response = {self.collection_wrap: collection}

        if with_pagination:
            response.update({'pagination': {'page': int(page),
                                            'page_size': int(page_size),
                                            'total': count}})

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def update(self, id):
        data = flask.request.get_json()

        try:
            # remove os campos de auditoria para serem
            # controladas internamente
            data.pop('created_at', None)
            data.pop('created_by', None)
            data.pop('updated_at', None)
            data.pop('updated_by', None)

            entity = self.manager.update(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = {self.resource_wrap: entity.to_dict()}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def delete(self, id):
        try:
            self.manager.delete(id=id)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=None,
                              status=204,
                              mimetype="application/json")

    def activate_or_deactivate_multiple_entities(self):
        data = flask.request.get_json()

        try:
            entities = self.manager.activate_or_deactivate_multiple_entities(
                **data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dicts = []
        for entity in entities:
            response_dict = {
                'id': entity.id,
                'active': entity.active
            }
            response_dicts.append(response_dict)
        response = {self.collection_wrap: response_dicts}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def export_xlsx(self):
        try:
            filters = flask.request.get_json()
            filters['filters'] = self._parse_list_options(filters['filters'])
            download_folder, file_name = self.manager.export_xlsx(**filters)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response = flask.send_from_directory(download_folder, file_name)
        utils.remove_file(f'{download_folder}/{file_name}')
        return response

    def export_pdf(self):
        try:
            filters = flask.request.get_json()
            filters['filters'] = self._parse_list_options(filters['filters'])
            response = self.manager.export_pdf(**filters)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=response,
                              status=200,
                              mimetype="application/pdf")

    def list_filtra_json(self):
        filters = flask.request.get_json()

        try:
            total = None
            filters = self._parse_list_options(filters)
            result = self.manager.list(**filters)
            if type(result) is tuple:
                entities = result[0]
                total = result[1]
            else:
                entities = result

            page = int(filters.get('page', -1))
            page_size = int(filters.get('page_size', -1))
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        collection = self._entities_to_dict(
            entities, self._get_include_dicts(filters))

        response = {self.collection_wrap: collection}

        if total is not None:
            response.update({'pagination': {'page': int(page),
                                            'page_size': int(page_size),
                                            'total': total}})

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
