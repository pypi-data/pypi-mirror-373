from viggocore.common.subsystem import manager, entity
from sqlalchemy import func, and_, or_
from datetime import datetime as datetime1
import datetime as datetime2


class CommonManager(manager.Manager):

    def __init__(self, driver, gerar_log=None):
        super(CommonManager, self).__init__(driver, gerar_log)

    def apply_filters_includes(self, query, dict_compare, **kwargs):
        for k, v in kwargs.items():
            if '.' in k:
                # attribute é o campo da classe do include que deve ser filtrado
                attribute = k.split('.')[-1]
                # individual é a chave que irá identificar qual resource usar
                individual = k.split('.')[0]
                # pega o resource pelo campo "individual" concatenado
                # com o ponto final, pois todos os dict_compare até
                # o momento estão com o ponto final
                resource = dict_compare.get(individual + '.', None)
                # se não encontrar o resource com o ponto ai vai buscar sem,
                # para que os próximos dict_compare possam ser implementados
                # sem o ponto final
                if resource is None:
                    resource = dict_compare.get(individual, None)

                # se resource não for encontrado retorna a query sem filtrar
                if resource is not None and hasattr(resource, attribute):
                    # verifica se não foi passada uma lista de valores
                    if not isinstance(v, list):
                        query = self.apply_filter_individual(
                            query, resource, attribute, v)
                    else:
                        query = self.apply_filter_list(
                            query, resource, attribute, v)

        return query

    def apply_filter_individual(self, query, resource, k, v):
        # verifica se o valor é do tipo string
        isinstance_aux = isinstance(v, str)
        # pega o atributo da classe para verificar se o campo da
        # classe é do tipo string
        attr = getattr(resource, k)

        if self.driver._is_id(k):
            query = query.filter(getattr(resource, k) == v)
        elif k == 'tag':
            # TODO(JorgeSilva): definir o caractere para split
            values = v
            if len(v) > 0 and v[0] == '#':
                values = v[1:]
            values = values.split(',')
            filter_tags = []
            for value in values:
                filter_tags.append(
                    getattr(resource, k)
                    .like('%#' + str(value) + ' %'))
            query = query.filter(or_(*filter_tags))
        # tipo data
        elif isinstance_aux and self.__isdate(v):
            day, next_day = self.__get_day_and_next_day(v)
            query = query.filter(
                and_(
                    or_(getattr(resource, k) < next_day,
                        getattr(resource, k).is_(None)),
                    or_(getattr(resource, k) >= day,
                        getattr(resource, k).is_(None))))
        # tipo string foi passado '%' no valor
        elif isinstance_aux and '%' in v:
            normalize = func.viggocore_normalize
            query = query.filter(
                normalize(getattr(resource, k)).ilike('%' + normalize(v)))
        # tipo string não foi passado '%' no valor
        elif isinstance_aux and attr.type.python_type is str:
            normalize = func.viggocore_normalize
            query = query.filter(
                normalize(getattr(resource, k)) == normalize(v))
        # se for qualquer outro filtro usa esse daqui
        else:
            query = query.filter(getattr(resource, k) == v)

        return query

    def apply_filter_list(self, query, resource, k, v):
        # verifica se o valor é do tipo string
        isinstance_aux = isinstance(v[0], str)
        # pega o atributo da classe para verificar se o campo da
        # classe é do tipo string
        attr = getattr(resource, k)

        # tipo string foi passado '%' no valor
        if self.driver._is_id(k):
            query = query.filter(getattr(resource, k).in_(v))
        elif isinstance_aux and '%' in v[0]:
            normalize = func.viggocore_normalize
            # monta uma lista com os filtros para aplicar o "or"
            filtro = [
                normalize(getattr(resource, k)).ilike('%' + normalize(v_aux))
                for v_aux in v]
            query = query.filter(or_(*filtro))
        # tipo string não foi passado '%' no valor
        elif isinstance_aux and attr.type.python_type is str:
            normalize = func.viggocore_normalize
            # monta uma lista com os filtros para aplicar o "or"
            filtro = [
                normalize(getattr(resource, k)) == normalize(v_aux)
                for v_aux in v]
            query = query.filter(or_(*filtro))
        # se for qualquer outro filtro usa esse daqui
        else:
            query = query.filter(getattr(resource, k).in_(v))

        return query

    def apply_filters(self, query, resource, **kwargs):
        for k, v in kwargs.items():
            if '.' not in k and hasattr(resource, k):
                # verifica se não foi passada uma lista de valores
                if not isinstance(v, list):
                    query = self.apply_filter_individual(
                        query, resource, k, v)
                else:
                    query = self.apply_filter_list(
                        query, resource, k, v)

        return query

    def with_pagination(self, **kwargs):
        require_pagination = kwargs.get('require_pagination', False)
        page = kwargs.get('page', None)
        page_size = kwargs.get('page_size', None)

        if None not in [page, page_size] and require_pagination is True:
            return True
        return False

    def __isdate(self, data, format="%Y-%m-%d"):
        res = True
        try:
            res = bool(datetime1.strptime(data, format))
        except ValueError:
            res = False
        return res

    def __get_day_and_next_day(self, data, format="%Y-%m-%d"):
        day = datetime1.strptime(data, format)
        next_day = day + datetime2.timedelta(days=1)
        return (day, next_day)

    def apply_filter_de_ate(self, resource, query, de, ate):
        inicio = datetime1.strptime(de, entity.DATE_FMT)
        fim = datetime1.strptime(ate, entity.DATE_FMT) +\
            datetime2.timedelta(days=1)
        return query.filter(
            and_(resource.created_at > inicio, resource.created_at < fim))

    # trata os campos "de" e "ate"
    def _convert_de_ate(self, is_date, **kwargs):
        de = kwargs.get('de', None)
        ate = kwargs.get('ate', None)
        inicio = None
        fim = None

        if de and ate:
            try:
                inicio = datetime1.strptime(de.replace(' ', '+'), '%Y-%m-%d%z')
                fim = datetime1.strptime(ate.replace(' ', '+'), '%Y-%m-%d%z') \
                    + datetime2.timedelta(days=1)

                if is_date:
                    de = de[:-5]
                    ate = ate[:-5]
                    inicio = datetime1.strptime(de, entity.DATE_FMT)
                    fim = datetime1.strptime(ate, entity.DATE_FMT) +\
                        datetime2.timedelta(days=1)

            except Exception:
                inicio = datetime1.strptime(de, entity.DATE_FMT)
                fim = datetime1.strptime(ate, entity.DATE_FMT) +\
                    datetime2.timedelta(days=1)

        return (inicio, fim)

    # função criada para filtrar na listagem um campo do tipo Date ou DateTime
    def apply_filter_de_ate_with_timezone(
            self, resource, query, **kwargs):
        attribute = kwargs.get('attribute', 'created_at')
        is_date = str(resource.__getattribute__(resource, attribute).type) == \
            'DATE'
        (de, ate) = self._convert_de_ate(is_date, **kwargs)
        if de and ate:
            if hasattr(resource, attribute):
                query = query.filter(
                    and_(getattr(resource, attribute) >= de,
                         getattr(resource, attribute) < ate))
        return query

    # função criada para filtrar na listagem de uma entidade mais
    # de um campo do tipo Date ou DateTime
    def apply_filter_multiple_de_ate_with_timezone(
            self, resource, query, **kwargs):
        attributes_filter = kwargs.get('attributes_filter', '')
        attributes_filter = attributes_filter.split(',')
        de_filter = kwargs.get('de_filter', '')
        de_filter = de_filter.split(',')
        ate_filter = kwargs.get('ate_filter', '')
        ate_filter = ate_filter.split(',')

        tamanho = len(attributes_filter)

        if not (tamanho == len(de_filter) and tamanho == len(ate_filter)):
            return query

        for i in range(tamanho):
            attribute = attributes_filter[i]
            if attribute == '':
                break
            is_date = str(
                resource.__getattribute__(resource, attribute).type) == 'DATE'
            data = {
                'de': de_filter[i],
                'ate': ate_filter[i]
            }
            (de, ate) = self._convert_de_ate(is_date, **data)
            if de and ate:
                if hasattr(resource, attribute):
                    query = query.filter(
                        and_(getattr(resource, attribute) >= de,
                             getattr(resource, attribute) < ate))
        return query
