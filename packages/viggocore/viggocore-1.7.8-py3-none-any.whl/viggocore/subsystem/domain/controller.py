import json

import flask

from viggocore.common import exception, utils
from viggocore.common.exception import BadRequest
from viggocore.common.subsystem import controller
from viggocore.subsystem.domain.functions.controller import (
    consulta_cpf_cnpj)
from viggocore.subsystem.image.resource import QualityImage
from datetime import datetime
import datetime as datetime2
from viggocore.common.subsystem import entity


class Controller(controller.Controller):

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def _get_name_in_args(self):
        name = flask.request.args.get('name', None)
        if not name:
            raise BadRequest()
        return name

    def domain_by_name(self):
        try:
            name = self._get_name_in_args()
            domain = self.manager.domain_by_name(domain_name=name)
            domain_dict = domain.to_dict()
            if 'settings' in domain_dict.keys():
                domain_dict.pop('settings')
            response = {self.resource_wrap: domain_dict}
            return flask.Response(response=json.dumps(response, default=str),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def domain_logo_by_name(self):
        try:
            kwargs = {}
            quality = flask.request.args.get('quality', None)
            kwargs['quality'] = \
                QualityImage[quality] if quality else QualityImage.med
            name = self._get_name_in_args()
            folder, filename = self.manager.domain_logo_by_name(
                domain_name=name, **kwargs)
            return flask.send_from_directory(folder, filename)
        except KeyError:
            return self.get_bad_request('Unknown Quality')
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def get_token_id(self):
        return flask.request.headers.get('token')

    def get_token(self, token_id):
        return self.manager.api.tokens().get(id=token_id)

    def get_domain(self, domain_id):
        return self.manager.api.domains().get(id=domain_id)

    def get_domain_id_from_token(self, token):
        user = self.manager.api.users().get(id=token.user_id)
        return user.domain_id

    def get_domain_id(self):
        token = self.get_token(self.get_token_id())
        domain_id = self.get_domain_id_from_token(token)
        return domain_id

    def upload_logo(self, id):
        try:
            token = flask.request.headers.get('token')
            file = flask.request.files.get('file', None)
            if not file:
                raise exception.BadRequest('ERROR! File not found in request.')

            image = self.manager.upload_logo(id=id, token=token, file=file)

            response = {'image': image.to_dict()}
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=201,
                              mimetype="application/json")

    def remove_logo(self, id):
        try:
            self.manager.remove_logo(id=id)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=None,
                              status=204,
                              mimetype="application/json")

    def register(self):
        try:
            data = flask.request.get_json()

            username = data.get('username', 'admin').lower()
            email = data.get('email', None)
            password = data.get('password', None)
            domain_name = data.get('domain_name', None)
            domain_display_name = data.get('domain_display_name', None)
            application_name = data.get('application_name', None)

            self.manager.register(
                username=username, email=email,
                password=password, domain_name=domain_name,
                domain_display_name=domain_display_name,
                application_name=application_name)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=None,
                              status=204,
                              mimetype="application/json")

    def activate(self, id1, id2):
        try:
            token_id = flask.request.headers.get('token')
            domain = self.manager.activate(
                token_id=token_id, domain_id=id1, user_admin_id=id2)

            response = {'domain': domain.to_dict()}
            return flask.Response(response=utils.to_json(response),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def update_settings(self, id):
        try:
            data = flask.request.get_json()

            settings = self.manager.update_settings(id=id, **data)
            response = {'settings': settings}

            return flask.Response(response=utils.to_json(response),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def _get_keys_from_args(self):
        keys = flask.request.args.get('keys')
        if not keys:
            raise exception.BadRequest(
                'ERRO! The keys parameter was not passed correctly')
        return list(filter(None, keys.split(',')))

    def remove_settings(self, id):
        try:
            keys = self._get_keys_from_args()
            kwargs = {'keys': keys}

            settings = self.manager.remove_settings(id=id, **kwargs)
            response = {'settings': settings}

            return flask.Response(response=utils.to_json(response),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def get_domain_settings_by_keys(self, id):
        try:
            keys = self._get_keys_from_args()
            kwargs = {'keys': keys}

            settings = self.manager.get_domain_settings_by_keys(
                id=id, **kwargs)
            response = {'id': id, 'settings': settings}

            return flask.Response(response=utils.to_json(response),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def send_email_activate_account(self):
        try:
            data = flask.request.get_json()

            self.manager.send_email_activate_account(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=None,
                              status=204,
                              mimetype="application/json")

    def get_domain_settings_by_publicas(self, id):
        try:
            kwargs = {'keys': ['public']}

            settings = self.manager.get_domain_settings_by_keys(
                id=id, **kwargs)
            response = {'id': id, 'settings': settings}

            return flask.Response(response=utils.to_json(response),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    def get_files_size(self, id):
        try:
            files_size = self.manager.get_files_size(id=id)
            response = {'id': id, 'sizes': files_size}

            return flask.Response(response=utils.to_json(response),
                                  status=200,
                                  mimetype="application/json")
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

    # return start and end
    def _get_page_and_page_size(self, page, page_size):
        if page < 0:
            raise exception.BadRequest(
                'the page parameter must be greater than -1')
        if page_size < 1:
            raise exception.BadRequest(
                'the page_size parameter must be greater than 0')

        if page == 0:
            return (page, page_size)
        else:
            start = page * page_size
            end = start + page_size
            return (start, end)

    def _convert_de_ate(self, **kwargs):
        de = kwargs.pop('de', '2020-01-01-0300')
        ate = kwargs.pop('ate', '9020-01-01-0300')

        if de and ate:
            try:
                inicio = datetime.strptime(de.replace(' ', '+'), '%Y-%m-%d%z')
                fim = datetime.strptime(ate.replace(' ', '+'), '%Y-%m-%d%z') +\
                    datetime2.timedelta(days=1)

            except Exception:
                inicio = datetime.strptime(de, entity.DATE_FMT)
                fim = datetime.strptime(ate, entity.DATE_FMT) +\
                    datetime2.timedelta(days=1)
            kwargs['de'] = inicio
            kwargs['ate'] = fim

        return kwargs

    def get_usage_info_by_domain(self):
        filters = self._filters_parse()
        filters = self._filters_cleanup(filters)

        try:
            filters = self._parse_list_options(filters)
            filters = self._convert_de_ate(**filters)

            require_pagination = filters.pop('require_pagination', False)
            page = filters.pop('page', None)
            page_size = filters.pop('page_size', None)
            domain_name = filters.pop('domain_name', None)
            active = filters.pop('active', None)

            entities, totals = self.manager.get_usage_info_by_domain(**filters)

        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        if domain_name is not None:
            if '%' in domain_name:
                domain_name = domain_name.replace('%', '')
                entities = list(
                    filter(lambda x: domain_name in x['domain_name'],
                           entities))
            else:
                entities = list(
                    filter(lambda x: domain_name == x['domain_name'],
                           entities))

        if active is not None:
            entities = list(
                filter(lambda x: x['active'] == active, entities))

        entities = sorted(entities, key=lambda item: item['domain_name'])

        total = len(entities)

        if require_pagination and None not in [page, page_size]:
            page = int(page)
            page_size = int(page_size)

            start, end = self._get_page_and_page_size(page, page_size)

            response = {self.collection_wrap: entities[start:end],
                        'totals': totals}

            response.update({'pagination': {'page': page,
                                            'page_size': page_size,
                                            'total': total}})
        else:
            response = {self.collection_wrap: entities, 'totals': totals}

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def get_roles(self, id: str):
        try:
            roles = self.manager.get_roles(id=id)
            response = {"roles": [role.to_dict() for role in roles]}

        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def check_permission(self, id: str):
        filters = self._filters_parse()
        filters = self._filters_cleanup(filters)

        try:
            filters = self._parse_list_options(filters)
            url = filters.get('url', None)
            method = filters.get('method', None)
            if not url or not method:
                raise exception.BadRequest('url and method are required')

            has_permission, route = self.manager.check_permission(
                id=id, url=url, method=method)
            response = {
                "domain_id": id,
                "route": route.to_dict(),
                "has_permission": has_permission}

        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def list(self):
        filters = self._filters_parse()
        # filters = self._filters_cleanup(filters)

        try:
            filters = self._parse_list_options(filters)
            entities = self.manager.list(**filters)

            with_pagination = False
            require_pagination = filters.get('require_pagination', False)
            page = filters.get('page', None)
            page_size = filters.get('page_size', None)

            if (page and page_size is not None) and require_pagination is True:
                with_pagination = True
                count = self.manager.count(**(self._clean_filters(**filters)))
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)
        except ValueError:
            raise exception.BadRequest('page or page_size is invalid')

        collection = self._entities_to_dict(
            entities, self._get_include_dicts(filters))

        response = {self.collection_wrap: collection}

        if with_pagination:
            response.update({'pagination': {'page': int(page),
                                            'page_size': int(page_size),
                                            'total': count}})

        return flask.Response(response=utils.to_json(response),
                              status=200,
                              mimetype="application/json")

    def consulta_cpf_cnpj(self):
        return consulta_cpf_cnpj.consulta_cpf_cnpj(self)
