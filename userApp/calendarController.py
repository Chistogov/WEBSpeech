# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for,request
from sqlalchemy import *
from userApp import *
from userApp.dbc import User, Journal, db, NameRec, Names, Config
from flask_login import login_required, current_user
import datetime, glob, os, time, threading, ftplib
import logging
import config

@userApp.route('/calendar')
@login_required
def calendar():
    logging.info("calendar")
    if ('date' in request.args):
        date = datetime.datetime.strptime(request.args['date'], "%Y-%m-%d %H:%M:%S")
        start_day = datetime.datetime.now().date().replace(month=date.month, year=date.year)
    else:
        start_day = datetime.datetime.now().date()
    start_day = start_day.replace(day=1)
    try:
        stop_day = start_day.replace(month=start_day.month + 1)
    except ValueError:
        stop_day = start_day.replace(year=start_day.year + 1, month=1)
    dates = list()
    for i in range((stop_day - start_day).days):
        view = viewer()
        view.date = start_day.replace(day=i+1)
        journal = db.session.query(Journal.Journal.id).filter(db.func.DATE(Journal.Journal.date) == start_day.replace(day=i+1))
        view.num_recs = len(
            list(db.session.query(Journal.Journal.record_name).filter(Journal.Journal.id.in_(journal)).group_by(
                Journal.Journal.record_name)))
        view.num_files = 0
        if (os.path.isdir(config.ARCHIVE_PATH + "/" + view.date.strftime('%Y%m%d'))):
            for root, dirs, files in os.walk(config.ARCHIVE_PATH + "/" + view.date.strftime('%Y%m%d')):
                view.num_files += len(files)
        dates.append(view)
    status = db.session.query(Config.Config).first().status
    return render_template('calendar.pug', dates = dates, current_date = start_day, status=status)

@userApp.route('/calendar', methods=['POST'])
@login_required
def calendar_post():
    form = request.form
    date = ''
    if (form['date']):
        date = datetime.datetime.strptime(form['date'], "%Y-%m-%d")
    my_thread = threading.Thread(target=uploadByTime, args=(form,))
    my_thread.start()
    return redirect(url_for('calendar', date=date.replace(day=1)))



@userApp.route('/calendar/recognize/<string:date>')
@login_required
def calendar_rec(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    for file in glob.glob(config.ARCHIVE_PATH + "/*/*/*.*"):
        print(file)
        date_call = file_name_to_date(os.path.basename(file).replace('.mp3', ''))
        if(date_call.date() == date.date()):
            if not (os.path.isdir(config.DATA_PATH + "/" + date_call.strftime('%Y%m%d') + "/" + date_call.strftime('%H%M'))):
                os.makedirs(config.DATA_PATH + "/" + date_call.strftime('%Y%m%d') + "/" + date_call.strftime('%H%M'))
            os.rename(file, config.DATA_PATH + "/" + date_call.strftime('%Y%m%d') + "/" + date_call.strftime('%H%M') + "/" + os.path.basename(file))
    return redirect(url_for('calendar', date = date.replace(day=1)))

@userApp.route('/calendar/download/<string:date>')
@login_required
def calendar_download(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    my_thread = threading.Thread(target=uploadByDate, args=(date,))
    my_thread.start()
    return redirect(url_for('calendar', date = date.replace(day=1)))

@userApp.route('/calendar/prev/<string:date>')
@login_required
def calendar_prev(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return redirect(url_for('calendar', date = date - datetime.timedelta(days=25)))

@userApp.route('/calendar/next/<string:date>')
@login_required
def calendar_next(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return redirect(url_for('calendar', date = date + datetime.timedelta(days=35)))

def file_name_to_date(file_name):
    dt_list = file_name.split('__')
    dt_str = dt_list[1] + "_" + dt_list[2]
    return datetime.datetime.strptime(dt_str, '%Y_%m_%d_%H_%M_%S_%f')

class viewer():
    date = ""
    num_recs = 0
    num_files = 0

#Обработка формы загрузки данных с сервера Октелла(по времени)
def uploadByTime(form):
    timeTo = ''
    timeFrom = ''
    if (form['date']):
        if (form['timeRecFrom']):
            timeFrom = datetime.datetime.strptime(form['date'] + " " + form['timeRecFrom'], "%Y-%m-%d %H:%M")
        if (form['timeRecTo']):
            timeTo = datetime.datetime.strptime(form['date'] + " " + form['timeRecTo'], "%Y-%m-%d %H:%M")
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
                                if not (os.path.isdir(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig)):
                                    os.makedirs(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig)
                                ftp.retrbinary("RETR " + file, open(
                                    config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig + "/" + file,
                                    "wb").write)
                                time.sleep(2)
                            except:
                                logging.info('[EXCEPTION Downloading]')
                                time.sleep(2)
                        ftp.cwd('../')
                ftp.cwd('../')

#Обработка формы загрузки данных с сервера Октелла(по дате)
def uploadByDate(date):
    ftp = ftplib.FTP()
    ftp.connect(config.FTP_IP)
    ftp.login(config.FTP_LOGIN, config.FTP_PASSWORD)
    logging.info('[Downloading new files]')
    for entry_date in ftp.nlst():
        dir_date_orig = entry_date
        dir_date = datetime.datetime.strptime(entry_date, '%Y%m%d')
        if(dir_date.date() == date.date()):
            ftp.cwd(entry_date)
            for entry_time in ftp.nlst():
                dir_time_orig = entry_time
                ftp.cwd(entry_time)
                for file in ftp.nlst():
                    try:
                        if not (os.path.isdir(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig)):
                            os.makedirs(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig)
                        ftp.retrbinary("RETR " + file, open(config.DATA_PATH + "/" + dir_date_orig + "/" + dir_time_orig + "/" + file, "wb").write)
                        time.sleep(2)
                    except:
                        logging.info('[EXCEPTION Downloading]')
                        time.sleep(2)
                ftp.cwd('../')
            ftp.cwd('../')
    logging.info('[Downloading OK]')

