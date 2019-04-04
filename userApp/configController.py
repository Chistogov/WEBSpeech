# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for,request
from sqlalchemy import *
from userApp import *
from userApp.dbc import User, Journal, db, NameRec, Names, Config
from flask_login import login_required, current_user
import datetime, glob, os
import logging
import threading, time

@userApp.route('/config')
@login_required
def config():
    logging.info("config")
    config = db.session.query(Config.Config).first()
    status = db.session.query(Config.Config).first().status
    return render_template('config.pug', config=config, status=status)

@userApp.route('/config', methods=['POST'])
@login_required
def config_post():
    config = db.session.query(Config.Config).first()
    form = request.form
    if (form['cleanerTimeout']):
        config.cleanerTimeout = form['cleanerTimeout']
    if (form['delta_rec']):
        config.delta_rec = form['delta_rec']
    if (form.has_key('new_calls')):
        config.new_calls = True
    else:
        config.new_calls = False
    if (form.has_key('repeat_calls')):
        config.repeat_calls = True
    else:
        config.repeat_calls = False
    if (form.has_key('pacient_voice')):
        config.pacient_voice = True
    else:
        config.pacient_voice = False
    if (form.has_key('admin_voice')):
        config.admin_voice = True
    else:
        config.admin_voice = False
    if (form.has_key('task_call')):
        config.task_call = True
    else:
        config.task_call = False
    if (form.has_key('input_call')):
        config.input_call = True
    else:
        config.input_call = False
    if (form.has_key('output_call')):
        config.output_call = True
    else:
        config.output_call = False
    if (form.has_key('internal_call')):
        config.internal_call = True
    else:
        config.internal_call = False
    if (form.has_key('yandex')):
        config.yandex = True
    else:
        config.yandex = False
    if (form.has_key('google')):
        config.google = True
    else:
        config.google = False

    db.session.commit()

    return redirect(url_for('config'))

