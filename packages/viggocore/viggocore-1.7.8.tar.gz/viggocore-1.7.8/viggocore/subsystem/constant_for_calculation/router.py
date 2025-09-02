from celery.app.utils import Settings
from viggocore.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'Get tables used in registering constants',
                'method': 'GET',
                'url': self.collection_url + '/get_table_names',
                'callback': 'get_table_names'
            }
        ]
