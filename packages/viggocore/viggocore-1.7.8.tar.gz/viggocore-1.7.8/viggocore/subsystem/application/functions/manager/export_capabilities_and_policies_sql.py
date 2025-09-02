from viggocore.common import exception
from viggocore.common import utils as core_utils
from viggocore.subsystem.capability.resource import Capability
from viggocore.subsystem.role.resource import Role
from viggocore.subsystem.route.resource import Route
from viggocore.subsystem.policy.resource import Policy
from sqlalchemy import func, or_
from viggocore.common.subsystem import operation
from viggocore.subsystem.application.functions.template import (
    insert_capabilities_sql as ic)
from viggocore.subsystem.application.functions.template import (
    insert_policies_sql as ip)
from datetime import datetime as datetime1


class ExportCapabilitiesAndPoliciesSql(operation.List):

    def _montar_sql_capabilities(self, capabilities):
        url_methods = ''
        for c in capabilities:
            url_methods += ic.QUERY_FILTER.format(url=c[0], method=c[1])

        return ic.QUERY.format(
            application_name=self.application_name,
            url_methods=url_methods)

    def _montar_sql_policies(self, policies):
        sql_policies = ''
        roles = list(set([p[0] for p in policies]))
        for role in roles:
            url_methods = ''
            policies_filtred = list(filter(lambda x: x[0] == role, policies))
            for policy in policies_filtred:
                url_methods += ip.QUERY_FILTER.format(
                    url=policy[1], method=policy[2])

            sql_policies += ip.QUERY.format(
                role_name=role,
                application_name=self.application_name,
                url_methods=url_methods)

        return sql_policies

    def _montar_sql(self, capabilities, policies):
        conteudo_sql = ''
        conteudo_sql += self._montar_sql_capabilities(capabilities)
        conteudo_sql += self._montar_sql_policies(policies)
        return conteudo_sql

    # função para pegar o nome do arquivo
    def _get_file_name(self, **kwargs):
        application = self.manager.get(id=self.id)
        self.application_name = application.name

        file_name = kwargs.get('file_name', None)
        if file_name is not None:
            return file_name
        else:
            file_name = f'{self.application_name}-{self.a_partir}.sql'
            return file_name

    # valida se o tipo de exportacao passado é válido
    def _validar_tipo_exportacao(self):
        tipos_permitidos = ['CAPACIDADE', 'POLITICA']
        if any(list(map(
                lambda x: x not in tipos_permitidos, self.tipo_exportacao))):
            raise exception.BadRequest(
                'Os tipos de exportação permitidos são:' +
                ', '.join(tipos_permitidos) + '.')

    # funções de buscar dados
    def _get_capabilities(self, session):
        query = session.query(Route.url, Route.method)\
            .join(Capability, Capability.route_id == Route.id)\
            .filter(Capability.application_id == self.id)\
            .filter(or_(Route.created_at >= self.a_partir,
                        Route.created_at.is_(None)))\
            .order_by(Route.url, Route.method)
        result = query.all()
        return result

    def _get_policies(self, session):
        papeis = [p.upper() for p in self.papeis]
        query = session.query(Role.name, Route.url, Route.method)\
            .join(Policy, Policy.role_id == Role.id)\
            .join(Capability, Capability.id == Policy.capability_id)\
            .join(Route, Route.id == Capability.route_id)\
            .filter(func.upper(Role.name).in_(papeis))\
            .filter(Capability.application_id == self.id)\
            .filter(or_(Route.created_at >= self.a_partir,
                        Route.created_at.is_(None)))\
            .order_by(Role.name, Route.url, Route.method)
        result = query.all()
        return result

    def _get_capabilities_and_policies(self, session):
        # inicia as listas de capacidades e políticas
        capabilities = []
        policies = []

        # se foi passada a CAPACIDADE como tipo_exportacao então vai buscar as
        # capacidades
        if 'CAPACIDADE' in self.tipo_exportacao:
            capabilities = self._get_capabilities(session=session)

        # se foi passada a POLITICA como tipo_exportacao então vai buscar as
        # políticas ligadas as capacidades desta aplicação
        if 'POLITICA' in self.tipo_exportacao:
            policies = self._get_policies(session=session)

        return (capabilities, policies)

    def pre(self, id, **kwargs):
        self.id = id
        if self.id is None:
            raise exception.BadRequest(
                'É obrigatório passar o id na rota da requisição.')

        self.tipo_exportacao = kwargs.pop('tipo_exportacao', [])
        if not self.tipo_exportacao:
            raise exception.BadRequest(
                'É obrigatório informar o tipo_exportacao.')

        self._validar_tipo_exportacao()

        self.papeis = kwargs.pop('papeis', [])
        if 'POLITICA' in self.tipo_exportacao and not self.papeis:
            raise exception.BadRequest(
                'É obrigatório informar os papéis caso você ' +
                'queira exportar as políticas também.')

        self.a_partir = kwargs.pop('a_partir', None)
        if self.a_partir is None:
            raise exception.BadRequest(
                'É obrigatório informar o campo "a_partir" para filtrar ' +
                'as informações que foram geradas posterior a esta data.')
        else:
            try:
                self.a_partir = datetime1.strptime(
                    self.a_partir.replace(' ', '+'), '%Y-%m-%d%z')
            except Exception:
                raise exception.BadRequest(
                    'É obrigatório passar a data no formato "yyyy-mm-dd-tz."')

        return True

    def do(self, session, **kwargs):
        capabilities, policies = self._get_capabilities_and_policies(
            session=session)

        if len(capabilities) == 0 and len(policies) == 0:
            raise exception.BadRequest(
                'Não existe dados para essa filtragem.')

        self.file_name = self._get_file_name(**kwargs)
        self.download_folder = core_utils.get_upload_folder()
        path = self.download_folder + '/' + self.file_name

        conteudo_sql = self._montar_sql(capabilities, policies)

        # salva o arquivo sql
        with open(path, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo_sql)

        return self.download_folder, self.file_name
