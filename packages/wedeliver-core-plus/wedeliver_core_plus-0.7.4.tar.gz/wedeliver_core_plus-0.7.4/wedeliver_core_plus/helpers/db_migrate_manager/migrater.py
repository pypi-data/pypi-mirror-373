import importlib
import os
import shutil

from alembic import command
from flask_migrate import Migrate, init


class MigrateManager:
    EXCLUDE_FILES = ["__init__.py"]
    models_directory = "model"
    directory = None
    app = None
    db = None
    producer = None

    def __init__(self, app, db, directory=None, producer=None):
        try:
            if directory:
                self.models_directory = directory

            Migrate(app, db, compare_type=True)
            self.directory = 'migrations'
            self.app = app
            self.db = db
            self.producer = producer

            app.logger.info("start..")
            for dir_path, dir_names, file_names in os.walk(self.models_directory):
                for file_name in file_names:
                    if file_name.endswith("py") and not file_name in self.EXCLUDE_FILES:
                        file_path_wo_ext, _ = os.path.splitext((os.path.join(dir_path, file_name)))
                        app.logger.debug(file_path_wo_ext)
                        module_name = file_path_wo_ext.replace(os.sep, ".")
                        importlib.import_module(module_name)
        except Exception as e:
            try:
                self.sent_notification(text='<!channel> {}'.format(str(e)), is_error=True)
            except Exception as x:
                raise x
            raise e

    def sent_notification(self, text, is_error=False):
        service_name = self.app.config.get('SERVICE_NAME')
        env = self.app.config.get('FLASK_ENV')
        channel = 'eng-database-migration-alert-{}'.format(env)

        title = '({}) Service on ({}) Environment'.format(service_name.upper(), env.upper())
        payload = dict(
            channel=channel,
            username='Migrate Manager',
            title=title,
            text=text
        )
        if is_error:
            payload.update(
                color='#ff0000'
            )

        self.producer().send_topic('internal_notification_message', dict(
            notification_method='slack',
            payload=payload
        ))

    def run(self):
        try:
            with self.app.app_context():
                try:
                    shutil.rmtree(self.directory)
                except FileNotFoundError as e:
                    pass

                init(directory=self.directory)

                self.db.engine.execute("DROP TABLE alembic_version;")

                _migrate = self.app.extensions['migrate'].migrate

                migrate_result = command.revision(config=_migrate.get_config(
                    self.directory, opts=['autogenerate']
                ), message='auto-migration', autogenerate=True)

                # migrate(directory=directory)

                # upgrade(directory=self.directory)

                command.upgrade(config=_migrate.get_config(
                    self.directory, x_arg=None
                ), revision='head', sql=False, tag=None)

                if self.producer and hasattr(migrate_result, 'log_entry'):
                    text = migrate_result.log_entry
                    self.sent_notification(text=text)

        except Exception as e:
            self.sent_notification(text='<!channel> {}'.format(str(e)), is_error=True)
            raise e
