import converter
import title
import os
import lit
import pg
# на входе папка, которая содержит папки, которые содержат pdf файлы
# на выходе папка с txt файлами

path = 'input\\'
out = 'txt\\'
if not os.path.isdir(out):
    os.makedirs(out)
mas = os.listdir(path)
for ii,i in enumerate(mas):
    print('{}/{}'.format(ii+1,len(mas))) #показывает, сколько папок уже обработано (необязательная строка)
    name = os.path.splitext(i)
    if name[1] == '':
        m = os.listdir(path+i)
        for jj,j in enumerate( m):
            name = os.path.splitext(j)
            if name[1]=='.pdf':
                data = title.extract(path+i+'\\'+j) #считывание ФИО и темы
                text = converter.convert(path+i+'\\'+j) #перевод в txt
                literature = lit.count(text) #подсчёт количества источников

                output = out+name[0]+'.txt' #запись в txt
                file = open(output,'w',encoding='utf-8',errors='ignore')
                file.write(text)
                file.close()
                
                '''
                data представляет собой массив, содержащий массив с ФИО и тему, т.е. 2 элемента
                массив с ФИО имеет n элементов с ФИО и пустой/непустой n+1 элемент, который содержит информацию о возможной ошибке при считывании фИО
                если ФИО не найдены, то data[0] имеет тип None, и метод len к нему применять нельзя
                Поэтому ниже по коду сначала вызывается проверка условия
                '''
                
                if data[0] is None:
                    pg.add([j,data[0],data[1],data[2],literature])
                    continue
                for k in range(0,len(data[0])-1):
                    if data[0][len(data[0])-1]!='':
                        data[0][k] = '!'+data[0][k]
                    pg.add([j,data[0][k],data[1],data[2],literature])
