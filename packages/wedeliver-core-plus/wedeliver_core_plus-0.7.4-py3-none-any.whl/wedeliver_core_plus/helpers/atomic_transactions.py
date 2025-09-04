from wedeliver_core_plus import WedeliverCorePlus


class Transactions(object):
    savepoint = None
    db = None

    def __init__(self):
        app = WedeliverCorePlus.get_app()

        self.db = app.extensions['sqlalchemy'].db
        self.savepoint = self.db.session.begin_nested()

    @staticmethod
    def atomic():
        return Transactions()

    def __enter__(self):
        return self

    def __exit__(self, a, error, traceback):
        if error:
            if self.savepoint.is_active:
                self.savepoint.rollback()

            self.db.session.rollback()
            raise error

        self.db.session.commit()

    def commit(self, instance):
        self.db.session.add(instance)
        if not self.savepoint.is_active:
            self.savepoint = self.db.session.begin_nested()

        self.savepoint.commit()
