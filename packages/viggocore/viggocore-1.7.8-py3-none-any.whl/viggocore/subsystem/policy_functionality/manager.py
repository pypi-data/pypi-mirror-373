from viggocore.common import manager, exception
from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.subsystem.capability_functionality.resource \
    import CapabilityFunctionality
from viggocore.subsystem.policy_functionality.resource \
    import PolicyFunctionality
from viggocore.subsystem.functionality.resource \
    import Functionality
from sqlalchemy import and_


class GetAvailableFunctionalitys(operation.List):

    def pre(self, **kwargs):
        self.role_id = kwargs.get('role_id', None)
        if self.role_id is None:
            raise exception.BadRequest('role_id is required')
        self.application_id = kwargs.get('application_id', None)
        if self.application_id is None:
            raise exception.BadRequest('application_id is required')
        return super().pre(**kwargs)

    def do(self, session, **kwargs):
        query = session.query(CapabilityFunctionality, Functionality). \
            join(Functionality,
                 CapabilityFunctionality.functionality_id == Functionality.id
                 ). \
            join(PolicyFunctionality,
                 and_(PolicyFunctionality.capability_functionality_id == CapabilityFunctionality.id,  # noqa
                      PolicyFunctionality.role_id == self.role_id),
                 isouter=True). \
            filter(
                CapabilityFunctionality.application_id == self.application_id)
        query = query.filter(PolicyFunctionality.role_id.is_(None))
        query = self.manager.apply_filters(
            query, CapabilityFunctionality, **kwargs)
        query = query.distinct()

        dict_compare = {'functionality.': CapabilityFunctionality,
                        'policy_functionality.': PolicyFunctionality}
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
        response = [r[0] for r in result]

        return (response, total_rows)


class GetSelectedFunctionalitys(operation.List):

    def pre(self, **kwargs):
        self.role_id = kwargs.get('role_id', None)
        if self.role_id is None:
            raise exception.BadRequest('role_id is required')
        self.application_id = kwargs.get('application_id', None)
        if self.application_id is None:
            raise exception.BadRequest('application_id is required')
        return super().pre(**kwargs)

    def do(self, session, **kwargs):
        query = session.query(CapabilityFunctionality, PolicyFunctionality.id,
                              Functionality). \
            join(Functionality,
                 CapabilityFunctionality.functionality_id == Functionality.id
                 ). \
            join(PolicyFunctionality,
                 and_(PolicyFunctionality.capability_functionality_id == CapabilityFunctionality.id,  # noqa
                      PolicyFunctionality.role_id == self.role_id)). \
            filter(
                CapabilityFunctionality.application_id == self.application_id)
        query = self.manager.apply_filters(
            query, CapabilityFunctionality, **kwargs)
        query = query.distinct()

        dict_compare = {'functionality.': Functionality,
                        'policy_functionality.': PolicyFunctionality}
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
        response = [(r[0], r[1]) for r in result]

        return (response, total_rows)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.get_available_functionalities = GetAvailableFunctionalitys(self)
        self.get_selected_functionalities = GetSelectedFunctionalitys(self)
