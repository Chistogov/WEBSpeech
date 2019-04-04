# -*- coding: utf-8 -*-
from userApp.dbc import Names, db, Journal, NameRec
from sqlalchemy.orm import sessionmaker
import logging
import datetime as dt

#Получение вхождений в строке(при перыичном распознании), возвращает массив id найденных вхождений
def get_names(s):
    names = db.session.query(Names.Names).all()
    ids = list()
    for name in names:
        flag = 0
        if(name.short_name.lower() in s.lower()):
            flag += 1
            sp = s.split(' ')
            i = 0
            # print name.name
            for w in sp:
                if (name.short_name.lower() in w.lower()):
                    for sub_w in sp[i-2:i+3]:
                        if(name.short_surname.lower() in sub_w.lower() or name.short_middle_name.lower() in sub_w.lower()):
                            flag += 1
                i += 1
        if(name.short_surname.lower() in s.lower()):
            flag += 2
        if(flag >= 2):
            if not (name.id in ids):
                ids.append(name.id)
                logging.info("[<-Entries->]" + name.surname + " " + name.name + " " + name.middle_name)
    return ids

#Поиск вхождений в архиве, функция сама записывает найденных вхождения в БД (должна выполняться в потоке)
def search_all(name_id):
    name = db.session.query(Names.Names).filter(Names.Names.id == name_id).first()
    notes = db.session.query(Journal.Journal)
    for note in notes:
        flag = 0
        if(note.text):
            if(name.short_name.lower() in note.text.lower()):
                flag += 1
                sp = note.text.split(' ')
                i = 0
                # print name.name
                for w in sp:
                    if (name.short_name.lower() in w.lower()):
                        for sub_w in sp[i-2:i+3]:
                            if(name.short_surname.lower() in sub_w.lower() or name.short_middle_name.lower() in sub_w.lower()):
                                flag += 1
                    i += 1
            if(name.short_surname.lower() in note.text.lower()):
                flag += 2
            if(flag >= 2):
                namerec = NameRec.NameRec()
                namerec.journal_id = note.id
                namerec.name_id = name.id
                namerec.pacient = True
                db.session.add(namerec)
                db.session.commit()
        flag = 0
        if(note.admin_text):
            if (name.short_name.lower() in note.admin_text.lower()):
                flag += 1
                sp = note.admin_text.split(' ')
                i = 0
                # print name.name
                for w in sp:
                    if (name.short_name.lower() in w.lower()):
                        for sub_w in sp[i - 2:i + 3]:
                            if (
                                    name.short_surname.lower() in sub_w.lower() or name.short_middle_name.lower() in sub_w.lower()):
                                flag += 1
                    i += 1
            if (name.short_surname.lower() in note.admin_text.lower()):
                flag += 2
            if (flag >= 2):
                namerec = NameRec.NameRec()
                namerec.journal_id = note.id
                namerec.name_id = name.id
                namerec.pacient = False
                db.session.add(namerec)
                db.session.commit()

def file_name_to_date(file_name):
    dt_list = file_name.split('__')
    dt_str = dt_list[1] + "_" + dt_list[2]
    return dt.datetime.strptime(dt_str, '%Y_%m_%d_%H_%M_%S_%f')
