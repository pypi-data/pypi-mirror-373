from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        settings_endpoint = '/settings'
        return super().routes + [
            {
                'action': 'getApplicationRoles',
                'method': 'GET',
                'url': self.resource_url + '/roles',
                'callback': 'get_roles'
            },
            {
                'action': 'Update settings on Application',
                'method': 'PUT',
                'url': self.resource_url + settings_endpoint,
                'callback': 'update_settings',
                'bypass': False
            },
            {
                'action': 'Remove settings from Application',
                'method': 'DELETE',
                'url': self.resource_url + settings_endpoint,
                'callback': 'remove_settings',
                'bypass': False
            },
            {
                'action': 'Get settings by keys from Application',
                'method': 'GET',
                'url': self.resource_url + settings_endpoint,
                'callback': 'get_application_settings_by_keys',
                'bypass': False
            },
            {
                'action': 'Exports application capabilities and policies',
                'method': 'POST',
                'url': self.resource_url + '/export_capabilities_and_policies',
                'callback': 'export_capabilities_and_policies',
                'bypass': False
            },
            {
                'action': 'Import application capabilities and policies',
                'method': 'POST',
                'url': self.resource_url + '/import_capabilities_and_policies',
                'callback': 'import_capabilities_and_policies',
                'bypass': False
            },
            {
                'action': ('Exports application capabilities and ' +
                           'policies in SQL'),
                'method': 'POST',
                'url': (self.resource_url +
                        '/export_capabilities_and_policies_sql'),
                'callback': 'export_capabilities_and_policies_sql',
                'bypass': False
            },
            {
                'action': 'Exports application capabilities and policies',
                'method': 'GET',
                'url': self.collection_url + '/xlsx_import_model',
                'callback': 'get_xlsx_import_model',
                'bypass': False
            },
        ]
