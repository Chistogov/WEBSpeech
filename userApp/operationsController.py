# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for,request
from sqlalchemy import *
from userApp import *
from userApp.Service import Entries
from userApp.dbc import User, Journal, db, NameRec, Names, Config
from flask_login import login_required, current_user
import datetime, glob, os
import logging
import threading, time, ftplib, config

@userApp.route('/operations')
@login_required
def operations():
    logging.info("operations")
    status = db.session.query(Config.Config).first().status
    return render_template('operations.pug', status=status)

@userApp.route('/operations', methods=['POST'])
@login_required
def operations_post():
    form = request.form
    my_thread = threading.Thread(target=uploadByTime, args=(form,))
    my_thread.start()

    return redirect(url_for('operations'))

#Установка статуса ПО
def setStaus(status):
    config = db.session.query(Config.Config).first()
    config.status = status
    db.session.commit()

#Обработка формы загрузки данных с сервера Октелла(по дате и времени)
def uploadByTime(form):
    timeTo = ''
    timeFrom = ''
    journal = db.session.query(Journal.Journal.record_name).all()
    if (form['dateRecFrom']):
        timeFrom = datetime.datetime.strptime(form['dateRecFrom'], "%Y-%m-%d")
    if (form['dateRecTo']):
        timeTo = datetime.datetime.strptime(form['dateRecTo'], "%Y-%m-%d")
    if (form['timeRecFrom']):
        timeFrom = datetime.datetime.strptime(form['dateRecFrom'] + " " + form['timeRecFrom'], "%Y-%m-%d %H:%M")
    if (form['timeRecTo']):
        timeTo = datetime.datetime.strptime(form['dateRecTo'] + " " + form['timeRecTo'], "%Y-%m-%d %H:%M")
    ftp = ftplib.FTP()
    ftp.connect(config.FTP_IP)
    ftp.login(config.FTP_LOGIN, config.FTP_PASSWORD)
    for entry_date in ftp.nlst():
        dir_date_orig = entry_date
        dir_date = datetime.datetime.strptime(entry_date, '%Y%m%d')
        if (dir_date.date() >= timeFrom.date() and dir_date.date() <= timeTo.date()):
            ftp.cwd(entry_date)
            for entry_time in ftp.nlst():
                dir_time_orig = entry_time
                dir_time = datetime.datetime.strptime(dir_date_orig + " " + entry_time, '%Y%m%d %H%M')
                if (dir_time >= timeFrom and dir_time <= timeTo):
                    ftp.cwd(entry_time)
                    for file in ftp.nlst():
                        try:
                            setStaus('[Загрузка файлов]')
                            if not(file in journal):
                                if not (os.path.isdir(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig)):
                                    os.makedirs(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig)
                                ftp.retrbinary("RETR " + file, open(
                                    config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig + "/" + file,
                                    "wb").write)
                        except:
                            logging.info('[EXCEPTION Downloading]')
                    ftp.cwd('../')
            ftp.cwd('../')
    setStaus('Простой')