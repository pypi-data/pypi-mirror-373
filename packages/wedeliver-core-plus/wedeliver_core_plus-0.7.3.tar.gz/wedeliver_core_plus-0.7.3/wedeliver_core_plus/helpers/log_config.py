# -*- coding: utf-8 -*-

import sys
import logging
from dotenv import load_dotenv

load_dotenv()


class AppLogger:
    stream = None
    level = None

    def __init__(self, level, stream=None):
        self.stream = stream or sys.stdout
        self.level = level

    def get_logger(self):
        handler = logging.StreamHandler(self.stream)
        handler.setLevel(self.level)
        handler.addFilter(LevelFilter(self.level))
        formatter = logging.Formatter(
            "(%(levelname)s) %(name)s in %(module)s@%(lineno)s: %(message)s"
        )

        handler.setFormatter(formatter)

        return handler


class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


handler_list = [
    AppLogger(level=logging.CRITICAL, stream=sys.stderr).get_logger(),
    AppLogger(level=logging.ERROR, stream=sys.stderr).get_logger(),
    AppLogger(level=logging.WARNING).get_logger(),
    AppLogger(level=logging.INFO).get_logger(),
]


def init_logger(app):
    if app.config.get("DEBUG"):
        handler_list.append(AppLogger(level=logging.DEBUG).get_logger())

    packages_loggers = [
        dict(app=logging.getLogger(), start_level=logging.DEBUG),  # root
        dict(app=app.logger, start_level=logging.DEBUG),  # flask
        dict(
            app=logging.getLogger("werkzeug"),  # webserver
            start_level=logging.DEBUG
            if "production" not in app.config.get("FLASK_ENV")
            else logging.WARNING,
        ),
    ]
    for package_logger in packages_loggers:
        logger = package_logger.get("app")
        start_level = package_logger.get("start_level")
        logger.setLevel(start_level)  # start listen form debug level
        logger.propagate = False
        for handler in logger.handlers:
            logger.removeHandler(handler)

        for handler in handler_list:
            logger.addHandler(handler)
