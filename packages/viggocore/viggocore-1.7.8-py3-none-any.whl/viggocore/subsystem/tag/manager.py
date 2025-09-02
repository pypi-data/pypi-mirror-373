from viggocore.common.subsystem.pagination import Pagination
from viggocore.common.subsystem import manager, operation
from viggocore.common import exception
from sqlalchemy import func, or_
from viggocore.subsystem.tag.resource import Tag
from sqlalchemy.sql import text


class List(operation.List):

    def apply_filters(self, query, resource, **kwargs):
        for k, v in kwargs.items():
            if hasattr(resource, k):
                if k == 'tag':
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
                elif k == 'tag_name':
                    values = v
                    if len(v) > 0 and v[0] == '#':
                        values = v[1:]
                    filter_tags = []
                    query = query.filter(
                        getattr(resource, k) == '#' + str(values) + ' ')
                elif isinstance(v, str) and '%' in v:
                    normalize = func.viggocore_normalize
                    query = query.filter(normalize(getattr(resource, k))
                                         .ilike(normalize(v)))
                else:
                    query = query.filter(getattr(resource, k) == v)

        return query

    def apply_pagination(self, query, pagination: Pagination):
        if (pagination.order_by is not None and pagination.page is not None
                and pagination.page_size is not None):
            query = query.order_by(text(pagination.order_by))

        if pagination.page_size is not None:
            query = query.limit(pagination.page_size)
            if pagination.page is not None:
                query = query.offset(pagination.page * pagination.page_size)

        return query

    def do(self, session, **kwargs):
        query = session.query(Tag)

        pagination = Pagination.get_pagination(Tag, **kwargs)

        query = self.apply_filters(query, Tag, **kwargs)
        query = self.apply_pagination(query, pagination)

        result = query.all()
        return result


class GetTagsFromEntity(operation.List):

    def pre(self, **kwargs):
        self.entity_name = kwargs.get('entity_name', None)
        self.domain_id = kwargs.get('domain_id', None)
        if not self.entity_name or not self.domain_id:
            raise exception.BadRequest(
                'entity_name and domain_id are required')
        if ',' in self.entity_name:
            self.entity_name = self.entity_name.split(',')
        else:
            self.entity_name = [self.entity_name]
        return True

    def do(self, session, **kwargs):
        query_model = (
            ' UNION ' +
            'SELECT DISTINCT UNNEST(STRING_TO_ARRAY(tag, \' \', \'\'))' +
            ' AS tag FROM {entity_name} ' +
            f'WHERE domain_id = \'{self.domain_id}\'')
        query_tables = ''
        for entity_name in self.entity_name:
            query_tables += query_model.format(entity_name=entity_name)
        sql_query = (
            'SELECT aux.tag ' +
            f'FROM ( SELECT NULL AS tag {query_tables}) AS aux')

        tag_name = kwargs.get('tag_name', None)
        if tag_name:
            sql_query += (f' WHERE aux.tag ILIKE \'%{tag_name}\'')

        sql_query += ' ORDER BY aux.tag ASC'

        page = kwargs.get('page', None)
        page_size = kwargs.get('page_size', None)

        if page and page_size:
            sql_query += (f' LIMIT {int(page_size)} OFFSET {int(page)}')

        rs = session.execute(sql_query.format(self.entity_name, self.domain_id))
        response = [r._mapping['tag'] for r in rs
                    if r._mapping['tag'] is not None]
        return response


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
        self.get_tags_from_entity = GetTagsFromEntity(self)
