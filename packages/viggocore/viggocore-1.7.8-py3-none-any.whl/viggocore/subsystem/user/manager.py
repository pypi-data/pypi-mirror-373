import os
import hashlib
import uuid

from sqlalchemy import or_, and_

from viggocore.common import exception
from viggocore.common.subsystem import manager
from viggocore.common.subsystem import operation
from viggocore.subsystem.functionality.resource import (
    FunctionalityRoute)
from viggocore.subsystem.module.resource import Module, ModuleFunctionality
from viggocore.subsystem.user.email import TypeEmail, send_email
from viggocore.subsystem.user.resource import CREATE_TYPE, User
from viggocore.subsystem.capability.resource import Capability
from viggocore.subsystem.capability_functionality.resource \
    import CapabilityFunctionality
from viggocore.subsystem.capability_module.resource import CapabilityModule
from viggocore.subsystem.domain.resource import Domain
from viggocore.subsystem.route.resource import Route
from viggocore.subsystem.grant.resource import Grant
from viggocore.subsystem.policy.resource import Policy
from viggocore.subsystem.policy_functionality.resource \
    import PolicyFunctionality
from viggocore.subsystem.policy_module.resource import PolicyModule
from viggocore.subsystem.role.resource import Role


class Create(operation.Create):

    def pre(self, session, **kwargs):
        self.role = self.manager.api.roles().get_role_by_name(
            role_name=Role.USER)
        kwargs.pop('settings', None)
        # remove o campo para não tentar instanciar User com ele
        kwargs.pop('create_type', None)
        return super().pre(session, **kwargs)

    def do(self, session, **kwargs):
        create_type = CREATE_TYPE[kwargs.pop('create_type',
                                             'GENERATE_PASSWORD')]
        # se escolher o tipo DEFAULT_PASSWORD vai atualizar a senha
        # do usuário com o hash da senha 123456
        if create_type is CREATE_TYPE.DEFAULT_PASSWORD:
            self.entity.password = ('8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92')  # noqa
        super().do(session)
        self.manager.api.grants().create(role_id=self.role.id,
                                         user_id=self.entity.id)
        return self.entity


class Update(operation.Update):

    def do(self, session, **kwargs):
        kwargs.pop('settings', None)
        return super().do(session, **kwargs)


class UpdatePassword(operation.Update):

    def _check_password(self, password, password_db):
        if not password:
            return password_db is None
        password_hash = self.manager.hash_password(password)
        return password_hash == password_db

    def pre(self, session, id, **kwargs):
        old_password = kwargs.pop('old_password', None)
        self.password = kwargs.pop('password', None)

        if not (id and self.password and old_password):
            raise exception.BadRequest()
        super().pre(session=session, id=id)

        if not self._check_password(old_password, self.entity.password):
            raise exception.BadRequest()
        return True

    def do(self, session, **kwargs):
        self.entity.password = self.manager.hash_password(self.password)
        self.entity = super().do(session)
        return self.entity


class Restore(operation.Operation):
    def pre(self, **kwargs):
        email = kwargs.get('email', None)
        domain_name = kwargs.get('domain_name', None)
        viggocore_reset_url = os.environ.get(
            'VIGGOCORE_RESET_URL', 'http://objetorelacional.com.br/#/reset/')
        self.reset_url = kwargs.get('reset_url', viggocore_reset_url)

        if not (domain_name and email and self.reset_url):
            raise exception.OperationBadRequest()

        domains = self.manager.api.domains().list(name=domain_name)
        if not domains:
            raise exception.OperationBadRequest()

        self.domain = domains[0]

        users = self.manager.api.users().list(
            email=email, domain_id=self.domain.id)
        if not users:
            raise exception.OperationBadRequest()

        self.user = users[0]

        return True

    def do(self, session, **kwargs):
        restore_type = kwargs.get('restore_type', 'EMAIL')

        if restore_type == 'EMAIL':
            self.manager.notify(
                id=self.user.id, type_email=TypeEmail.FORGOT_PASSWORD)
        elif restore_type == 'ALTERNATE_PASSWORD':
            self.password = uuid.uuid4().hex[:10]
            self.user.password = self.manager.hash_password(self.password)
            super().do(session=session, **{})

            self.manager.notify(
                id=self.user.id,
                type_email=TypeEmail.FORGOT_PASSWORLD_ALTERNATE,
                **{'alternate_pass': self.password},
            )
        else:
            raise exception.OperationBadRequest('unknown restoration type')


class Reset(operation.Update):

    def pre(self, session, id, **kwargs):
        create_type = CREATE_TYPE[kwargs.pop('create_type',
                                             'INPUT_PASSWORD')]
        if create_type is CREATE_TYPE.DEFAULT_PASSWORD:
            self.password = '123456'
        else:
            self.password = kwargs.get('password', None)
        if not (id and self.password):
            raise exception.BadRequest()
        super().pre(session=session, id=id)
        return True

    def do(self, session, **kwargs):
        # remove para não tentar usar no atualizar User
        kwargs.pop('create_type', None)
        self.entity.password = self.manager.hash_password(self.password)
        self.entity = super().do(session)
        return self.entity


class Routes(operation.Operation):

    def _get_application_id(self, session, user_id):
        result_application = session.query(Domain.application_id). \
            join(User). \
            filter(User.id == user_id). \
            first()

        if not result_application.application_id:
            raise exception.BadRequest(
                'This user is not associated with any applications')

        return result_application.application_id

    def do(self, session, user_id, **kwargs):
        response = []
        application_id = self._get_application_id(session, user_id)

        query = session.query(Route). \
            join(Capability). \
            outerjoin(Policy). \
            outerjoin(Grant, Policy.role_id == Grant.role_id). \
            outerjoin(User). \
            outerjoin(Domain,
                      and_(Domain.application_id == Capability.application_id,
                           Domain.id == User.domain_id)). \
            filter(Capability.application_id == application_id,
                   Capability.active, Route.active,
                   or_(Route.bypass,
                       and_(User.id == user_id,
                            User.active, Domain.active, Grant.active,
                            Policy.active))). \
            distinct()
        projeto = kwargs.get('projeto', None)
        if projeto is not None:
            query = query.filter(
                or_(Route.projeto.is_(None), Route.projeto.is_(projeto)))

        routes = query.all()
        response += routes

        query = session.query(Route). \
            join(FunctionalityRoute). \
            join(CapabilityFunctionality,
                 CapabilityFunctionality.functionality_id ==
                 FunctionalityRoute.functionality_id). \
            outerjoin(PolicyFunctionality). \
            outerjoin(Grant, PolicyFunctionality.role_id == Grant.role_id). \
            outerjoin(User). \
            outerjoin(Domain,
                      and_(Domain.application_id ==
                           CapabilityFunctionality.application_id,
                           Domain.id == User.domain_id)). \
            filter(CapabilityFunctionality.application_id == application_id,
                   CapabilityFunctionality.active, Route.active,
                   or_(Route.bypass,
                       and_(User.id == user_id,
                            User.active, Domain.active, Grant.active,
                            PolicyFunctionality.active))). \
            distinct()
        if projeto is not None:
            query = query.filter(
                or_(Route.projeto.is_(None), Route.projeto.is_(projeto)))

        routes = query.all()
        response += routes

        query = session.query(Route). \
            join(FunctionalityRoute). \
            join(ModuleFunctionality,
                 ModuleFunctionality.functionality_id
                 == FunctionalityRoute.functionality_id). \
            join(Module). \
            join(CapabilityModule). \
            outerjoin(PolicyModule). \
            outerjoin(Grant, PolicyModule.role_id == Grant.role_id). \
            outerjoin(User). \
            outerjoin(Domain,
                      and_(Domain.application_id ==
                           CapabilityModule.application_id,
                           Domain.id == User.domain_id)). \
            filter(CapabilityModule.application_id == application_id,
                   CapabilityModule.active, Route.active,
                   or_(Route.bypass,
                       and_(User.id == user_id,
                            User.active, Domain.active, Grant.active,
                            PolicyModule.active))). \
            distinct()
        if projeto is not None:
            query = query.filter(
                or_(Route.projeto.is_(None), Route.projeto.is_(projeto)))

        routes = query.all()
        response += routes
        response = set(response)

        return response


class Roles(operation.Operation):

    def do(self, session, user_id, **kwargs):
        roles = session.query(Role). \
            join(Grant, Grant.role_id == Role.id). \
            filter(Grant.user_id == user_id). \
            distinct(). \
            all()

        return roles


class Authorization(operation.Operation):

    def do(self, session, user_id, route, **kwargs):
        has_capabilities = session.query(User.id). \
            join(Domain). \
            join(Grant). \
            join(Role). \
            join(Policy). \
            join(Capability,
                 and_(Capability.id == Policy.capability_id,
                      Capability.application_id == Domain.application_id,
                      Capability.route_id == route.id)). \
            filter(and_(User.id == user_id,
                        or_(not route.sysadmin, Role.name == Role.SYSADMIN),
                        User.active, Domain.active, Grant.active,
                        Policy.active, Capability.active)). \
            count()

        has_capability_functionalities = session.query(User.id). \
            join(Domain). \
            join(Grant). \
            join(Role). \
            join(PolicyFunctionality). \
            join(CapabilityFunctionality,
                 and_(CapabilityFunctionality.id
                      == PolicyFunctionality.capability_functionality_id,
                      CapabilityFunctionality.application_id
                      == Domain.application_id)). \
            join(FunctionalityRoute,
                 and_(FunctionalityRoute.functionality_id
                      == CapabilityFunctionality.functionality_id,
                      FunctionalityRoute.route_id == route.id)). \
            filter(and_(User.id == user_id,
                        or_(not route.sysadmin, Role.name == Role.SYSADMIN),
                        User.active, Domain.active, Grant.active,
                        PolicyFunctionality.active,
                        CapabilityFunctionality.active)). \
            count()

        has_capability_modules = session.query(User.id). \
            join(Domain). \
            join(Grant). \
            join(Role). \
            join(PolicyModule). \
            join(CapabilityModule,
                 and_(PolicyModule.capability_module_id
                      == CapabilityModule.id,
                      CapabilityModule.application_id
                      == Domain.application_id)). \
            join(ModuleFunctionality,
                 ModuleFunctionality.module_id
                 == CapabilityModule.module_id). \
            join(FunctionalityRoute,
                 and_(FunctionalityRoute.functionality_id
                      == ModuleFunctionality.functionality_id,
                      FunctionalityRoute.route_id == route.id)). \
            filter(and_(User.id == user_id,
                        or_(not route.sysadmin, Role.name == Role.SYSADMIN),
                        User.active, Domain.active, Grant.active,
                        ModuleFunctionality.active,
                        CapabilityFunctionality.active)). \
            count()

        total = (has_capabilities + has_capability_functionalities +
                 has_capability_modules)

        return total > 0


class UploadPhoto(operation.Update):

    def pre(self, session, id, **kwargs):
        kwargs.pop('password', None)
        photo_id = kwargs.pop('photo_id', None)
        super().pre(session, id, **kwargs)

        # monta o json_anterior
        self.entity_old = {"photo_id": self.entity.photo_id}
        # monta o json_posterior
        self.entity_new = {"photo_id": photo_id}
        # atualiza a photo_id
        self.entity.photo_id = photo_id
        return self.entity.is_stable()

    def do(self, session, **kwargs):
        return super().do(session=session)


class DeletePhoto(operation.Update):

    def pre(self, session, id, **kwargs):
        kwargs.pop('password', None)
        super().pre(session, id, **kwargs)

        # monta o json_anterior
        self.entity_old = {"photo_id": self.entity.photo_id}
        # monta o json_posterior
        self.entity_new = {"photo_id": None}

        self.photo_id = self.entity.photo_id
        self.entity.photo_id = None
        return self.entity.is_stable()

    def do(self, session, **kwargs):
        return super().do(session=session)

    def post(self):
        if self.photo_id:
            self.manager.api.images().delete(id=self.photo_id)


class Notify(operation.Operation):

    def _get_sysadmin(self):
        users = self.manager.list(name=User.SYSADMIN_USERNAME)
        user = users[0] if users else None
        return user

    def pre(self, session, id, type_email, **kwargs):
        self.user = self.manager.get(id=id)
        self.type_email = type_email
        if not self.user or not self.type_email:
            raise exception.BadRequest()
        return True

    def do(self, session, **kwargs):
        alternate_pass = kwargs.get('alternate_pass', None)
        if self.type_email is TypeEmail.ACTIVATE_ACCOUNT:
            user_token = self._get_sysadmin()
        else:
            user_token = self.user

        self.token = self.manager.api.tokens().create(
            session=session, user=user_token)

        self.domain = self.manager.api.domains().get(id=self.user.domain_id)
        if not self.domain:
            raise exception.OperationBadRequest()

        send_email(
            type_email=self.type_email,
            token_id=self.token.id,
            user=self.user,
            domain=self.domain,
            alternate_pass=alternate_pass,
        )


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


class GetUserSettingsByKeys(operation.Get):

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
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update = Update(self)
        self.update_password = UpdatePassword(self)
        self.restore = Restore(self)
        self.reset = Reset(self)
        self.routes = Routes(self)
        self.upload_photo = UploadPhoto(self)
        self.delete_photo = DeletePhoto(self)
        self.notify = Notify(self)
        self.authorize = Authorization(self)
        self.roles = Roles(self)
        self.update_settings = UpdateSettings(self)
        self.remove_settings = RemoveSettings(self)
        self.get_user_settings_by_keys = GetUserSettingsByKeys(self)

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
