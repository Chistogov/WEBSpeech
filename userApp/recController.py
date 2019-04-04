# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for,request
from sqlalchemy import *
import config
from userApp import *
from userApp.dbc import User, Journal, db, NameRec, Names, Config
from userApp.Service import Yandex, Google, Entries
from flask_login import login_required, current_user
import datetime, glob, os
import logging
import threading, time

@userApp.route('/rec/<int:id>')
@login_required
def rec(id):
    logging.info("rec")
    rec = db.session.query(Journal.Journal).filter(Journal.Journal.id == id).first()
    status = db.session.query(Config.Config).first().status
    return render_template('rec/card.pug', note=rec, status=status)


@userApp.route('/adm_processing/<int:id>')
@login_required
def adm_processing(id):
    logging.info("adm_processing")
    journal = db.session.query(Journal.Journal).filter(Journal.Journal.id == id).first()
    journal.admin_text = "Распознание..."
    db.session.commit()
    if("Yandex" in journal.recognizer):
        my_thread = threading.Thread(target=Yad, args=(id,), kwargs={'pacient': 'False'})
        my_thread.start()
        # Yad(id, pacient=False)
    else:
        my_thread = threading.Thread(target=Go2, args=(id,), kwargs={'pacient': 'False'})
        my_thread.start()
        # Go2(id, pacient=False)
    return redirect('/rec/'+str(id))

@userApp.route('/pacient_processing/<int:id>')
@login_required
def pacient_processing(id):
    logging.info("pacient_processing")
    journal = db.session.query(Journal.Journal).filter(Journal.Journal.id == id).first()
    journal.text = "Распознание..."
    db.session.commit()
    if("Yandex" in journal.recognizer):
        my_thread = threading.Thread(target=Yad, args=(id, ), kwargs = {'pacient':'True'})
        my_thread.start()
        # Yad(id, pacient=True)
    else:
        my_thread = threading.Thread(target=Go2, args=(id,), kwargs={'pacient': 'True'})
        my_thread.start()
        # Go2(id, pacient=True)
    return redirect('/rec/'+str(id))

@userApp.route('/entries_pacient/<int:id>')
@login_required
def entries_pacient(id):
    logging.info("entries_pacient")
    journal = db.session.query(Journal.Journal).filter(Journal.Journal.id == id).first()
    db.session.query(NameRec.NameRec).filter(NameRec.NameRec.journal_id == journal.id, NameRec.NameRec.pacient == True).delete()
    db.session.commit()
    if(journal.text):
        for item in Entries.get_names(journal.text):
            old_recs = db.session.query(NameRec.NameRec).filter(NameRec.NameRec.journal_id == journal.id, NameRec.NameRec.name_id == item, NameRec.NameRec.pacient == True)
            if(len(list(old_recs)) == 0):
                namerec = NameRec.NameRec()
                namerec.journal_id = journal.id
                namerec.name_id = item
                namerec.pacient = True
                db.session.add(namerec)
                db.session.commit()
    return redirect('/rec/'+str(id))

@userApp.route('/entries_adm/<int:id>')
@login_required
def entries_adm(id):
    logging.info("entries_adm")
    journal = db.session.query(Journal.Journal).filter(Journal.Journal.id == id).first()
    db.session.query(NameRec.NameRec).filter(NameRec.NameRec.journal_id == journal.id, NameRec.NameRec.pacient == False).delete()
    db.session.commit()
    if(journal.admin_text):
        for item in Entries.get_names(journal.admin_text):
            old_recs = db.session.query(NameRec.NameRec).filter(NameRec.NameRec.journal_id == journal.id, NameRec.NameRec.name_id == item, NameRec.NameRec.pacient == False)
            if(len(list(old_recs)) == 0):
                namerec = NameRec.NameRec()
                namerec.journal_id = journal.id
                namerec.name_id = item
                namerec.pacient = False
                db.session.add(namerec)
                db.session.commit()
    return redirect('/rec/'+str(id))

#Перевод звука в текст (работа с БД, вызывает функцию работы с Yandex.Speech)
def Yad(rec_id, pacient = True):
    logging.info("[Yandex Start " + str(datetime.datetime.now()) +"]")
    journal = db.session.query(Journal.Journal).filter(Journal.Journal.id == rec_id).first()
    date_call = Entries.file_name_to_date(journal.record_name.replace('.mp3', ''))
    file =  config.ARCHIVE_PATH + "/" + date_call.strftime('%Y%m%d') + "/" + date_call.strftime('%H%M') + "/" + journal.record_name
    result = Yandex.recognize(file, pacient=pacient)
    pc = False
    if (pacient == "True" or pacient == True):
        journal.text = result
        pc = True
    else:
        journal.admin_text = result
    db.session.commit()
    print("Yandex OK")
    for item in Entries.get_names(result):
        old_recs = db.session.query(NameRec.NameRec).filter(NameRec.NameRec.journal_id == journal.id, NameRec.NameRec.name_id == item, NameRec.NameRec.pacient == pacient)
        if(len(list(old_recs)) == 0):
            namerec = NameRec.NameRec()
            namerec.journal_id = journal.id
            namerec.name_id = item
            namerec.pacient = pc
            db.session.add(namerec)
            db.session.commit()

#Перевод звука в текст (работа с БД, вызывает функцию работы с Google.Speech)
def Go2(rec_id, pacient = True):
    logging.info("[Google Start" + str(datetime.datetime.now()) +"]")
    journal = db.session.query(Journal.Journal).filter(Journal.Journal.id == rec_id).first()
    date_call = Entries.file_name_to_date(journal.record_name.replace('.mp3', ''))
    file = config.ARCHIVE_PATH + "/" + date_call.strftime('%Y%m%d') + "/" + date_call.strftime('%H%M') + "/" + journal.record_name
    result = Google.recognize_v1p1beta1(file, pacient=pacient)
    pc = False
    if (pacient == "True" or pacient == True):
        journal.text = result
        pc = True
    else:
        journal.admin_text = result
    db.session.commit()
    print("Google OK")
    for item in Entries.get_names(result):
        old_recs = db.session.query(NameRec.NameRec).filter(NameRec.NameRec.journal_id == journal.id, NameRec.NameRec.name_id == item, NameRec.NameRec.pacient == pacient)
        if(len(list(old_recs)) == 0):
            namerec = NameRec.NameRec()
            namerec.journal_id = journal.id
            namerec.name_id = item
            namerec.pacient = pc
            db.session.add(namerec)
            db.session.commit()