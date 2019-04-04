# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for,request
from sqlalchemy import *
from userApp import *
from userApp.Service import Entries
from userApp.dbc import User, Journal, db, NameRec, Names, Config
from flask_login import login_required, current_user
import datetime, glob, os
import logging
import threading, time

@userApp.route('/names')
@login_required
def names():
    logging.info("names")
    names = db.session.query(Names.Names)
    status = db.session.query(Config.Config).first().status
    return render_template('names.pug', status=status, names=names)

@userApp.route('/names', methods=['POST'])
@login_required
def names_post():
    form = request.form
    name = Names.Names()
    name.name = form['name']
    name.short_name = form['short_name']
    name.surname = form['surname']
    name.short_surname = form['short_surname']
    name.middle_name = form['middle_name']
    name.short_middle_name = form['short_middle_name']
    db.session.add(name)
    db.session.commit()


    if (form.has_key('search_ref')):
        my_thread = threading.Thread(target=Entries.search_all, args=(name.id,))
        my_thread.start()
        # Entries.search_all(name.id)

    return redirect(url_for('names'))

@userApp.route('/names/remove/<int:id>', methods=['GET'])
@login_required
def name_remove(id):
    db.session.query(NameRec.NameRec).filter(NameRec.NameRec.name_id == id).delete()
    db.session.query(Names.Names).filter(Names.Names.id == id).delete()
    db.session.commit()
    return redirect(url_for('names'))

@userApp.route('/names/refers/<int:id>', methods=['GET'])
@login_required
def name_refers(id):
    db.session.query(NameRec.NameRec).filter(NameRec.NameRec.name_id == id).delete()
    db.session.commit()

    my_thread = threading.Thread(target=Entries.search_all, args=(id,))
    my_thread.start()
    # Entries.search_all(id)
    return redirect(url_for('names'))