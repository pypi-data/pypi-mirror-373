import flask
from viggocore.common import controller, utils, exception


class Controller(controller.CommonController):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    # return start and end
    def _get_page_and_page_size(self, page, page_size):
        if page < 0:
            raise exception.BadRequest(
                'the page parameter must be greater than -1')
        if page_size < 1:
            raise exception.BadRequest(
                'the page_size parameter must be greater than 0')

        if page == 0:
            return (page, page_size)
        else:
            start = page * page_size
            end = start + page_size
            return (start, end)

    def get_table_names(self):
        try:
            msg = (
                'É necessário sobrescrever a variável lista_table_names' +
                'no projeto específico para garantir que as ' +
                'tabelas listadas são apenas as importantes.')
            # se não preencher a lista no projeto específico lançara a exceção
            if len(self.lista_table_names) == 0:
                return flask.Response(response=msg, status=400)
        except Exception:
            return flask.Response(response=msg,
                                  status=400)

        filters = self._filters_parse()
        filters = self._filters_cleanup(filters)
        filters = self._parse_list_options(filters)

        lista_response = self.lista_table_names
        total = len(self.lista_table_names)

        name = filters.pop('name', None)
        if name is not None:
            if '%' in name:
                name = name.replace('%', '')
                lista_response = list(
                    filter(lambda x: name in x,
                           self.lista_table_names))
            else:
                lista_response = list(
                    filter(lambda x: name == x,
                           self.lista_table_names))

        require_pagination = filters.pop('require_pagination', False)
        page = filters.pop('page', None)
        page_size = filters.pop('page_size', None)
        total = len(lista_response)

        if require_pagination and None not in [page, page_size]:
            page = int(page)
            page_size = int(page_size)

            start, end = self._get_page_and_page_size(page, page_size)

            response = {'table_names': lista_response[start:end]}

            response.update({'pagination': {'page': page,
                                            'page_size': page_size,
                                            'total': total}})
        else:
            response = {'table_names': lista_response[start:end]}
        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")
