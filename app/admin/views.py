# -*- coding:utf-8 -*-
__author__ = u'东方鹗'

from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from app.models import User, Path
from .forms import LoginForm, RegisterForm, ChangePasswordForm, UploadForm, PathForm
from . import admin
from .. import db
from werkzeug.utils import secure_filename
import os
import stat
import zipfile


def allowed_file(filename, filetype):
    return '.' in filename and filename.rsplit('.', 1)[1] == filetype


@admin.route('/', methods=['GET', 'POST'])
@login_required
def index():
    upload_form = UploadForm(prefix='upload')
    if upload_form.validate_on_submit():
        path = Path.query.get(1)
        if path:
            this_file = request.files['file']
            if upload_form.markdown.data == u'markdown':
                if allowed_file(filename=this_file.filename, filetype='md'):
                    filename = secure_filename(this_file.filename)
                    this_file.save(os.path.join('%s/blog' % path.markdown, filename))
                    os.chmod(os.path.join('%s/blog' % path.markdown, filename), stat.S_IRWXU)
                    flash({'success': u'上传Markdown文件成功！'})
                else:
                    flash({'error': u'只支持后缀为md的文件！'})
            elif upload_form.markdown.data == u'picture':
                if allowed_file(filename=this_file.filename, filetype='zip'):
                    filename = secure_filename(this_file.filename)
                    this_file.save(os.path.join('%s/blog' % path.markdown, 'img/%s' % filename))
                    zip_file = os.path.join('%s/blog' % path.markdown, 'img/%s' % filename)
                    file_dir = os.path.join('%s/blog' % path.markdown, 'img/')
                    z = zipfile.is_zipfile(zip_file)
                    if z:
                        fz = zipfile.ZipFile(zip_file, 'r')
                        for f in fz.namelist():
                            fz.extract(f, file_dir)
                        flash({'success': u'压缩包上传并解压成功！'})
                    else:
                        flash({'error': u'该压缩包不是真正的zip格式！'})
                else:
                    flash({'error': u'只支持zip的的压缩包！'})
            else:
                flash({'error': u'未知错误！'})
        else:
            return redirect(url_for('.set_path'))

    return render_template('admin/index.html', uploadForm=upload_form)


@admin.route('/clear_cache', methods=['GET', 'POST'])
@login_required
def clear_cache():
    path = Path.query.get(1)
    cache_path = os.path.join(path.markdown, 'app/cache')
    import shutil
    shutil.rmtree(cache_path)
    os.mkdir(cache_path)
    flash({'success': u'清除缓存成功！'})

    return redirect(url_for('.index'))


@admin.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(prefix='login')
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data.strip()).first()
        if user is not None and user.verify_password(login_form.password.data.strip()):
            login_user(user=user, remember=login_form.remember_me.data)
            return redirect(request.args.get('next') or url_for('.index'))
        elif user is None:
            flash({'error': u'邮箱未注册！'})
        elif not user.verify_password(login_form.password.data.strip()):
            flash({'error': u'密码不正确！'})
    return render_template('admin/login.html', loginForm=login_form)


@admin.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm(prefix='register')
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data.strip(),
                    username=register_form.username.data.strip(),
                    password=register_form.password.data.strip())
        db.session.add(user)
        db.session.commit()
        login_user(user=user)
    return render_template('admin/register.html', registerForm=register_form)


@admin.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    change_password_form = ChangePasswordForm(prefix='change_password')
    if change_password_form.validate_on_submit():
        if current_user.verify_password(change_password_form.old_password.data.strip()):
            current_user.password = change_password_form.password.data.strip()
            flash({'success': u'您的账户密码已修改成功！'})
        else:
            flash({'error': u'无效的旧密码！'})

    return render_template('admin/change_password.html', changePasswordForm=change_password_form)


@admin.route('/set_path', methods=['GET', 'POST'])
@login_required
def set_path():
    path_form = PathForm(prefix='path')
    path = Path.query.get(1)
    if path_form.validate_on_submit():
        if path:
            path.markdown = path_form.path.data.strip()
            flash({'success': u'上传路径修改成功！'})
        else:
            new_path = Path(markdown=path_form.path.data.strip())
            db.session.add(new_path)
            flash({'success': u'上传路径设置成功！'})

    return render_template('admin/path.html', path=path, pathForm=path_form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))
