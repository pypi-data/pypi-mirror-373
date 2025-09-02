from typing import Optional
import uuid
import flask
import sqlalchemy

# TODO this import here is so strange
from datetime import datetime
from viggocore.common import exception
from viggocore.common.operation_after_post import \
    operation_after_post_registry
from viggocore.common.subsystem.driver import Driver
import os


class Operation(object):

    def _get_gerar_log(self, manager_gerar_log, operation_gerar_log):
        if operation_gerar_log is not None:
            return operation_gerar_log
        elif manager_gerar_log is not None:
            return manager_gerar_log
        else:
            project_gerar_log = os.getenv('GERAR_LOG', None)
            if project_gerar_log is not None:
                return project_gerar_log.upper() == 'TRUE'
            else:
                return False

    def __init__(self, manager, gerar_log=None):
        self.manager = manager
        self.driver: Optional[Driver] = (
            manager.driver if hasattr(manager, 'driver') else None)
        # flag usada para saber se gera log ou não
        self.gerar_log = self._get_gerar_log(manager.gerar_log, gerar_log)

    def _get_user(self):
        try:
            token_id = flask.request.headers.get('token')
            token = self.manager.api.tokens().get(id=token_id)
            user = self.manager.api.users().get(id=token.user_id)
        except Exception:
            user = None
        return user

    def pre(self, **kwargs):
        return True

    def do(self, **kwargs):
        return True

    def post(self):
        pass

    def __call__(self, **kwargs):
        session = kwargs.pop(
            'session', self.driver.transaction_manager.session)

        if not self.pre(session=session, **kwargs):
            raise exception.PreconditionFailed()

        try:
            self.driver.transaction_manager.begin()

            result = self.do(session, **kwargs)

            self.driver.transaction_manager.commit()

            self.post()

            key = (self.manager.__class__, self.__class__)
            fn_after_post = operation_after_post_registry.get(key, None)
            if fn_after_post is not None:
                fn_after_post(self)

        except sqlalchemy.exc.IntegrityError as e:
            self.driver.transaction_manager.rollback()
            msg_info = ''.join(e.args)
            raise exception.DuplicatedEntity(msg_info)
        except Exception as e:
            self.driver.transaction_manager.rollback()
            raise e
        return result


class Create(Operation):

    def pre(self, session, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4().hex
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.now()
        if 'created_by' not in kwargs:
            if flask.has_request_context():
                token_id = flask.request.headers.get('token')
                if token_id is not None:
                    self.token = self.manager.api.tokens().get(id=token_id)
                    kwargs['created_by'] = self.token.user_id

        self.entity = self.driver.instantiate(**kwargs)

        return self.entity.is_stable()

    def do(self, session, **kwargs):
        self.driver.create(self.entity, session=session)
        return self.entity


class Get(Operation):

    def pre(self, session, id, **kwargs):
        self.id = id
        return True

    def do(self, session, **kwargs):
        entity = self.driver.get(self.id, session=session)
        return entity


class List(Operation):

    def _att_kwargs_with_query(self, session, **kwargs):
        if 'order_by' in kwargs.keys():
            order_by = kwargs.get('order_by', '')
            if '.' in order_by:
                kwargs['query'] = self.manager.init_query(
                    session, order_by, self.driver.resource)
        return kwargs

    def do(self, session, **kwargs):
        kwargs = self._att_kwargs_with_query(session=session, **kwargs)
        entities = self.driver.list(session=session, **kwargs)
        return entities


class Update(Operation):

    def _get_entity_new(self):
        return self.entity.to_dict()

    def _gerar_log(self, session, **kwargs):
        if self.gerar_log and not hasattr(self, 'entity_old'):
            raise exception.BadRequest(
                'A flag de gerar_log está marcada, mas não foi ' +
                'preenchido o entity_old.')

        # se a flag tiver marcada e o user do token for encontrado
        if self.gerar_log and self.user:
            if not hasattr(self, 'entity_new'):
                self.entity_new = self._get_entity_new()

            # cria o log da alteração de ativacao ou inativacao
            self.manager.api.log_systems().criar_log_system(
                session=session,
                entity=self.entity,
                user=self.user,
                json_anterior=self.entity_old,
                json_posterior=self.entity_new,
                **kwargs)

    def pre(self, session, id, **kwargs):
        if id is None:
            raise exception.BadRequest

        self.entity = self.driver.get(id, session=session)

        # preenche a variável entity_old para gerar o log antes de
        # fazer qualquer alteração na entidade
        if self.gerar_log:
            self.entity_old = self.entity.to_dict()

        self.entity.updated_at = datetime.now()
        self.user = None
        if 'updated_by' not in kwargs:
            if flask.has_request_context():
                token_id = flask.request.headers.get('token')
                if token_id is not None:
                    self.token = self.manager.api.tokens().get(id=token_id)
                    self.entity.updated_by = self.token.user_id
                    if self.gerar_log:
                        self.user = self.manager.api.users().get(
                            id=self.token.user_id)

        return self.entity.is_stable()

    def do(self, session, **kwargs):
        self.driver.update(self.entity, kwargs, session=session)
        self._gerar_log(session, **kwargs)
        return self.entity


class Delete(Operation):

    def _gerar_log(self, session, **kwargs):
        if self.gerar_log and not hasattr(self, 'entity_old'):
            raise exception.BadRequest(
                'A flag de gerar_log está marcada, mas não foi ' +
                'preenchido o entity_old.')

        # se a flag tiver marcada e o user do token for encontrado
        if self.gerar_log and self.user:
            # cria o log da alteração de ativacao ou inativacao
            self.manager.api.log_systems().criar_log_system(
                session=session,
                entity=self.entity,
                user=self.user,
                json_anterior=self.entity_old,
                json_posterior={},
                **kwargs)

    def pre(self, session, id, **kwargs):
        self.entity = self.driver.get(id, session=session)

        self.user = self._get_user()

        # preenche a variável entity_old para gerar o log antes de
        # fazer qualquer alteração na entidade
        if self.gerar_log:
            self.entity_old = self.entity.to_dict()

        return True

    def do(self, session, **kwargs):
        self._gerar_log(session, **kwargs)
        self.driver.delete(self.entity, session=session)


class Count(Operation):

    def do(self, session, **kwargs):
        rows = self.driver.count(session=session, **kwargs)
        return rows


class ListMultipleSelection(Operation):

    def do(self, session, **kwargs):
        entities = self.driver.list_multiple_selection(
            session=session, **kwargs)
        return entities


class ActivateOrDeactivateMultipleEntities(Operation):

    def pre(self, session, **kwargs):
        domain_id = kwargs.get('domain_id', None)
        if domain_id is None:
            raise exception.BadRequest('domain_id is required.')

        active = kwargs.get('active', None)
        if active is None:
            raise exception.PreconditionFailed('active is required.')

        multiple_selection = kwargs.get('multiple_selection', None)
        if multiple_selection is None:
            raise exception.PreconditionFailed(
                'multiple_selection is required.')

        self.user = self._get_user()

        return True

    def do(self, session, **kwargs):
        # atualiza o updated_at e o updated_by
        kwargs['updated_at'] = datetime.now()
        if self.user is not None:
            kwargs['updated_by'] = self.user.id

        result = self.driver.activate_or_deactivate_multiple_entities(
            session=session, **kwargs)

        # se a flag tiver marcada e o user do token for encontrado
        if self.gerar_log and self.user:
            # cria o log da alteração de ativacao ou inativacao
            self.manager.api.log_systems().criar_log_system_ativacao(
                session=session, result=result, user=self.user,
                **kwargs)

        return result
