# -*- coding: utf-8 -*-
from flask import render_template, request, redirect
from userApp import *
from userApp.dbc import User
from flask_login import LoginManager, current_user, login_required, login_user, logout_user


login_manager = LoginManager()
login_manager.init_app(userApp)


@login_manager.user_loader
def load_user(user_id):
    newuser = User.User.query.get(int(user_id))
    if newuser:
        return newuser
    else:
        return None

@userApp.route('/login', methods=['GET'])
def login():
    if(current_user.is_authenticated):
        return redirect("/")
    else:
        return render_template('login.pug', encoding='utf-8')

@userApp.route('/login', methods=['POST'])
def login_post():
    username = request.form['login']
    password = request.form['loginpassword']
    user = User.User.query.filter_by(user_name=username).first()
    if user:
        if(user.password == password):
            login_user(user)
            return redirect("/")
        else:
            return render_template('login.pug', error = "Не удается войти. \
            Пожалуйста, проверьте правильность написания имени пользователя и пароля.")
    else:
        return render_template('login.pug', error="Не удается войти. \
            Пожалуйста, проверьте правильность написания имени пользователя и пароля.")

# somewhere to logout
@userApp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")