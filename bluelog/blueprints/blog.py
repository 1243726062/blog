# -*- coding: utf-8 -*-
"""
    Created by 亥虫 on 2019/5/2
"""

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user

from bluelog.emails import send_new_reply_email, send_new_comment_email
from bluelog.models import Post, Comment, Category
from bluelog.forms import PostForm, CommentForm, AdminCommentForm
from bluelog.utils import redirect_back
from bluelog.extensions import db

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=per_page)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, reviewed=reviewed, post=post
        )
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:  # send message based on authentication status
            flash('评论提交成功', 'success')
        else:
            flash('谢谢, 评论将在审核后显示', 'info')
            send_new_comment_email(post)  # send notification email to admin
        return redirect(url_for('.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, form=form, comments=comments, pagination=pagination)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    """
    这里的分页查询语句和以往稍稍有些不同，不过并不难理解。我们
    需要获取对应分类下的所有文章，如果我们直接调用category.posts，会
    以列表的形式返回该分类下的所有文章对象，但是我们需要对这些文章
    记录附加其他查询过滤器和方法，所以不能使用这个方法。在上面的查
    询中，我们仍然从post模型出发，使用with_parent（）查询方法传入分
    类对象，最终筛选出属于该分类的所有文章记录。因为调用
    with_parent（）查询方法会返回查询对象，所以我们可以继续附加其他
    查询方法来过滤文章记录。
    :param category_id:
    :return:
    """
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, posts=posts, pagination=pagination)


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('禁止评论', 'warning')
        return redirect_back(url_for('blog.show_post', post_id=comment.post_id))
    return redirect(url_for('blog.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')

