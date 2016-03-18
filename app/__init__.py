# -*- coding:utf-8 -*-
__author__ = u'东方鹗'


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login'


def create_app(config_name):
    """ 使用工厂函数初始化程序实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app=app)

    db.init_app(app=app)
    login_manager.init_app(app=app)

    # 注册蓝本 main
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app