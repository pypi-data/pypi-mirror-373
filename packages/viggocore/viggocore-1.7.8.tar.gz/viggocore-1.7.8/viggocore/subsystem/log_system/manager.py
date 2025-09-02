import flask
from viggocore.common import exception, manager, utils
from viggocore.subsystem.log_system.functions import (
    entity_create)


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = entity_create.Create(self)

    def _get_user_informado(self, domain_id, user_name):
        users = self.api.users().list(
            domain_id=domain_id, name=user_name)
        if len(users) == 1:
            return users[0]
        else:
            raise exception.BadRequest('Esse usuário não existe.')

    def valida_user(self, user=None, **kwargs):
        domain_id = kwargs.get('domain_id', None)
        if domain_id is None:
            raise exception.BadRequest('O domain_id é obrigatório.')
        user_name = kwargs.get('user_name', None)
        # valida se o usuário informado existe
        if user is None:
            user = self._get_user_informado(domain_id, user_name)

        # pega esta informação para preencher a tabela de
        # log_alteracao_custo_pedido
        self.user_id = user.id

        # valida se a senha informada bate com a senha do usuário encontrado
        password_informada = kwargs.get('user_password', 'None')
        if user.password != password_informada:
            raise exception.BadRequest('A senha informada está incorreta.')

    def _get_tag(self):
        return ' - '.join([flask.request.url, flask.request.method])

    def _get_domain_id(self, entity, user, domain_id=None):
        if type(entity) is list and len(entity) > 0:
            entity_aux = entity[0]
        else:
            entity_aux = entity

        domain_id = (
            domain_id if domain_id is not None else entity_aux.get_domain_id())
        if domain_id is None:
            """como o log só é gerado se encontrar o user do token,
            então podemos pegar o domain_id dele se a entidade em questão
            não tiver domain_id, ou não puder sobrescrever a função
            get_domain_id() para pegar o domain_id de uma entidade
            backref como o caso do token, que se colocarmos o backref
            de user nele, será possível dar include"""
            domain_id = user.domain_id
        return domain_id

    def _get_user_info(self, user):
        user_id = None
        user_name = None

        if user is not None:
            user_id = user.id
            user_name = user.name

        return (user_id, user_name)

    def _get_kwargs_info(self, user_name, **kwargs):
        """
        Essa função vai pegar as informações passadas pelo client na requisição
        """
        # se não for passado um "user_name" na requisição ai usará o
        # do usuário do token mesmo
        user_name = kwargs.get('user_name', user_name)
        user_password = kwargs.get('user_password', None)
        justificativa = kwargs.get('justificativa', None)

        return (user_name, user_password, justificativa)

    def criar_log_system_ativacao(self, session, result, user=None,
                                  domain_id=None, **kwargs):
        if len(result) > 0:
            tag = self._get_tag()
            entity = result[0]

            domain_id = self._get_domain_id(entity=entity, domain_id=domain_id,
                                            user=user)
            user_id, user_name = self._get_user_info(user=user)
            user_name, user_password, justificativa = (
                self._get_kwargs_info(user_name=user_name, **kwargs))

            entidade_ids = ','.join([r.id for r in result])
            json_posterior = {
                "active": entity.active
            }
            log_alteracao_dict = {
                "tag": tag,
                "domain_id": domain_id,
                "user_id": user_id,
                "user_name": user_name,
                "user_password": user_password,
                "justificativa": justificativa,
                "entidade_ids": entidade_ids,
                "entidade_nome": entity.individual(),
                "json_anterior": utils.to_json({}),
                "json_posterior": utils.to_json(json_posterior)
            }
            self.create(session=session, **log_alteracao_dict)

    def criar_log_system(self, session, entity, json_anterior,
                         json_posterior, user=None, domain_id=None, **kwargs):
        tag = self._get_tag()

        domain_id = self._get_domain_id(entity=entity, domain_id=domain_id,
                                        user=user)
        user_id, user_name = self._get_user_info(user=user)
        user_name, user_password, justificativa = (
            self._get_kwargs_info(user_name=user_name, **kwargs))

        log_alteracao_dict = {
            "tag": tag,
            "domain_id": domain_id,
            "user_id": user_id,
            "user_name": user_name,
            "user_password": user_password,
            "justificativa": justificativa,
            "entidade_ids": entity.id,
            "entidade_nome": entity.individual(),
            "json_anterior": utils.to_json(json_anterior),
            "json_posterior": utils.to_json(json_posterior)
        }
        self.create(session=session, **log_alteracao_dict)
