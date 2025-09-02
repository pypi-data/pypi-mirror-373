from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Adicionar routes',
                'method': 'PUT',
                'url': self.resource_url + '/add_routes',
                'callback': 'add_routes'
            },
            {
                'action': 'Remove routes',
                'method': 'PUT',
                'url': self.resource_url + '/rm_routes',
                'callback': 'rm_routes'
            },
            {
                'action': 'Pega as rotas disponiveis',
                'method': 'GET',
                'url': self.resource_url + '/get_available_routes',
                'callback': 'get_available_routes'
            },
            {
                'action': 'Pega as rotas selecionadas',
                'method': 'GET',
                'url': self.resource_url + '/get_selected_routes',
                'callback': 'get_selected_routes'
            }
        ]
