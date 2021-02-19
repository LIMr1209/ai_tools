# encoding: utf-8
import logging

from flask import Flask
import datetime
import os

# from loguru import logger

from app.helpers.exception import APIException, ServerError, framework_error
from app.helpers.interceptor import register_api

PROJDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
CONFDIR = os.path.join(PROJDIR, "config")


def create_app(config=None):
    app = Flask(__name__, static_url_path="/static", static_folder="../static")

    app.config.from_pyfile(os.path.join(CONFDIR, "app.py"))

    if isinstance(config, dict):
        app.config.update(config)
    elif config:
        app.config.from_pyfile(config)

    app.config.update({"SITE_TIME": datetime.datetime.utcnow()})

    # app.logger = logger

    from .views import api

    routers = [api]
    register_api(app, routers)

    app.register_error_handler(Exception, framework_error)
    return app
