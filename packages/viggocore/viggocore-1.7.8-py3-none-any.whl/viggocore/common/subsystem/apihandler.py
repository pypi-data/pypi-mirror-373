from viggocore.common.input import RouteResource
from typing import Any, Callable, Dict, List

from viggocore.common.subsystem import Subsystem
from viggocore.common.subsystem.manager import Manager
from viggocore.common.subsystem.transaction_manager import TransactionManager


class Api(object):

    def __init__(self, managers: Dict[str, Callable[[], Manager]],
                 bootstrap_resources: List[Any],
                 transaction_manager: TransactionManager) -> None:
        self.__instances: Dict[str, Manager] = dict()
        self.__bootstrap_resources = bootstrap_resources
        self.__transaction_manager = transaction_manager

        for name, fn in managers.items():
            setattr(self, name, self.__get_instance(name, fn))

    def __get_instance(self, name: str,
                       fn: Callable[[TransactionManager], Manager]) -> Callable[[TransactionManager], Manager]:
        def wrapper():
            manager = self.__instances.get(name)

            if not manager:
                manager = fn(self.__transaction_manager)
                setattr(manager, 'api', self)
                setattr(manager,
                        'bootstrap_resources',
                        self.__bootstrap_resources)
                self.__instances[name] = manager

            return manager

        return wrapper

    @property
    def transaction_manager(self):
        return self.__transaction_manager


class ApiHandler(object):

    def __init__(self, subsystems: Dict[str, Subsystem],
                 bootstrap_resources: Dict[str, RouteResource]) -> None:
        self.__managers_dict = {name: s.lazy_manager
                                for name, s in subsystems.items()}
        self.__bootstrap_resources = self.__get_resources(bootstrap_resources)

    def api(self, transaction_manager: TransactionManager = None) -> Api:
        tm = transaction_manager if transaction_manager is not None \
            else TransactionManager()
        return Api(self.__managers_dict, self.__bootstrap_resources, tm)

    def __get_resources(self, bootstrap_resources):
        def resources():
            None

        for key, resource in bootstrap_resources.items():
            setattr(resources, key, resource)

        return resources
