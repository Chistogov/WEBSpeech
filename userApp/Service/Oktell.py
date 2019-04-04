# -*- coding: utf-8 -*-
import pyodbc, config



cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}',
                      server=config.Okt_server,
                      database=config.Okt_database,
                      uid=config.Okt_username,
                      pwd=config.Okt_password)
cursor = cnxn.cursor()
#Получение данных о звонке из БД Октелла
def getcall(datet):
    cursor.execute("SELECT ReasonStart, AOutNumber FROM A_Stat_Connections_1x1 WHERE DATEPART(YEAR, TimeStart) = " + str(
        datet.year) + " AND DATEPART(MONTH, TimeStart) = " + str(datet.month) + "  AND DATEPART(DAY, TimeStart) = " + str(datet.day) + " AND DATEPART(HOUR, TimeStart) = " + str(datet.hour) + " AND DATEPART(MINUTE , TimeStart) = " + str(datet.minute)+ " AND DATEPART(SECOND , TimeStart) = " + str(datet.second))
    return cursor.fetchall()[0]