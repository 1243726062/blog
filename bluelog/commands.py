# -*- coding: utf-8 -*-
"""
    Created by 亥虫 on 2019/4/29
"""

import click

from bluelog.fakes import fake_links
from bluelog.models import Admin, Category
from bluelog.extensions import db


def register_commands(app):
    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')


    @app.cli.command()
    @click.option('--username', prompt=True, help='创建账号用于登录')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='创建密码用于登录')
    def init(username, password):

        click.echo('初始化数据库')
        # db.drop_all()
        # db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('这个账号已经存在, 更新中...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='小陈博客',
                blog_sub_title='分享快乐',
                name='HaiChong',
                about='南工渣渣春'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')


