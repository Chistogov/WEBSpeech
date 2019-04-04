# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for,request
from sqlalchemy import *
from userApp import *
from userApp.dbc import User, Journal, db, NameRec, Names, Config
from flask_login import login_required, current_user
import datetime, glob, os
import logging
import threading, time

@userApp.route('/')
@login_required
def index():
    logging.info("Index")
    history = list()
    dates = db.session.query(db.func.DATE(Journal.Journal.date)).group_by(Journal.Journal.date).order_by(Journal.Journal.date)
    journal = db.session.query(Journal.Journal)
    dex = list()
    dateFrom = ''
    if ('dateFrom' in request.args):
        if (request.args['dateFrom'] != ''):
            dateFrom = request.args['dateFrom']
            dates = dates.filter(db.func.DATE(Journal.Journal.date) >= dateFrom)
            dateFrom = datetime.datetime.strptime(dateFrom, "%Y-%m-%d %H:%M:%S")

    dateTo = ''
    if ('dateTo' in request.args):
        if (request.args['dateTo'] != ''):
            dateTo = request.args['dateTo']
            dates = dates.filter(db.func.DATE(Journal.Journal.date) <= dateTo)
            dateTo = datetime.datetime.strptime(dateTo, "%Y-%m-%d %H:%M:%S")
    specialist = ''
    specialist_name = ''
    records = ''
    if ('specialist' in request.args):
        if (request.args['specialist'] != ''):
            specialist = request.args['specialist']
            specialist_name = db.session.query(Names.Names).filter(Names.Names.id == specialist).first()
            records = db.session.query(NameRec.NameRec.journal_id).filter(NameRec.NameRec.name_id == specialist)
    new_calls = False
    repeat_calls = False
    if(dateFrom != '' or dateTo != '' or specialist != ''):
        for h in dates:
            if not(h[0] in dex):
                rec = recHistory()
                rec.date = h[0]
                if(specialist != ''):
                    notes = db.session.query(Journal.Journal).filter(db.func.DATE(Journal.Journal.date) == h[0], Journal.Journal.id.in_(records)).order_by(Journal.Journal.date)
                else:
                    notes = db.session.query(Journal.Journal).filter(db.func.DATE(Journal.Journal.date) == h[0]).order_by(Journal.Journal.date)
                if ('new_calls' in request.args and 'repeat_calls' in request.args):
                    if (request.args['new_calls'] == 'True' and request.args['repeat_calls'] == 'False'):
                        notes = notes.filter(Journal.Journal.new_call == True)
                    new_calls = request.args['new_calls']
                    if (request.args['repeat_calls'] == 'True' and request.args['new_calls'] == 'False'):
                        notes = notes.filter(Journal.Journal.new_call == False)
                    repeat_calls = request.args['repeat_calls']
                rec.rec = list()
                nex = list()
                for note in notes:
                    if not(note.record_name in nex):
                        rec_note = recNote()
                        rec_note.record_name = note.record_name
                        rec_note.notes = journal.filter(Journal.Journal.record_name == note.record_name)
                        rec.rec.append(rec_note)
                        nex.append(note.record_name)
                history.append(rec)
                dex.append(h[0])
    names = db.session.query(Names.Names)
    status = db.session.query(Config.Config).first().status
    return render_template('index.pug', history = history, names = names, dateFrom=dateFrom, dateTo=dateTo, specialist_name=specialist_name, new_calls=new_calls, repeat_calls=repeat_calls, status=status)

@userApp.route('/', methods=['POST'])
@login_required
def index_post():
    form = request.form
    dateTo = ''
    dateFrom = ''
    specialist = ''
    if (form['dateRecFrom']):
        dateFrom = datetime.datetime.strptime(form['dateRecFrom'], "%Y-%m-%d")
    if (form['dateRecTo']):
        dateTo = datetime.datetime.strptime(form['dateRecTo'], "%Y-%m-%d")
    if (form.has_key('specialist')):
        specialist = form['specialist']
    new_calls = False
    repeat_calls = False
    if (form.has_key('new_calls')):
        new_calls = True
    if (form.has_key('repeat_calls')):
        repeat_calls = True
    return redirect(url_for('index', dateFrom=dateFrom, dateTo=dateTo, specialist=specialist, repeat_calls=repeat_calls, new_calls=new_calls))


@userApp.route('/recognize')
@login_required
def recognize():
    logging.info("recognize")

    # thread = threading.Thread(target=recognizer.recognize_speech)
    # thread.start()

    return redirect(url_for('index'))

@userApp.route('/refers')
@login_required
def refers():
    logging.info("Refers")

    journal = db.session.query(Journal.Journal.id)

    dateFrom = ''
    if ('dateFrom' in request.args):
        if (request.args['dateFrom'] != ''):
            dateFrom = request.args['dateFrom']
            journal = journal.filter(db.func.DATE(Journal.Journal.date) >= dateFrom)
            dateFrom = datetime.datetime.strptime(dateFrom, "%Y-%m-%d %H:%M:%S")

    dateTo = ''
    if ('dateTo' in request.args):
        if (request.args['dateTo'] != ''):
            dateTo = request.args['dateTo']
            journal = journal.filter(db.func.DATE(Journal.Journal.date) <= dateTo)
            dateTo = datetime.datetime.strptime(dateTo, "%Y-%m-%d %H:%M:%S")

    timeFrom = ''
    if ('timeFrom' in request.args):
        if (request.args['timeFrom'] != ''):
            timeFrom = datetime.datetime.strptime(request.args['timeFrom'], "%Y-%m-%d %H:%M:%S")
            journal = journal.filter(and_(db.func.extract('hour', Journal.Journal.date) >= timeFrom.hour))
            # timeFrom = timeFrom.strftime("%H:%M:%S")
                                     # db.func.extract('minute', Journal.Journal.date) >= datetime.datetime.strptime(timeFrom, "%Y-%m-%d %H:%M:%S").minute))

    timeTo = ''
    if ('timeTo' in request.args):
        if (request.args['timeTo'] != ''):
            timeTo = datetime.datetime.strptime(request.args['timeTo'], "%Y-%m-%d %H:%M:%S")
            journal = journal.filter(and_(db.func.extract('hour', Journal.Journal.date) <= timeTo.hour))
                                     # db.func.extract('minute', Journal.Journal.date) <= datetime.datetime.strptime(timeTo, "%Y-%m-%d %H:%M:%S").minute))
            # timeTo = timeTo.strftime("%H:%M:%S")
    new_calls = False
    repeat_calls = False
    if ('new_calls' in request.args and 'repeat_calls' in request.args):
        if (request.args['new_calls'] == 'True' and request.args['repeat_calls'] == 'False'):
            journal = journal.filter(Journal.Journal.new_call == True)
        new_calls = request.args['new_calls']
        if (request.args['repeat_calls'] == 'True' and request.args['new_calls'] == 'False'):
            journal = journal.filter(Journal.Journal.new_call == False)
        repeat_calls = request.args['repeat_calls']

    notes_count = len(list(db.session.query(Journal.Journal.record_name).filter(Journal.Journal.id.in_(journal)).group_by(
        Journal.Journal.record_name)))

    refers = list()
    names = db.session.query(Names.Names).order_by(Names.Names.surname)
    for name in names:
        ref = refer()
        ref.doctor = name
        if(timeTo != '' or timeFrom != '' or dateTo != '' or dateFrom != '' or new_calls or repeat_calls):
            ids = db.session.query(NameRec.NameRec.journal_id).filter(NameRec.NameRec.name_id == name.id, NameRec.NameRec.journal_id.in_(journal))
            ref.refer_num = len(list(db.session.query(Journal.Journal.record_name).filter(Journal.Journal.id.in_(ids)).group_by(Journal.Journal.record_name)))
        else:
            ids = db.session.query(NameRec.NameRec.journal_id).filter(NameRec.NameRec.name_id == name.id)
            ref.refer_num = len(list(db.session.query(Journal.Journal.record_name).filter(Journal.Journal.id.in_(ids)).group_by(Journal.Journal.record_name)))

        refers.append(ref)
    # names = db.session.query(Names.Names)
    asc = ''
    alph = ''
    if ('alph' in request.args):
        if(request.args['alph'] == 'True'):
            refers.sort(key=lambda x: x.doctor.surname)
        alph = request.args['alph']
    if ('asc' in request.args):
        if(request.args['asc'] == 'True'):
            refers.sort(key=lambda x: x.refer_num, reverse=True)
        asc = request.args['asc']
    status = db.session.query(Config.Config).first().status

    return render_template('refers.pug', refers = refers, names=names, notes_count = notes_count, dateFrom=dateFrom, dateTo=dateTo,
                           timeTo=timeTo, timeFrom=timeFrom, asc=asc, alph=alph, new_calls=new_calls, repeat_calls=repeat_calls, status=status)

@userApp.route('/refers', methods=['POST'])
@login_required
def refers_post():
    form = request.form
    dateTo = ''
    timeTo = ''
    dateFrom = ''
    timeFrom = ''
    if (form['dateRecFrom']):
        dateFrom = datetime.datetime.strptime(form['dateRecFrom'], "%Y-%m-%d")
    if (form['dateRecTo']):
        dateTo = datetime.datetime.strptime(form['dateRecTo'], "%Y-%m-%d")
    if (form['timeRecFrom']):
        timeFrom = datetime.datetime.strptime(form['timeRecFrom'], "%H:%M")
    if (form['timeRecTo']):
        timeTo = datetime.datetime.strptime(form['timeRecTo'], "%H:%M")
    alph = False
    asc = False
    if (form.has_key('alph')):
        alph = True
    if (form.has_key('asc')):
        asc = True
    new_calls = False
    repeat_calls = False
    if (form.has_key('new_calls')):
        new_calls = True
    if (form.has_key('repeat_calls')):
        repeat_calls = True
    return redirect(url_for('refers', dateFrom=dateFrom, dateTo=dateTo, timeTo=timeTo, timeFrom=timeFrom, asc=asc, alph=alph, new_calls=new_calls, repeat_calls=repeat_calls))

class refer():
    doctor = ""
    refer_num = ""

class recHistory():
    date = ""
    rec = list()

class recNote():
    record_name = ""
    notes = ""
