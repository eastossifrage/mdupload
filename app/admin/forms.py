# -*- coding:utf-8 -*-
__author__ = u'东方鹗'


from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User


class LoginForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(label=u'记住我', default=False)
    submit = SubmitField(u'登 录')


class RegisterForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 16, message=u'用户名长度要在1和16之间'),
                           Regexp(ur'^[\u4E00-\u9FFF]+$', flags=0, message=u'用户名必须为中文')])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo(u'password2', message=u'密码必须一致！')])
    password2 = PasswordField(u'重输密码', validators=[DataRequired()])
    submit = SubmitField(u'注 册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册！')


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo(u'password2', message=u'密码必须一致！')])
    password2 = PasswordField(u'重输密码', validators=[DataRequired()])
    submit = SubmitField(u'更新密码')


class PasswordResetRequestForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    submit = SubmitField(u'发送')


class PasswordResetForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(6, 64, message=u'邮件长度要在6和64之间'),
                        Email(message=u'邮件格式不正确！')])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo(u'password2', message=u'密码必须一致！')])
    password2 = PasswordField(u'重输密码', validators=[DataRequired()])
    submit = SubmitField(u'确认')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'邮箱未注册！')


class UploadForm(Form):
    markdown = RadioField(label=u'类型', choices=[(u'markdown', u'Markdown文件'), (u'picture', u'图片压缩包')],
                          default=u'markdown')
    submit = SubmitField(u'上 传')


class PathForm(Form):
    path = StringField(u'路径', validators=[DataRequired()])
    submit = SubmitField(u'确认')

