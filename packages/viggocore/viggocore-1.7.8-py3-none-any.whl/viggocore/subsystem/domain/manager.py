from sqlalchemy import and_
from viggocore.common import exception
from viggocore.common.subsystem.pagination import Pagination
from viggocore.subsystem.application.resource import Application
from viggocore.subsystem.capability.resource import Capability
from viggocore.subsystem.capability_functionality.resource \
    import CapabilityFunctionality
from viggocore.subsystem.capability_module.resource import CapabilityModule
from viggocore.subsystem.domain import tasks
from viggocore.common.subsystem import operation
from viggocore.common import manager
from viggocore.subsystem.domain.functions.manager import (
    consulta_cpf_cnpj)
from viggocore.subsystem.domain.resource import Domain
from viggocore.subsystem.functionality.resource import FunctionalityRoute
from viggocore.subsystem.image.resource import QualityImage
from viggocore.subsystem.domain.files import utils
from viggocore.common.utils import round_abnt
from viggocore.subsystem.module.resource import ModuleFunctionality
from viggocore.subsystem.policy.resource import Policy
from viggocore.subsystem.policy_functionality.resource import (
    PolicyFunctionality)
from viggocore.subsystem.policy_module.resource import PolicyModule
from viggocore.subsystem.role.resource import Role
from sqlalchemy.orm import aliased


class DomainByName(operation.Operation):

    def pre(self, session, domain_name, **kwargs):
        self.domain_name = domain_name
        return True

    def do(self, session, **kwargs):
        domains = self.manager.list(name=self.domain_name)
        if not domains:
            raise exception.NotFound('ERROR! Domain name not found')
        domain = domains[0]

        # Hide user ID and settings from public resources
        domain.created_by = None
        domain.updated_by = None

        return domain


class DomainLogoByName(operation.Operation):

    def pre(self, session, domain_name, **kwargs):
        self.domain_name = domain_name
        return True

    def do(self, session, **kwargs):
        domains = self.manager.list(name=self.domain_name)
        if not domains:
            raise exception.NotFound('ERROR! Domain name not found')
        domain = domains[0]

        if domain.logo_id is None:
            raise exception.NotFound('ERROR! Domain logo not found')

        kwargs['quality'] = kwargs.get('quality', QualityImage.med)
        return self.manager.api.images().get(id=domain.logo_id, **kwargs)


class UploadLogo(operation.Update):

    def pre(self, session, id, token, file, **kwargs):
        self.file = file
        self.token = token

        return super().pre(session, id, **kwargs)

    def do(self, session, **kwargs):
        kwargs = {}
        kwargs['domain_id'] = self.entity.id
        kwargs['user_id'] = self.token.user_id
        kwargs['type_image'] = 'DomainLogo'

        image = self.manager.api.images().create(file=self.file, **kwargs)

        # monta o json_anterior
        self.entity_old = {"logo_id": self.entity.logo_id}
        # monta o json_posterior
        self.entity_new = {"logo_id": image.id}
        # atualiza a photo_id
        self.entity.logo_id = image.id

        return super().do(session=session)


class RemoveLogo(operation.Update):

    def do(self, session, **kwargs):
        logo_id = self.entity.logo_id
        self.entity.logo_id = None

        # monta o json_anterior
        self.entity_old = {"logo_id": logo_id}
        # monta o json_posterior
        self.entity_new = {"logo_id": None}

        entity = super().do(session=session)

        if logo_id and entity is not None:
            self.manager.api.images().delete(id=logo_id)

        return


class Register(operation.Create):

    def _register_domain(self, domain_name, domain_display_name,
                         application_id, username, email, password):
        self.domain = self.manager.api.domains().create(
            application_id=application_id, name=domain_name,
            display_name=domain_display_name,
            addresses=[], contacts=[], active=False)

        self.user = self.manager.api.users().create(
            name=username, email=email, domain_id=self.domain.id, active=False)

        self.manager.api.users().reset(id=self.user.id, password=password)

    def pre(self, session, username, email, password,
            domain_name, domain_display_name, application_name):
        self.username = username
        self.email = email
        self.password = password
        self.domain_name = domain_name
        self.domain_display_name = domain_display_name
        self.application_name = application_name

        user_params_ok = username and email and password
        app_params_ok = domain_name and application_name
        if not user_params_ok and app_params_ok:
            raise exception.BadRequest(
                'ERROR! Not enough data to register domain')

        applications = \
            self.manager.api.applications().list(name=application_name)
        if not applications:
            raise exception.BadRequest('ERROR! Application name not found.')
        self.application = applications[0]

        return True

    def do(self, session, **kwargs):
        domains = self.manager.api.domains().list(name=self.domain_name)
        if not domains:
            self._register_domain(
                self.domain_name, self.domain_display_name,
                self.application.id, self.username, self.email, self.password)
        else:
            self.domain = domains[0]
            domain = domains[0]

            users = self.manager.api.users().list(email=self.email,
                                                  domain_id=domain.id)

            if domain.active:
                raise exception.BadRequest('Domain already activated')

            if domain.name == self.domain_name:
                raise exception.BadRequest('Domain already registered')

            if not users:
                raise exception.BadRequest('User not found')

            self.user = users[0]
            self.manager.api.users().reset(id=self.user.id,
                                           password=self.password)

        return True

    def post(self):
        # The notification don't be part of transaction must be on post
        tasks.send_email(self.user.id)


class Activate(operation.Create):

    def pre(self, session, token_id, domain_id, user_admin_id):
        if not (user_admin_id or domain_id):
            raise exception.BadRequest(
                'ERROR! Not enough data to Activate Domain')

        self.token_id = token_id
        self.domain_id = domain_id
        self.user_admin_id = user_admin_id

        roles = self.manager.api.roles().list(name='Admin')
        if not roles:
            raise exception.BadRequest('ERROR! Role Admin not found')
        self.role_admin = roles[0]

        return True

    def do(self, session, **kwargs):
        self.manager.api.domains().update(id=self.domain_id, active=True)
        self.manager.api.users().update(id=self.user_admin_id, active=True)
        self.manager.api.grants().create(user_id=self.user_admin_id,
                                         role_id=self.role_admin.id)
        self.manager.api.tokens().delete(id=self.token_id)

        domain = self.manager.api.domains().get(id=self.domain_id)
        if not domain:
            raise exception.BadRequest('ERROR! Domain not found')

        return domain


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


class GetDomainSettingsByKeys(operation.Get):

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


class SendEmailActivateAccount(operation.Create):

    def pre(self, session, **kwargs):
        return True

    def do(self, session, **kwargs):
        domain_name = kwargs.get('domain_name', None)
        email = kwargs.get('email', None)
        domains = self.manager.api.domains().list(name=domain_name)
        if not domains:
            raise exception.NotFound('Domain not found')

        domain = domains[0]

        users = self.manager.api.users().list(email=email,
                                              domain_id=domain.id,
                                              name='admin')

        if domain.active:
            raise exception.BadRequest('Domain already activated')

        if not users:
            raise exception.NotFound('Invalid information')

        self.user = users[0]

        return True

    def post(self):
        # The notification don't be part of transaction must be on post
        tasks.send_email(self.user.id)


class GetFilesSize(operation.Get):

    def pre(self, session, id, **kwargs):
        return super().pre(session, id=id)

    def do(self, session, **kwargs):
        response_dict = utils.get_size(domain_id=self.id, **kwargs)
        return response_dict


class GetUsageInfoByDomain(operation.List):

    PRECISION = 2

    # vai pegar os totais de linhas em cada tabela do banco por domínio
    def _get_totals_by_domain(self, session):
        msg = """
            É necessário implementar a função get_totals_by_domain no
            projeto específico para garantir que as tabelas listadas e
            filtradas por domínio são apenas as importantes. O retorno
            deve ser uma lista de dicionários no seguinte formato:

            return = [
                {
                    'table_name': None,
                    'total': None,
                    'domain_name': None,
                    'application_id': None,
                    'application_name': None
                    'domain_id': None,
                    'active': None
                }
            ]
        """
        raise exception.BadRequest(msg)

    # vai pegar os totais de linhas em cada tabela do banco
    def _get_totals_db(self, session):
        msg = """
            É necessário implementar a função _get_totals_db no
            projeto específico para garantir que as tabelas listadas
            são apenas as importantes para aquele projeto. O retorno
            deve ser uma lista de dicionários no seguinte formato:

            return = {
                "entity_name1": total1,
                "entity_name2": total2,
                "entity_name3": total3
            }
        """
        raise exception.BadRequest(msg)

    def _normalizar_tamanho(self, tamanho: str):
        numero, unidade = tamanho.split(' ')
        numero = int(numero)
        if unidade == 'bytes':
            return numero
        elif unidade == 'kB':
            return (numero * 1024)
        elif unidade == 'MB':
            return (numero * 1024 * 1024)
        elif unidade == 'GB':
            return (numero * 1024 * 1024 * 1024)

    def _get_value_or_default(self, value, tipo):
        if value is not None:
            return value
        else:
            if tipo is str:
                return ''
            elif tipo is int:
                return 0

    # vai pegar o total de espaço de disco ocupado por cada tabela do banco
    def _get_disk_space_totals_by_db(self, session):
        from viggocore.subsystem.domain.sql.disk_space_totals_by_db \
            import QUERY
        rs = session.execute(QUERY)
        response = [r for r in rs]

        response_dict = {
            r[0]: self._normalizar_tamanho(r[1])
            for r in response}
        return response_dict

    # função responsável por pegar o objeto constante com as constantes para
    # realizar o cálculo
    def _get_const(self, application_id, table_name):
        for const in self.constants:
            if const.application_id == application_id and\
               const.table_name == table_name:
                return (const.p_processos, const.p_acessos_db)
        return (1, 1)

    # vai pegar as "constantes" que serão usadas para aplicar os pesos
    # de cada cálculo
    def _get_constant_for_calculation(self):
        self.constants, _ = self.manager.api.constant_for_calculations().list(
            active=True)

    def _apply_calculations(self):
        for i in range(0, len(self.totals_by_domain)):
            total = self.totals_by_domain[i].get('total', 0)
            table_name = self.totals_by_domain[i].get('table_name', '')
            # domain_name = self.totals_by_domain[i].get('domain_name', '')
            application_id = self.totals_by_domain[i].get(
                'application_id', '')
            percent = (total / self.totals_db.get(table_name, 1))
            disk_space_table = self.disk_space_totals_by_db_dict.get(
                table_name, 0)

            self.totals_by_domain[i]['percent'] = percent
            self.totals_by_domain[i]['total_space_disc_bank'] = (
                percent * disk_space_table)

            p_processos, p_acessos_db = self._get_const(
                application_id, table_name)
            self.totals_by_domain[i]['total_process'] = total * p_processos
            self.totals_by_domain[i]['total_acess_db'] = total * p_acessos_db

    def _make_base_dict(self, domain_name):
        return {
            'application_id': None,
            'application_name': None,
            'domain_id': None,
            'domain_name': domain_name,
            'total_entities': 0,
            'total_space_disc_bank': 0,
            'total_process': 0,
            'total_acess_db': 0,
            'total_space_disc_file': 0
        }

    def _group_by_domain(self):
        grand_totals_dict = {
            'total_entities': 0,
            'total_space_disc_bank': 0,
            'total_process': 0,
            'total_acess_db': 0,
            'total_space_disc_file': 0
        }

        domains = list(
            set(map(lambda x: x.get('domain_name', ''), self.totals_by_domain)))
        domains_dict = list(map(lambda x: self._make_base_dict(x), domains))
        response = []
        for dc in domains_dict:
            domain_name = dc.get('domain_name', '')
            list_aux = list(filter(lambda x: x['domain_name'] == domain_name,
                                   self.totals_by_domain))

            # preenche os campos do dicionário que estavam faltando
            dc['application_name'] = list_aux[0].get('application_name', None)
            dc['application_id'] = list_aux[0].get('application_id', None)
            dc['domain_id'] = list_aux[0].get('domain_id', None)
            dc['active'] = list_aux[0].get('active', False)

            # soma todos os totais de um domínio
            for aux in list_aux:
                total_entities = aux.get('total', 0)
                total_space_disc_bank = aux.get('total_space_disc_bank', 0)
                total_process = aux.get('total_process', 0)
                total_acess_db = aux.get('total_acess_db', 0)

                dc['total_entities'] += total_entities
                dc['total_space_disc_bank'] += total_space_disc_bank
                dc['total_process'] += total_process
                dc['total_acess_db'] += total_acess_db

            # calcula o espaço ocupado por arquivos no servidor para este
            # domínio
            dc['total_space_disc_file'] = self.manager.get_files_size(
                id=dc['domain_id'], de=self.de, ate=self.ate).get('BYTES', 0)

            # faz a somatória total de todos os campos
            grand_totals_dict['total_entities'] += dc['total_entities']
            grand_totals_dict['total_space_disc_bank'] += \
                dc['total_space_disc_bank']
            grand_totals_dict['total_process'] += dc['total_process']
            grand_totals_dict['total_acess_db'] += dc['total_acess_db']
            grand_totals_dict['total_space_disc_file'] += \
                dc['total_space_disc_file']

            response.append(dc)

        return (response, grand_totals_dict)

    def _calculate_cost_individual(self, usage, cost):
        return usage * float(cost)

    def _calculate_cost(self, usage):
        return ((usage * float(self.cost_servidor)) +
                (usage * float(self.cost_operacional)) +
                (usage * float(self.cost_administrativo)))

    def _calculate_usage(
            self, percent_total_entities, percent_total_space_disc_bank,
            percent_total_process, percent_total_access_db,
            percent_total_space_disc_file):
        usage_storage_bank = (
            float(percent_total_space_disc_bank) * self.p_storage_bank)
        usage_storage_file = (
            float(percent_total_space_disc_file) * self.p_storage_file)
        usage_process = float(percent_total_process) * self.p_process
        usage_access_db = float(percent_total_access_db) * self.p_access_db

        return (usage_storage_bank + usage_storage_file + usage_process +
                usage_access_db)

    def _normalize_values_response(self, response_item):
        response_item['total_space_disc_bank'] = round_abnt(
            response_item['total_space_disc_bank'], self.PRECISION)
        response_item['total_process'] = round_abnt(
            response_item['total_process'], self.PRECISION)
        response_item['total_acess_db'] = round_abnt(
            response_item['total_acess_db'], self.PRECISION)
        response_item['total_space_disc_file'] = round_abnt(
            response_item['total_space_disc_file'], self.PRECISION)
        response_item['percent_total_entities'] = round_abnt(
            response_item['percent_total_entities'], self.PRECISION)
        response_item['percent_total_space_disc_bank'] = round_abnt(
            response_item['percent_total_space_disc_bank'], self.PRECISION)
        response_item['percent_total_process'] = round_abnt(
            response_item['percent_total_process'], self.PRECISION)
        response_item['percent_total_access_db'] = round_abnt(
            response_item['percent_total_access_db'], self.PRECISION)
        response_item['percent_total_space_disc_file'] = round_abnt(
            response_item['percent_total_space_disc_file'], self.PRECISION)
        response_item['usage'] = round_abnt(
            response_item['usage'], self.PRECISION)
        response_item['cost_servidor'] = round_abnt(
            response_item['cost_servidor'], self.PRECISION)
        response_item['cost_operacional'] = round_abnt(
            response_item['cost_operacional'], self.PRECISION)
        response_item['cost_administrativo'] = round_abnt(
            response_item['cost_administrativo'], self.PRECISION)
        response_item['cost'] = (
            response_item['cost_servidor'] +
            response_item['cost_operacional'] +
            response_item['cost_administrativo']
        )
        response_item['cost'] = round_abnt(
            response_item['cost'], self.PRECISION)

        return response_item

    def _normalize_values_grand_totals_dict(self, grand_totals_dict):
        grand_totals_dict['total_entities'] = round_abnt(
            grand_totals_dict['total_entities'], self.PRECISION)
        grand_totals_dict['total_space_disc_bank'] = round_abnt(
            grand_totals_dict['total_space_disc_bank'], self.PRECISION)
        grand_totals_dict['total_process'] = round_abnt(
            grand_totals_dict['total_process'], self.PRECISION)
        grand_totals_dict['total_acess_db'] = round_abnt(
            grand_totals_dict['total_acess_db'], self.PRECISION)
        grand_totals_dict['total_space_disc_file'] = round_abnt(
            grand_totals_dict['total_space_disc_file'], self.PRECISION)
        grand_totals_dict['cost_servidor'] = round_abnt(
            grand_totals_dict['cost_servidor'], self.PRECISION)
        grand_totals_dict['cost_operacional'] = round_abnt(
            grand_totals_dict['cost_operacional'], self.PRECISION)
        grand_totals_dict['cost_administrativo'] = round_abnt(
            grand_totals_dict['cost_administrativo'], self.PRECISION)

        return grand_totals_dict

    def fill_in_percentages(self, response, grand_totals_dict):
        total_entities = grand_totals_dict['total_entities']
        total_space_disc_bank = grand_totals_dict['total_space_disc_bank']
        total_process = grand_totals_dict['total_process']
        total_acess_db = grand_totals_dict['total_acess_db']
        total_space_disc_file = grand_totals_dict['total_space_disc_file']
        if total_space_disc_file == 0:
            total_space_disc_file = 1

        for i in range(0, len(response)):
            response[i]['percent_total_entities'] = (
                response[i]['total_entities'] / total_entities)
            response[i]['percent_total_space_disc_bank'] = (
                response[i]['total_space_disc_bank'] / total_space_disc_bank)
            response[i]['percent_total_process'] = (
                response[i]['total_process'] / total_process)
            response[i]['percent_total_access_db'] = (
                response[i]['total_acess_db'] / total_acess_db)
            response[i]['percent_total_space_disc_file'] = (
                response[i]['total_space_disc_file'] / total_space_disc_file)

            response[i]['usage'] = self._calculate_usage(
                response[i]['percent_total_entities'],
                response[i]['percent_total_space_disc_bank'],
                response[i]['percent_total_process'],
                response[i]['percent_total_access_db'],
                response[i]['percent_total_space_disc_file']
            )
            usage = response[i]['usage']
            response[i]['cost_servidor'] = self._calculate_cost_individual(
                usage, self.cost_servidor)
            response[i]['cost_operacional'] = self._calculate_cost_individual(
                usage, self.cost_operacional)
            response[i]['cost_administrativo'] = self\
                ._calculate_cost_individual(usage, self.cost_administrativo)
            response[i]['cost'] = self._calculate_cost(response[i]['usage'])
            response[i] = self._normalize_values_response(response[i])

        return response

    def _valid_weights(self):
        total = (self.p_storage_bank + self.p_storage_file +  # noqa
                 self.p_process + self.p_access_db)
        if total > 1:
            raise exception.BadRequest(
                'the sum of the general weights must total 100%')

    def _get_cost_db(self, session, cost_name):
        return self.manager.api.project_costs().\
            get_cost_by_name_most_recent(
                session=session, name=cost_name, active=True)

    def _get_costs_params(self, **kwargs):
        session = kwargs.get('session', None)
        self.cost_servidor = kwargs.pop(
            'cost_servidor',
            self._get_cost_db(session, 'servidor'))
        self.cost_operacional = kwargs.pop(
            'cost_operacional',
            self._get_cost_db(session, 'operacional'))
        self.cost_administrativo = kwargs.pop(
            'cost_administrativo',
            self._get_cost_db(session, 'administrativo'))

        if self.cost_servidor is None:
            self.cost_servidor = 0
        if self.cost_operacional is None:
            self.cost_operacional = 0
        if self.cost_administrativo is None:
            self.cost_administrativo = 0

    def pre(self, **kwargs):
        self.de = kwargs.get('de', '2020-01-01-0300')
        self.ate = kwargs.get('ate', '9020-01-01-0300')
        self.domain_name = kwargs.get('domain_name', None)

        session = kwargs.get('session', None)

        self.p_storage_bank = float(kwargs.get('p_storage_bank', 0.1))
        self.p_storage_file = float(kwargs.get('p_storage_file', 0.1))
        self.p_process = float(kwargs.get('p_process', 0.3))
        self.p_access_db = float(kwargs.get('p_access_db', 0.5))

        self._valid_weights()

        precision = kwargs.get('precision', None)
        if precision is not None:
            try:
                self.PRECISION = int(precision)
            except Exception:
                raise exception.BadRequest(
                    'the precision parameter must be an integer')

        self.totals_db = self._get_totals_db(session)
        self.disk_space_totals_by_db_dict = self._get_disk_space_totals_by_db(
            session)
        self._get_constant_for_calculation()
        self.totals_by_domain = self._get_totals_by_domain(session)

        self._get_costs_params(**kwargs)
        return True

    def do(self, session, **kwargs):
        self._apply_calculations()

        response, grand_totals_dict = self._group_by_domain()
        response = self.fill_in_percentages(response, grand_totals_dict)

        grand_totals_dict['cost_servidor'] = self.cost_servidor
        grand_totals_dict['cost_operacional'] = self.cost_operacional
        grand_totals_dict['cost_administrativo'] = self.cost_administrativo
        grand_totals_dict['p_storage_bank'] = self.p_storage_bank
        grand_totals_dict['p_storage_file'] = self.p_storage_file
        grand_totals_dict['p_process'] = self.p_process
        grand_totals_dict['p_access_db'] = self.p_access_db
        grand_totals_dict = self._normalize_values_grand_totals_dict(
            grand_totals_dict)
        return (response, grand_totals_dict)


class GetRoles(operation.Operation):

    def pre(self, session, id, **kwargs):
        self.entity = self.driver.get(id, session=session)
        return self.entity is not None

    def do(self, session, **kwargs):
        roles = session.query(Role). \
            join(Policy). \
            join(Capability). \
            join(Application). \
            filter(and_(Capability.application_id == self.entity.application_id,
                        Role.name != Role.USER)). \
            distinct().all()

        roles_module = session.query(Role). \
            join(PolicyModule, Role.id == PolicyModule.role_id). \
            join(CapabilityModule,
                 CapabilityModule.id == PolicyModule.capability_module_id). \
            filter(and_(CapabilityModule.application_id ==
                        self.entity.application_id,
                        Role.name != Role.USER)). \
            distinct().all()

        roles_functionality = session.query(Role). \
            join(PolicyFunctionality,
                 Role.id == PolicyFunctionality.role_id). \
            join(CapabilityFunctionality,
                 CapabilityFunctionality.id ==
                 PolicyFunctionality.capability_functionality_id). \
            filter(and_(CapabilityFunctionality.application_id ==
                        self.entity.application_id,
                        Role.name != Role.USER)). \
            distinct().all()

        roles += roles_module
        roles += roles_functionality
        return set(roles)


class CheckPermission(operation.Get):

    def pre(self, session, id, url, method, **kwargs):
        self.id = id
        routes = self.manager.api.routes().list(
            url=url, method=method)

        if not routes:
            msg = 'Route not found'
            raise exception.BadRequest(msg)
        self.route = routes[0]

        if not self.route.active:
            msg = 'Route is inactive'
            raise exception.BadRequest(msg)

        return True

    def do(self, session, **kwargs):
        domain = super().do(session, **kwargs)
        if self.route.bypass:
            # return (has_permission, route)
            return (True, self.route)
        elif self.route.sysadmin and domain.name != 'default':
            return (False, self.route)

        has_capabilities = session.query(Domain.id). \
            join(Application). \
            join(Capability,
                 and_(Capability.application_id == Application.id,
                      Capability.route_id == self.route.id)). \
            filter(and_(Domain.id == self.id,
                        Domain.active, Application.active,
                        Capability.active)). \
            count()

        has_capability_functionalities = session.query(Domain.id). \
            join(Application). \
            join(CapabilityFunctionality). \
            join(FunctionalityRoute,
                 and_(FunctionalityRoute.functionality_id
                      == CapabilityFunctionality.functionality_id,
                      FunctionalityRoute.route_id == self.route.id)). \
            filter(and_(Domain.id == self.id,
                        Domain.active, Application.active,
                        CapabilityFunctionality.active,
                        FunctionalityRoute.active)). \
            count()

        has_capability_modules = session.query(Domain.id). \
            join(Application). \
            join(CapabilityModule). \
            join(ModuleFunctionality,
                 ModuleFunctionality.module_id
                 == CapabilityModule.module_id). \
            join(FunctionalityRoute,
                 and_(FunctionalityRoute.functionality_id
                      == ModuleFunctionality.functionality_id,
                      FunctionalityRoute.route_id == self.route.id)). \
            filter(and_(Domain.id == self.id,
                        Domain.active, Application.active,
                        ModuleFunctionality.active,
                        FunctionalityRoute.active)). \
            count()

        total = (has_capabilities + has_capability_functionalities +
                 has_capability_modules)
        hsa_permission = total > 0

        return (hsa_permission, self.route)


class List(operation.List):

    def do(self, session, **kwargs):
        Domain2 = aliased(Domain)

        query = session.query(Domain). \
            join(Application, Application.id == Domain.application_id). \
            join(Domain2, Domain2.id == Domain.parent_id, isouter=True)
        query = self.manager.apply_filters(query, Domain, **kwargs)

        dict_compare = {"application.": Application,
                        "parent.": Domain2}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        pagination = Pagination.get_pagination(Domain, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Domain)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return result


class Count(operation.Count):

    def do(self, session, **kwargs):
        Domain2 = aliased(Domain)

        query = session.query(Domain). \
            join(Application, Application.id == Domain.application_id). \
            join(Domain2, Domain2.id == Domain.parent_id, isouter=True)
        query = self.manager.apply_filters(query, Domain, **kwargs)

        dict_compare = {"application.": Application,
                        "parent.": Domain2}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        result = query.count()

        return result


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.domain_by_name = DomainByName(self)
        self.domain_logo_by_name = DomainLogoByName(self)
        self.upload_logo = UploadLogo(self)
        self.remove_logo = RemoveLogo(self)
        self.register = Register(self)
        self.activate = Activate(self)
        self.update_settings = UpdateSettings(self)
        self.remove_settings = RemoveSettings(self)
        self.get_domain_settings_by_keys = GetDomainSettingsByKeys(self)
        self.send_email_activate_account = SendEmailActivateAccount(self)
        self.get_files_size = GetFilesSize(self)
        self.get_usage_info_by_domain = GetUsageInfoByDomain(self)
        self.get_roles = GetRoles(self)
        self.check_permission = CheckPermission(self)
        self.list = List(self)
        self.count = Count(self)
        self.consulta_cpf_cnpj = consulta_cpf_cnpj.ConsultaCpfCnpj(self)
