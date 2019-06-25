# -*- coding: utf-8 -*-
"""
    Created by 亥虫 on 2019/4/29
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog.models import Admin, Category, Post, Comment, Link
from bluelog.extensions import db

# 中文数据
fake = Faker('zh_CN')


def fake_admin():
    admin = Admin(
        username='haichong',
        blog_title='haichong',
        blog_sub_title='亥虫',
        name='陈春亥',
        about='南工渣渣春'
    )
    admin.set_password('123456')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)
    """
        分类的名称要求不能重复，如果随机生成的分类
        名和已创建的分类重名，就会导致数据库出错，抛出
        sqlalchemy.exc.IntegrityError异常。在这种情况下，我们可以使用try…
        except…语句来捕捉异常，在try子句中调用db.session.commit（）提交数
        据库会话，如果发生sqlalchemy.exc.IntegrityError异常，就调用
        db.session.rollback（）方法进行回滚操作。
    """
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            # 随机生成一句话
            title=fake.sentence(),
            # 随机生成一篇文章 2000字
            body=fake.text(2000),
            # 生成分类信息
            category=Category.query.get(random.randint(1, Category.query.count())),
            # 生成时间戳 datetime.datetime(2019, 3, 1, 9, 45, 16)
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
        db.session.commit()


def fake_comments(count=500):

    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员发表的评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            from_admin=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # 回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()