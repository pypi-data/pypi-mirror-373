from viggocore.common import manager, exception
from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.subsystem.module.resource \
    import Module, ModuleFunctionality
from viggocore.subsystem.functionality.resource \
    import Functionality
from sqlalchemy import func, and_


class Create(operation.Create):

    def _get_domain_default(self):
        domains = self.manager.api.domains().list(name='default')
        if len(domains) > 0:
            return domains[0]
        else:
            raise exception.NotFound('Default domain not found.')

    def _validar_name(self, name):
        if self.manager.verify_if_exists(name=name):
            raise exception.BadRequest(
                'There is already a module with this name.')

    def pre(self, session, **kwargs):
        name = kwargs.get('name', None)
        self._validar_name(name)
        domain = self._get_domain_default()
        domain_id = domain.id
        kwargs['code'] = self.manager.api.domain_sequences().\
            get_nextval(id=domain_id, name=Module.CODE_SEQUENCE)
        return super().pre(session, **kwargs)


class AddFunctionalities(operation.Update):

    def do(self, session, **kwargs):
        functionalities = kwargs.pop("functionalities", [])
        functionality_ids = [
            r.get('functionality_id', None) for r in functionalities]
        entity = self.entity.add_functionalities(functionality_ids)
        super().do(session=session)
        return entity


class RmFunctionalities(operation.Update):

    def do(self, session, **kwargs):
        functionalities = kwargs.pop("functionalities", [])
        functionality_ids = [
            r.get('functionality_id', None) for r in functionalities]
        entity = self.entity.rm_functionalities(functionality_ids)
        super().do(session=session)
        return entity


class GetAvailableFunctionalitys(operation.List):

    def do(self, session, **kwargs):
        # remove from kwargs to not be passed in the apply filters function
        id = kwargs.pop("id", None)
        query = session.query(Functionality). \
            join(ModuleFunctionality,
                 and_(ModuleFunctionality.functionality_id == Functionality.id,
                      ModuleFunctionality.module_id == id),
                 isouter=True) \
            .filter(ModuleFunctionality.module_id.is_(None))  # noqa
        query = self.manager.apply_filters(query, Functionality, **kwargs)
        query = query.distinct()

        dict_compare = {}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Functionality, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Functionality)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class GetSelectedFunctionalitys(operation.Get):

    def do(self, session, **kwargs):
        # remove from kwargs to not be passed in the apply filters function
        id = kwargs.pop("id", None)
        query = session.query(Functionality). \
            join(ModuleFunctionality,
                 ModuleFunctionality.functionality_id == Functionality.id). \
            join(Module,
                 ModuleFunctionality.module_id == Module.id)\
            .filter(Module.id == id)
        query = self.manager.apply_filters(query, Functionality, **kwargs)
        query = query.distinct()

        dict_compare = {}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Functionality, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Functionality)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class VerifyIfExists(operation.List):

    def do(self, session, **kwargs):
        normalize = func.viggocore_normalize
        name = kwargs.pop('name', None)
        if name is None:
            raise exception.BadRequest('Name is required.')
        query = session.query(Module). \
            filter(normalize(getattr(Module, 'name'))
                   .ilike(normalize(name))).\
            distinct()
        result = query.all()

        if len(result) > 0:
            return True
        else:
            return False


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.add_functionalities = AddFunctionalities(self)
        self.rm_functionalities = RmFunctionalities(self)
        self.get_available_functionalities = GetAvailableFunctionalitys(self)
        self.get_selected_functionalities = GetSelectedFunctionalitys(self)
        self.verify_if_exists = VerifyIfExists(self)
