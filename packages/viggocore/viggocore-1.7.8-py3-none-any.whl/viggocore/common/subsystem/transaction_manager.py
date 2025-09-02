from viggocore import database


class TransactionManager(object):

    def __init__(self, session=None) -> None:
        self.session = database.db.session
        self.count = 0

    def begin(self):
        self.count += 1

    def commit(self):
        self.count -= 1
        if self.count == 0:
            self.session.commit()

    def rollback(self):
        self.session.rollback()
        self.count = -1000000

    def shutdown(self):
        pass