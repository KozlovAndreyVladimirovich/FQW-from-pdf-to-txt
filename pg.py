import psycopg2 as ps

def add(data):
    connection = ps.connect(dbname='имя_бд',user='postgres',password='пароль',host='localhost')
    cursor = connection.cursor()
    for i in range(0,len(data)):
        if data[i] is None:
            data[i]='Null'
    cursor.execute('select * from Students where "Файл" = \'{}\''.format(data[0]))
    records = cursor.fetchall()
    if len(records)==0:
        cursor.execute('insert into Students("Файл","ФИО","Тема","Страницы","Источники") values(\'{}\',\'{}\',\'{}\',{},{})'.format(data[0],data[1],data[2],data[3],data[4]))
    else:
        cursor.execute('update Students set "ФИО" = \'{}\', "Тема" = \'{}\', "Страницы" = {}, "Источники" = {} where "Файл" = \'{}\''.format(data[1],data[2],data[3],data[4],data[0]))
    connection.commit()
    cursor.close()
    connection.close()
