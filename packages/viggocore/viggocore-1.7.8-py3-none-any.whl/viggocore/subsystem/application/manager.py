from sqlalchemy import func, or_, and_
from viggocore.subsystem.application.resource import Application
from typing import List
from viggocore.common import exception
from viggocore.common.input import RouteResource, InputResource, \
    InputResourceUtils
from viggocore.common.subsystem import operation, manager
from viggocore.subsystem.capability.resource import Capability
from viggocore.subsystem.capability_functionality.resource import (
    CapabilityFunctionality)
from viggocore.subsystem.capability_module.resource import CapabilityModule
from viggocore.subsystem.policy.resource import Policy
from viggocore.subsystem.policy_functionality.resource import (
    PolicyFunctionality)
from viggocore.subsystem.policy_module.resource import PolicyModule
from viggocore.subsystem.role.resource import Role
from viggocore.subsystem.route.resource import Route
from viggocore.common.subsystem.pagination import Pagination
from sqlalchemy.sql import text
from viggocore.subsystem.application.functions.manager import (
    export_capabilities_and_policies,
    export_capabilities_and_policies_sql,
    get_xlsx_import_model,
    import_capabilities_and_policies)


class Create(operation.Create):

    def pre(self, session, **kwargs) -> bool:
        self.exceptions = kwargs.pop('exceptions', [])

        return super().pre(session, **kwargs)

    def do(self, session, **kwargs):
        super().do(session)
        self.manager.create_user_capabilities_and_policies(id=self.entity.id,
                                                           session=session)
        if self.entity.name != Application.DEFAULT:
            self.manager.create_admin_capabilities_and_policies(
                id=self.entity.id, session=session, exceptions=self.exceptions)
        return self.entity


class ListManager(operation.List):

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
        not_default = kwargs.pop('not_default', False)
        query = session.query(Application)

        pagination = Pagination.get_pagination(Application, **kwargs)

        if not_default is True:
            query = query.filter(Application.name != Application.DEFAULT)

        query = self.apply_filters(query, Application, **kwargs)
        query = self.apply_pagination(query, pagination)

        result = query.all()
        return result


class CreateUserCapabilitiesAndPolicies(operation.Operation):

    def pre(self, session, id, **kwargs) -> bool:
        self.application_id = id
        self.user_resources = self.manager.bootstrap_resources.USER
        self.role_id = self.manager.api.roles().\
            get_role_by_name(role_name=Role.USER).id

        return True

    def do(self, session, **kwargs):
        self.resources = {'resources': self.user_resources}
        self.manager.api.capabilities().create_capabilities(
            id=self.application_id, **self.resources)

        self.resources['application_id'] = self.application_id
        self.manager.api.roles().create_policies(id=self.role_id,
                                                 **self.resources)


class CreateAdminCapabilitiesAndPolicies(operation.Operation):

    def _map_routes(self, routes: List[Route]) -> List[RouteResource]:
        resources = [(route.url, route.method) for route in routes]
        return resources

    def _filter_resources(self, all_resources: List[RouteResource],
                          exceptions_resources: List[RouteResource],
                          sysadmin_exclusive_resources: List[RouteResource],
                          user_resources: List[RouteResource]) \
            -> List[RouteResource]:
        resources = InputResourceUtils.diff_resources(
            all_resources, sysadmin_exclusive_resources, user_resources,
            exceptions_resources)
        return resources

    def pre(self, session, id, exceptions: List[InputResource] = [], **kwargs):
        self.application_id = id
        exceptions_resources = InputResourceUtils.parse_resources(exceptions)

        routes = self.manager.api.routes().list(active=True)
        routes_resources = self._map_routes(routes)

        self.admin_role_id = self.manager.api.roles().\
            get_role_by_name(role_name=Role.ADMIN).id

        self.admin_resources = self._filter_resources(
            routes_resources, exceptions_resources,
            self.manager.bootstrap_resources.SYSADMIN_EXCLUSIVE,
            self.manager.bootstrap_resources.USER)
        return True

    def do(self, session, **kwargs):
        self.resources = {'resources': self.admin_resources}
        self.manager.api.capabilities().create_capabilities(
            id=self.application_id, **self.resources)

        self.resources['application_id'] = self.application_id
        self.manager.api.roles().create_policies(id=self.admin_role_id,
                                                 **self.resources)


class CreateCapabilitiesWithExceptions(operation.Operation):

    def _filter_resources(self, routes: List[Route],
                          exceptions: List[RouteResource],
                          sysadmin_exclusive_resources: List[RouteResource],
                          user_resources: List[RouteResource]) \
            -> List[RouteResource]:
        all_resources = [(route.url, route.method) for route in routes]
        resources = InputResourceUtils.diff_resources(
            all_resources, sysadmin_exclusive_resources, user_resources,
            exceptions)
        return resources

    def pre(self, session, id: str, **kwargs):
        self.application_id = id
        exceptions = kwargs.get('exceptions', None)

        if not self.application_id or exceptions is None:
            raise exception.BadRequest()

        routes = self.manager.api.routes().list(active=True)
        exceptions_resources = InputResourceUtils.parse_resources(exceptions)
        self.resources = self.\
            _filter_resources(routes,
                              exceptions_resources,
                              self.manager.bootstrap_resoures.
                              SYSADMIN_EXCLUSIVE,
                              self.manager.bootstrap_resources.USER)

        return self.driver.get(id, session=session) is not None

    def do(self, session, **kwargs):
        data = {'resources', self.resources}
        self.manager.api.capabilities().\
            create_capabilities(id=self.application_id, **data)


class GetRoles(operation.Operation):

    def pre(self, session, id, **kwargs):
        self.application_id = id
        return self.driver.get(id, session=session) is not None

    def do(self, session, **kwargs):
        roles = session.query(Role). \
            join(Policy). \
            join(Capability). \
            filter(and_(Capability.application_id == self.application_id,
                        Role.name != Role.USER)). \
            distinct().all()

        roles_module = session.query(Role). \
            join(PolicyModule, Role.id == PolicyModule.role_id). \
            join(CapabilityModule,
                 CapabilityModule.id == PolicyModule.capability_module_id). \
            filter(and_(CapabilityModule.application_id == self.application_id,
                        Role.name != Role.USER)). \
            distinct().all()

        roles_functionality = session.query(Role). \
            join(PolicyFunctionality,
                 Role.id == PolicyFunctionality.role_id). \
            join(CapabilityFunctionality,
                 CapabilityFunctionality.id ==
                 PolicyFunctionality.capability_functionality_id). \
            filter(and_(CapabilityFunctionality.application_id ==
                        self.application_id,
                        Role.name != Role.USER)). \
            distinct().all()

        roles += roles_module
        roles += roles_functionality
        return set(roles)


class UpdateSettings(operation.Update):

    def pre(self, session, id: str, **kwargs) -> bool:
        self.settings = kwargs
        if self.settings is None or not self.settings:
            raise exception.BadRequest("Erro! There is not a setting")
        return super().pre(session=session, id=id)

    def do(self, session, **kwargs):
        result = {}
        for key, value in self.settings.items():
            new_value = self.entity.update_setting(key, value)
            result[key] = new_value
        super().do(session)

        return result


class RemoveSettings(operation.Update):

    def pre(self, session, id: str, **kwargs) -> bool:
        self.keys = kwargs.get('keys', [])
        if not self.keys:
            raise exception.BadRequest('Erro! keys are empty')
        super().pre(session, id=id)

        return self.entity.is_stable()

    def do(self, session, **kwargs):
        result = {}
        for key in self.keys:
            value = self.entity.remove_setting(key)
            result[key] = value
        super().do(session=session)

        return result


class GetApplicationSettingsByKeys(operation.Get):

    def pre(self, session, id, **kwargs):
        self.keys = kwargs.get('keys', [])
        if not self.keys:
            raise exception.BadRequest('Erro! keys are empty')
        return super().pre(session, id=id)

    def do(self, session, **kwargs):
        entity = super().do(session=session)
        settings = {}
        for key in self.keys:
            value = entity.settings.get(key, None)
            if value is not None:
                settings[key] = value
        return settings


class Manager(manager.Manager):

    def __init__(self, driver):
        super().__init__(driver)
        self.create = Create(self)
        self.list = ListManager(self)
        self.create_user_capabilities_and_policies = \
            CreateUserCapabilitiesAndPolicies(self)
        self.create_admin_capabilities_and_policies = \
            CreateAdminCapabilitiesAndPolicies(self)
        self.get_roles = GetRoles(self)
        self.update_settings = UpdateSettings(self)
        self.remove_settings = RemoveSettings(self)
        self.get_application_settings_by_keys = \
            GetApplicationSettingsByKeys(self)
        self.export_capabilities_and_policies_sql = (
            export_capabilities_and_policies_sql
            .ExportCapabilitiesAndPoliciesSql(self))
        self.export_capabilities_and_policies = (
            export_capabilities_and_policies
            .ExportCapabilitiesAndPolicies(self))
        self.import_capabilities_and_policies = (
            import_capabilities_and_policies
            .ImportCapabilitiesAndPolicies(self))
        self.get_xlsx_import_model = (
            get_xlsx_import_model.GetXlsxImportModel(self))
