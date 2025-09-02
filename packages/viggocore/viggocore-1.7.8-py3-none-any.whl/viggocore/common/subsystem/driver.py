import uuid
from viggocore.common.subsystem.pagination import Pagination
from viggocore.common.subsystem.entity import DATE_FMT
from datetime import datetime as datetime1
import datetime as datetime2
from typing import Any, Type

from viggocore.common import exception
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import exc
from sqlalchemy.sql import text

from viggocore.common.subsystem.transaction_manager import TransactionManager


class Driver(object):

    def __init__(self, resource: Type[Any],
                 transaction_manager: TransactionManager) -> None:
        self.resource = resource
        self.transaction_manager = transaction_manager

    def removeId(self, entity_aux):
        new_id = uuid.uuid4().hex

        if entity_aux.get('id') is not None:
            new_id = entity_aux.pop('id')

        return new_id

    def instantiate(self, **kwargs):
        try:
            embedded = {}
            for attr in self.resource.embedded():
                if attr not in kwargs:
                    raise Exception(
                        f'O campo embedded {attr} é obrigatório em ' +
                        f'{self.resource.__name__}.')
                embedded.update({attr: kwargs.pop(attr)})

            instance = self.resource(**kwargs)

            for attr in embedded:
                value = embedded[attr]
                var = getattr(self.resource, attr)
                # TODO(samueldmq): is this good enough? should we discover it?
                mapped_attr = {self.resource.individual() + '_id': instance.id}
                if isinstance(value, list):
                    setattr(instance, attr, [var.property.mapper.class_(
                        id=self.removeId(ref), **dict(ref, **mapped_attr))
                        for ref in value])
                else:
                    # TODO(samueldmq): id is inserted here. it is in the
                    # manager for the entities. do it all in the resource
                    # contructor
                    setattr(instance, attr, var.property.mapper.class_(
                        id=uuid.uuid4().hex, **dict(value, **mapped_attr)))
        except Exception as exec:
            # TODO(samueldmq): replace with specific exception
            message = ''.join(exec.args)
            raise exception.BadRequest(message)

        return instance

    def create(self, entity, session):
        if not entity.is_stable():
            raise exception.PreconditionFailed()
        session.add(entity)
        session.flush()

    def update(self, entity, data, session):
        # try:
        #     entity = self.get(id, session)
        # except exc.NoResultFound:
        #     raise exception.NotFound()

        for attr in self.resource.embedded():
            if attr in data:
                value = data.pop(attr)
                var = getattr(self.resource, attr)
                # TODO(samueldmq): is this good enough? should we discover it?
                mapped_attr = {self.resource.individual() + '_id': id}
                if isinstance(value, list):
                    setattr(entity, attr, [var.property.mapper.class_(
                        id=self.removeId(ref), **dict(ref, **mapped_attr))
                        for ref in value])
                else:
                    # TODO(samueldmq): id is inserted here. it is in the
                    # manager for the entities. do it all in the resource
                    # contructor
                    setattr(entity, attr, var.property.mapper.class_(
                        id=uuid.uuid4().hex, **dict(value, **mapped_attr)))

        for key, value in data.items():
            if hasattr(entity, key):
                try:
                    setattr(entity, key, value)
                except AttributeError:
                    raise exception.BadRequest(
                        f'Error! The attribute {key} is read only')
            else:
                raise exception.BadRequest(
                    f'Error! The attribute {key} not exists')

        if not entity.is_stable():
            raise exception.PreconditionFailed()
        session.flush()
        return entity

    def delete(self, entity, session):
        session.delete(entity)
        session.flush()

    def get(self, id, session):
        try:
            query = session.query(self.resource).filter_by(id=id)
            result = query.one()
        except exc.NoResultFound:
            raise exception.NotFound()

        return result

    def list(self, session, **kwargs):
        if 'query' in kwargs.keys():
            query = kwargs.pop('query', None)
            pagination = Pagination.get_pagination(self.resource, **kwargs)

            query = self.apply_filters(query, self.resource, **kwargs)
            pagination.adjust_dinamic_order_by(self.resource)
            query = self.apply_pagination(query, pagination)

            result = query.all()
            result = list(map(lambda x: x[0], result))
            return result
        else:
            query = session.query(self.resource)

            pagination = Pagination.get_pagination(self.resource, **kwargs)

            query = self.apply_filters(query, self.resource, **kwargs)
            query = self.apply_pagination(query, pagination)

            result = query.all()
            return result

    def count(self, session, **kwargs):
        try:
            # TODO(JogeSilva): improve filtering so as not to ignore parameters
            # that are attributes of an entity to include
            query = session.query(self.resource.id)
            rows = self.apply_filters(query, self.resource, **kwargs).count()
            result = rows
        except exc.NoResultFound:
            raise exception.NotFound()

        return result

    def activate_or_deactivate_multiple_entities(self, session, **kwargs):
        updated_at = kwargs.pop('updated_at', None)
        updated_by = kwargs.pop('updated_by', None)
        active = kwargs.pop('active', None)

        entities = self.list_multiple_selection(session, **kwargs)
        key = 'active'

        for entity in entities:
            if hasattr(entity, key):
                setattr(entity, key, active)
                if updated_at is not None:
                    setattr(entity, 'updated_at', updated_at)
                if updated_by is not None:
                    setattr(entity, 'updated_by', updated_by)
            else:
                raise exception.BadRequest(
                    f'Error! The attribute {key} not exists.')

            if not entity.is_stable():
                raise exception.PreconditionFailed()
        session.flush()
        return entities

    def _parse_list_options(self, filters):
        key = filters.pop('list_options', None)
        _filters = filters.copy()
        options = {
            'ACTIVE_ONLY': True,
            'INACTIVE_ONLY': False
        }
        if key in options.keys():
            _filters['active'] = options[key]
        return _filters

    def list_multiple_selection(self, session, **kwargs):
        '''
            fields that can be passed in kwargs:

            dict_compare
            resource
            query

            the possibility of passing these fields as parameters makes
            the function generic.
        '''

        dict_compare = kwargs.pop('dict_compare', {})
        only_first_column = kwargs.pop('only_first_column', False)
        multiple_selection = kwargs.get('multiple_selection', None)
        if multiple_selection is None:
            raise exception.BadRequest('multiple_selection is required.')

        resource_filtro = self.resource
        resource = kwargs.pop('resource', None)
        if resource is not None:
            resource_filtro = resource

        if 'query' in kwargs.keys():
            query = kwargs.pop('query', None)
        else:
            query = session.query(resource_filtro)

        selected_list = multiple_selection.get('selected_list', [])
        unselected_list = multiple_selection.get('unselected_list', [])

        if len(selected_list) > 0:
            query = query.filter(resource_filtro.id.in_(selected_list))
        else:
            if len(unselected_list) > 0:
                query = query.filter(
                    resource_filtro.id.not_in(unselected_list))
            if 'list_options' in kwargs.keys():
                kwargs = self._parse_list_options(kwargs)
            query = self.apply_filters(query, resource_filtro, **kwargs)
            query = self.apply_filters_includes(query, dict_compare, **kwargs)
            query = self.apply_filter_de_ate_with_timezone(
                resource_filtro, query, **kwargs)

        query = query.distinct()
        result = query.all()

        if only_first_column:
            result = list(map(lambda x: x[0], result))

        return result

    def _is_id(self, k):
        k = k.split('_')[-1]
        return k == 'id'

    def apply_filter_individual(self, query, resource, k, v):
        # verifica se o valor é do tipo string
        isinstance_aux = isinstance(v, str)
        # pega o atributo da classe para verificar se o campo da
        # classe é do tipo string
        attr = getattr(resource, k)

        if self._is_id(k):
            query = query.filter(getattr(resource, k) == v)
        elif k == 'tag':
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
        elif isinstance_aux and '%' in v:
            normalize = func.viggocore_normalize
            query = query.filter(
                normalize(getattr(resource, k)).ilike('%' + normalize(v)))
        elif isinstance_aux and attr.type.python_type is str:
            normalize = func.viggocore_normalize
            query = query.filter(
                normalize(getattr(resource, k)) == normalize(v))
        else:
            query = query.filter(getattr(resource, k) == v)

        return query

    def apply_filter_list(self, query, resource, k, v):
        # verifica se o valor é do tipo string
        isinstance_aux = isinstance(v[0], str)
        # pega o atributo da classe para verificar se o campo da
        # classe é do tipo string
        attr = getattr(resource, k)

        # verifica o tipo do primeiro campo da lista
        if self._is_id(k):
            query = query.filter(getattr(resource, k).in_(v))
        elif isinstance_aux and '%' in v[0]:
            normalize = func.viggocore_normalize
            # monta uma lista com os filtros para aplicar o "or"
            filtro = [
                normalize(getattr(resource, k)).ilike('%' + normalize(v_aux))
                for v_aux in v]
            # aplica os filtros
            query = query.filter(or_(*filtro))
        elif isinstance_aux and attr.type.python_type is str:
            normalize = func.viggocore_normalize
            # monta uma lista com os filtros para aplicar o "or"
            filtro = [
                normalize(getattr(resource, k)) == normalize(v_aux)
                for v_aux in v]
            # aplica os filtros
            query = query.filter(or_(*filtro))
        else:
            # se for tipo numérico ou outro tipo, aplica o in sem normalize
            query = query.filter(getattr(resource, k).in_(v))

        return query

    def apply_filters(self, query, resource, **kwargs):
        for k, v in kwargs.items():
            if hasattr(resource, k):
                # verifica se não foi passada uma lista de valores
                if not isinstance(v, list):
                    query = self.apply_filter_individual(query, resource, k, v)
                else:
                    query = self.apply_filter_list(query, resource, k, v)

        return query

    def apply_pagination(self, query, pagination: Pagination):
        if (pagination.order_by is not None):
            query = query.order_by(text(pagination.order_by))

        if pagination.page_size is not None:
            query = query.limit(pagination.page_size)
            if pagination.page is not None:
                query = query.offset(pagination.page * pagination.page_size)

        return query

    def apply_filters_includes(self, query, dict_compare, **kwargs):
        for k, v in kwargs.items():
            if '.' in k:
                # attribute é o campo da classe do include que deve ser
                # filtrado
                attribute = k.split('.')[-1]
                # individual é a chave que irá identificar qual resource usar
                individual = k.split('.')[0]
                # pefa o resource pelo campo "individual"
                resource = dict_compare.get(individual, None)
                if resource is None:
                    individual += '.'
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

    def _convert_de_ate(self, **kwargs):
        de = kwargs.get('de', None)
        ate = kwargs.get('ate', None)
        inicio = None
        fim = None

        if de and ate:
            try:
                inicio = datetime1.strptime(de.replace(' ', '+'), '%Y-%m-%d%z')
                fim = datetime1.strptime(ate.replace(' ', '+'), '%Y-%m-%d%z') \
                    + datetime2.timedelta(days=1)

            except Exception:
                inicio = datetime1.strptime(de, DATE_FMT)
                fim = datetime1.strptime(ate, DATE_FMT) +\
                    datetime2.timedelta(days=1)

        return (inicio, fim)

    def apply_filter_de_ate_with_timezone(
            self, resource, query, **kwargs):
        attribute = kwargs.get('attribute', 'created_at')
        (de, ate) = self._convert_de_ate(**kwargs)
        if de and ate:
            if hasattr(resource, attribute):
                query = query.filter(
                    and_(getattr(resource, attribute) >= de,
                         getattr(resource, attribute) < ate))
        return query

    def _aplicar_filtro_status_periodo_data(self, query, resource, **kwargs):
        evento_status = kwargs.get('evento_status', None)
        evento_status_dh_de = kwargs.get('evento_status_dh_de', None)
        evento_status_dh_ate = kwargs.get('evento_status_dh_ate', None)
        campos = [evento_status, evento_status_dh_de, evento_status_dh_ate]
        if None not in campos:
            data = {
                'de': evento_status_dh_de,
                'ate': evento_status_dh_ate
            }
            (de, ate) = self.manager._convert_de_ate(is_date=False, **data)
            if de and ate:
                query = query.filter(
                    and_(resource.status_dh >= de,
                         resource.status_dh < ate,
                         resource.status == evento_status))
        return query
