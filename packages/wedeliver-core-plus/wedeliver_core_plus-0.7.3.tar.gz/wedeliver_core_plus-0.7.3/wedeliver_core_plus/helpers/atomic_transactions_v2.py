from wedeliver_core_plus import WedeliverCorePlus


class Transactions(object):
    """

    """
    session = None

    def __init__(self):
        app = WedeliverCorePlus.get_app()

        self.session = app.extensions['sqlalchemy'].db.session

    @staticmethod
    def atomic():
        """

        :return:
        """
        return Transactions()

    def commit(self, instance):
        """

        :param instance:
        """
        self.session.add(instance)
        self.session.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

# with Transaction.atomic() as session:
#     # Insert into table 1
#     session.add(Table1(...))
#     session.flush()
#
#     # Insert into table 2
#     session.add(Table2(...))
#     session.flush()
