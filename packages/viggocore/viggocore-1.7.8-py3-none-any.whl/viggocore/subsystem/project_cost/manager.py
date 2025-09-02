from viggocore.common.subsystem import operation
from viggocore.common import manager
from viggocore.subsystem.project_cost.resource import ProjectCost
from viggocore.common.subsystem.pagination import Pagination


class List(operation.List):

    def do(self, session, **kwargs):
        query = session.query(ProjectCost)
        query = self.manager.apply_filters(
            query, ProjectCost, **kwargs)

        query = self.manager.apply_filter_de_ate_with_timezone(
            ProjectCost, query, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(
            ProjectCost, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(ProjectCost)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class GetCostByNameMostRecent(operation.List):

    def do(self, session, **kwargs):
        kwargs['order_by'] = 'created_at desc'
        costs = super().do(session, **kwargs)
        if len(costs) > 0:
            return costs[0].cost
        return None


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.list = List(self)
        self.get_cost_by_name_most_recent = GetCostByNameMostRecent(self)
