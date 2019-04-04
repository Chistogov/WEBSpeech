# -*- coding: utf-8 -*-
import pyodbc, config



cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}',
                      server=config.Pol_server,
                      database=config.Pol_database,
                      uid=config.Pol_username,
                      pwd=config.Pol_password)
cursor = cnxn.cursor()
f = '%d.%m.%Y'
#Возвращает результат функции из полимеда
def getcall(date):
    cursor.execute("SELECT * FROM fn_phoneZapPac (CONVERT(DATETIME,\'" + date.strftime(f) + "\'))")
    return cursor.fetchall()