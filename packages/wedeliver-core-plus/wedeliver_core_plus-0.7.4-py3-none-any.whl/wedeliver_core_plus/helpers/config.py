# -*- coding: utf-8 -*-

import os
import json

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session, sessionmaker
from wedeliver_core_plus import WedeliverCorePlus


class RoutingSession(Session):
    # Declare app and db as class attributes (they will be set only once)
    db = None
    app = None

    def get_bind(self, mapper=None, clause=None, **kwargs):
        if not self.app:
            self.app = WedeliverCorePlus.get_app()
            self.db = self.app.extensions['sqlalchemy'].db
        # If the clause is a SELECT, route to the read replica.
        if clause is not None and clause.__visit_name__ == 'select':
            self.app.logger.debug("Call read-database-replica")
            return self.db.get_engine(bind='read')
        # Otherwise, default to the write engine.
        self.app.logger.debug("Call write-database")
        return self.db.get_engine()


class CustomSQLAlchemy(SQLAlchemy):
    def create_session(self, options):
        # Remove any 'class_' in options to avoid duplicates
        options.pop('class_', None)
        # Use your custom session class instead of the default SignallingSession
        return sessionmaker(class_=RoutingSession, **options)


class Config(object):
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_BINDS = None

    def init_database_config(self):
        def build_uri(server):
            return (
                f"{os.environ.get('DATABASE_ENGINE')}://"
                f"{os.environ.get('DATABASE_USERNAME')}:"
                f"{os.environ.get('DATABASE_PASSWORD')}@"
                f"{server}:"
                f"{os.environ.get('DATABASE_PORT', 3306)}/"
                f"{os.environ.get('DATABASE_NAME')}?charset=utf8"
            )

        primary_server = os.environ.get("DATABASE_SERVER")
        readonly_server = os.environ.get("DATABASE_READONLY")

        self.SQLALCHEMY_DATABASE_URI = build_uri(primary_server)
        self.SQLALCHEMY_BINDS = {
            "read": build_uri(readonly_server) if readonly_server else self.SQLALCHEMY_DATABASE_URI
        }

    def __init__(self):
        if not os.environ.get("DATABASE_ENGINE"):
            load_dotenv()

        self.init_database_config()

        for k, v in os.environ.items():

            if not k:
                continue

            env_val = os.environ.get(k).strip()
            # Convert Null and empty value to None
            env_val = None if env_val.upper() in ["NULL", ""] else env_val
            # Convert True and False value to Boolean
            env_val = (
                json.loads(env_val.lower())
                if env_val and env_val.upper() in ["TRUE", "FALSE"]
                else env_val
            )

            self.__dict__[k] = env_val
