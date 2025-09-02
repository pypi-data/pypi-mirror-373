from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Adicionar functionalities',
                'method': 'PUT',
                'url': self.resource_url + '/add_functionalities',
                'callback': 'add_functionalities'
            },
            {
                'action': 'Remove functionalities',
                'method': 'PUT',
                'url': self.resource_url + '/rm_functionalities',
                'callback': 'rm_functionalities'
            },
            {
                'action': 'Pega as funcionalidades disponiveis',
                'method': 'GET',
                'url': self.resource_url + '/get_available_functionalities',
                'callback': 'get_available_functionalities'
            },
            {
                'action': 'Pega as funcionalidades selecionadas',
                'method': 'GET',
                'url': self.resource_url + '/get_selected_functionalities',
                'callback': 'get_selected_functionalities'
            }
        ]
