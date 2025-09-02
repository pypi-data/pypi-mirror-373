from celery.app.utils import Settings
from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        settings_endpoint = '/settings'
        return super().routes + [
            {
                'action': 'Get Domain By Name',
                'method': 'GET',
                'url': '/domainbyname',
                'callback': 'domain_by_name',
                'bypass': True
            },
            {
                'action': 'Get Domain Logo By Name',
                'method': 'GET',
                'url': '/domainlogobyname',
                'callback': 'domain_logo_by_name',
                'bypass': True
            },
            {
                'action': 'Upload logo to Domain',
                'method': 'PUT',
                'url': self.resource_url + '/logo',
                'callback': 'upload_logo'
            },
            {
                'action': 'Remove logo from Domain',
                'method': 'DELETE',
                'url': self.resource_url + '/logo',
                'callback': 'remove_logo'
            },
            {
                'action': 'Register new Domain',
                'method': 'POST',
                'url': self.collection_url + '/register',
                'callback': 'register',
                'bypass': True
            },
            {
                'action': 'Activate a register Domain',
                'method': 'PUT',
                'url': self.resource_enum_url + '/activate/<id2>',
                'callback': 'activate',
                'bypass': True
            },
            {
                'action': 'Update settings on Domain',
                'method': 'PUT',
                'url': self.resource_url + settings_endpoint,
                'callback': 'update_settings',
                'bypass': False
            },
            {
                'action': 'Remove settings from Domain',
                'method': 'DELETE',
                'url': self.resource_url + settings_endpoint,
                'callback': 'remove_settings',
                'bypass': False
            },
            {
                'action': 'Get settings by keys from Domain',
                'method': 'GET',
                'url': self.resource_url + settings_endpoint,
                'callback': 'get_domain_settings_by_keys',
                'bypass': False
            },
            {
                'action': 'Send email activate account',
                'method': 'POST',
                'url': self.collection_url + '/send_email_activate_account',
                'callback': 'send_email_activate_account',
                'bypass': True
            },
            {
                'action': 'Get settings by "publicas" from Domain',
                'method': 'GET',
                'url': self.resource_url + '/public_settings',
                'callback': 'get_domain_settings_by_publicas',
                'bypass': True
            },
            {
                'action': 'Get files size form Domain',
                'method': 'GET',
                'url': self.resource_url + '/files_size',
                'callback': 'get_files_size'
            },
            {
                'action': 'Get usage infos by Domain',
                'method': 'GET',
                'url': self.collection_url + '/get_usage_info_by_domain',
                'callback': 'get_usage_info_by_domain'
            },
            {
                'action': 'Lista papéis pesquisando por domínio',
                'method': 'GET',
                'url': self.resource_url + '/roles',
                'callback': 'get_roles'
            },
            {
                'action': 'Lista papéis pesquisando por domínio',
                'method': 'GET',
                'url': self.resource_url + '/check_permission',
                'callback': 'check_permission'
            },
            {
                'action': 'buscar CPF/CNPJ pela API',
                'method': 'GET',
                'url': self.collection_url + '/consulta_cpf_cnpj',
                'callback': 'consulta_cpf_cnpj'
            }
        ]
