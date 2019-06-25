# -*- coding: utf-8 -*-
"""
    Created by 亥虫 on 2019/4/29
"""
import os

from flask import Flask
from flask_login import current_user

from bluelog.settings import config
from bluelog.extensions import db, bootstrap, login_manager, moment, mail, csrf, ckeditor
from bluelog.commands import register_commands
from bluelog.blueprints.blog import blog_bp
from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.models import Admin, Category, Link, Comment


"""
app = Flask('bluelog')   创建 app
app.config.from_object(config[config_name])   加载一些默认配置
register_commands(app)   注册命令，用来生成数据库，生成管理员，文章，分类，链接的数据
register_extensions(app)   注册插件，用来加载数据库、bootstrap、以及富文本编辑器的扩展
register_blueprints(app)    注册蓝图，博客分成3个模块，auth登录模块, blog博客模块, admin后台管理模块
register_template_context(app) 注册全局模板，在模板中使用全局设置
"""
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_commands(app)
    register_extensions(app)
    register_blueprints(app)
    register_template_context(app)

    return app


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin,
            categories=categories,
            links=links,
            unread_comments=unread_comments
        )


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
