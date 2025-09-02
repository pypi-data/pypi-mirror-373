from typing import Any, Type, Optional
from viggocore.common import exception
from viggocore.common.exception import BadRequest


class Pagination(object):

    def __init__(self, page: Optional[int], page_size: Optional[int],
                 order_by: Optional[str]) -> None:
        self.page = page
        self.page_size = page_size
        self.order_by = order_by

    @classmethod
    def get_pagination(cls, resource: Type[Any], **kwargs):
        try:
            page = kwargs.pop('page', None)
            page = int(page) if page is not None else None
            page_size = kwargs.pop('page_size', None)
            page_size = int(page_size) if page_size is not None else None
            order_by = kwargs.pop('order_by', None)

            name_pagination_column = 'pagination_column'

            if order_by is None and page is not None and page_size is not None \
                    and hasattr(resource, name_pagination_column):
                order_by = getattr(resource, name_pagination_column)

            if page_size is not None and page_size <= 0:
                raise exception.BadRequest(
                    'page_size must be greater than to zero')
            if page is not None and page < 0:
                raise exception.BadRequest(
                    'page must be greater than or equal to zero')

            # cls._validate_order_by(order_by, resource)
        except BadRequest as br:
            raise exception.BadRequest(br.message)
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        return cls(page=page, page_size=page_size, order_by=order_by)

    def _validate_order_by(order_by: Optional[str], resource: Type[Any]):
        if order_by is None:
            return None
        order_by_post_split = order_by.split(',')
        for item in order_by_post_split:
            splited_item = item.split()

            if len(splited_item) < 3 and len(splited_item) > 0:
                if len(splited_item) == 1 or (splited_item[1] == 'asc' or
                   splited_item[1] == 'desc'):

                    attr = splited_item[0]
                    if hasattr(resource, attr):
                        table_name = resource.__tablename__
                        columns = resource.metadata.tables[table_name].columns\
                            ._all_columns
                        columns_name = list(
                            map(lambda item: item.name, columns))
                        if attr not in columns_name:
                            raise exception.BadRequest(f'{attr} is \
                                not a column in table {table_name}')
                    else:
                        raise exception.BadRequest(f'{attr} is \
                                not a attribute in class {resource.__name__}')
                else:
                    raise exception.BadRequest('Each order_by item must be the \
                        attribute name and optionally "asc" (sort ascending) or\
                        "desc" (sort descending)')
            else:
                raise exception.BadRequest('each order_by item must be one or\
                    two words at most')

    def adjust_order_by(self, resource: Type[Any]):
        if self.order_by is not None:
            order_by_ajusted = ''
            table_name = resource.__tablename__
            order_by_post_split = self.order_by.split(',')
            for item in order_by_post_split:
                order_by_ajusted += f'{table_name}.{item},'

            self.order_by = order_by_ajusted[:-1]

    def adjust_order_by_no_distinct(self, resource: Type[Any]):
        if self.order_by is not None:
            order_by_ajusted = ''
            table_name = resource.__tablename__
            order_by_post_split = self.order_by.split(',')
            for item in order_by_post_split:
                item_aux = item.split(' ')
                if 'VARCHAR' in str(getattr(resource, item_aux[0]).type):
                    if ' ' in item:
                        order_by_ajusted += (
                            'ordenar_sem_formatacao(' +
                            f'{table_name}.{item_aux[0]}) {item_aux[1]},')
                    else:
                        order_by_ajusted += (
                            f'ordenar_sem_formatacao({table_name}.{item}),')
                else:
                    order_by_ajusted += f'{table_name}.{item},'

            self.order_by = order_by_ajusted[:-1]

    def adjust_dinamic_order_by(self, resource: Type[Any]):
        if self.order_by is not None:
            order_by_ajusted = ''
            table_name = resource.__tablename__
            order_by_post_split = self.order_by.split(',')
            for item in order_by_post_split:
                if '.' in item:
                    order_by_ajusted += f'{item},'
                else:
                    order_by_ajusted += f'{table_name}.{item},'

            self.order_by = order_by_ajusted[:-1]
