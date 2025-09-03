from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.helpers.auth import Auth
from sqlalchemy import event


def init_base_model():
    app = WedeliverCorePlus.get_app()
    db = app.extensions['sqlalchemy'].db

    class BaseModel(db.Model):
        __abstract__ = True
        id = db.Column(db.Integer, primary_key=True)
        creation = db.Column(db.DateTime, default=db.func.now())
        created_by = db.Column(db.String(64), default=Auth.get_user_str)

        modification = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

        def __init__(self, *args, **kwargs):
            super(BaseModel, self).__init__(*args, **kwargs)
            self.register_hooks()

        # def __init__(self, created_by=None):
        #     self.created_by = created_by or Auth.get_user().get("email", "Guest")

        @classmethod
        def register_hooks(cls):
            @event.listens_for(cls, 'before_insert')
            def before_insert(mapper, connection, target):
                if hasattr(target, 'before_insert'):
                    target.before_insert(mapper, connection)

            @event.listens_for(cls, 'after_insert')
            def after_insert(mapper, connection, target):
                if hasattr(target, 'after_insert'):
                    target.after_insert(mapper, connection)

            @event.listens_for(cls, 'before_update')
            def before_update(mapper, connection, target):
                if hasattr(target, 'before_update'):
                    target.before_update(mapper, connection)

            @event.listens_for(cls, 'after_update')
            def after_update(mapper, connection, target):
                if hasattr(target, 'after_update'):
                    target.after_update(mapper, connection)

            @event.listens_for(cls, 'before_delete')
            def before_delete(mapper, connection, target):
                if hasattr(target, 'before_delete'):
                    target.before_delete(mapper, connection)

            @event.listens_for(cls, 'after_delete')
            def after_delete(mapper, connection, target):
                if hasattr(target, 'after_delete'):
                    target.after_delete(mapper, connection)

    return BaseModel
