import pytesseract as p
import cv2 as cv
from PIL import Image
import numpy as np
import os
import re
import fitz as f
p.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'#путь к файлу, с которым работает извлечение текста с картинки

def extract(path):
    pdf = f.open(path)#открывает pdf
    title = pdf.loadPage(0)#берёт титульный лист
    temp = title.getPixmap()#сохраняет его как картинку
    out = 'temp.png'
    temp.writePNG(out)
    img = remove_white(cv.imread(out))#открывает картинку и сразу вызывает метод обрезки белых краёв
    os.remove(out)#удаляет временный файл
    theme = get_theme(cut_theme(Image.fromarray(img)))#обрезает изображение так, что остаётся кусочек с темой
    img = cut_snp(img)#обрезает изображение так, что остаётся кусочек с ФИО студентов
    out = ['',theme,len(pdf)]#на выходе массив фамилий и тема ВКР
    if img is None:
        out[0] = None
    else:
        out[0] = get_snp(img)#получает массив ФИО студентов
        for i in range(0,len(out[0])-1):
            out[0][i] = out[0][i].strip(' ')#обрезка лишних пробелов
    return out

def remove_white(img):
    mask1 = cv.inRange(img,(0,0,0),(255,255,254))
    mask2 = cv.inRange(img,(0,0,0),(255,254,255))
    mask3 = cv.inRange(img,(0,0,0),(254,255,255))
    mask4 = cv.bitwise_or(mask1,mask2)
    mask = cv.bitwise_or(mask3,mask4)#бинаризация изображения и объединение масок в одну
    contours = cv.findContours(mask,cv.RETR_TREE,cv.CHAIN_APPROX_NONE)#извлечение информации о контурах
    contours = contours[0]#получение массива контуров
    contours = sorted(contours,key=cv.contourArea,reverse=True)#сортировка контуров по площади по невозрастанию
    x,y,w,h = cv.boundingRect(contours[0]) #извлечение координат обрамляющей наибольший контур рамки
    ww,hh,c = img.shape #получение размеров исходного изображения(переменная c не нужна)
    if cv.contourArea(contours[0])/(ww*hh) < 0.5:#если найденный контур занимает менее 50% общей площади изображения
        return img
    img = img[y:y+h,x:x+w]#обрезка исходного изображения по обрамляющей рамке
    return img

def cut_snp(img):
    img = Image.fromarray(img)#перевод массива пикселей в объект "изображение"
    w,h = img.size #извлечение размера исходного изображения
    crop = img.crop((0,h/2,w,h))#удаление верхней половины изображения
    w,h = crop.size#извлечение размеров обрезанного изображения
    w*=2
    h*=2
    img = crop.resize((w,h))#пропорциональное увеличение изображения в 2 раза
    img_copy = np.array(img.copy())#копирование
    img = np.array(img)#перевод изображения в массив
    w1 = 'работу'#опорные слова
    w2 = 'руководитель'
    top = []#координата первого
    bottom = []#координата второго
    n = 127
    t1 = True
    t2 = True
    k = 0
    while n < 255 and (t1 or t2):
        data = p.image_to_data(img_copy,'rus',output_type=p.Output.DICT)#считывание информации с картинки в словарь
        for i, word in enumerate(data['text']):#перебор слов в словаре
            if t1 and word.lower() == w1:
                top = [data['left'][i]+data['width'][i],data['top'][i]]#если первое слово найдено, берётся координата
                t1 = False
            elif t2 and word.lower() == w2:
                bottom = [data['left'][i]+data['width'][i],data['top'][i]]#если второе слово найдено, берётся координата
                t2 = False
        if not t1 and not t2:#если оба слова найдены
            break
        if k%3==0:#поочерёдное примененние бинаризации, для увеличения вероятности нахождения опорных слов (не очень хороший подход)
            img_copy = cv.threshold(img,n,255,cv.THRESH_TOZERO)[1]
        elif k%3==1:
            img_copy = cv.threshold(img,n,255,cv.THRESH_TRUNC)[1]
        elif k%3==2:
            img_copy = cv.threshold(img,n,255,cv.THRESH_BINARY)[1]
            n += 1
        k+=1
    if not t1 and not t2:#если оба слова найдены
        l = None#объявление левой границы
        if top[0] > bottom[0]:#поиск слова, которое правее
            l = top[0]
        else:
            l = bottom[0]
        img = Image.fromarray(img)#перевод массива в изображение        
        crop = img.crop((l,top[1],w,bottom[1]))#обрезка исходного изображения
        return crop
    else:
        return None
    
def get_snp(img):
    img = np.array(img)#перевод в массив
    match = []#создание массива
    n = 127
    k = 0
    err = False#переменная, которая предупреждает о возможной ошибке
    img_copy = (Image.fromarray(img)).copy()#копирование
    while n<255 and len(match) == 0:
        text = p.image_to_string(img_copy,'rus')#считывание текста
        text = re.sub('[^А-Яа-яЁё\s()]','',text)#оставить только буквы и скобки
        text = re.sub('\n',' ',text)#заменить переносы строк на пробелы
        mas = text.split(' ')#разделить нв отдельные слова
        pattern = '[А-ЯЁ][а-яё]+| |угли|кизи'#регулярное выражение для поиска отдельных слов, которые могут содержаться в ФИО
        text = ''
        for i in range(0,len(mas)):
            if re.match(pattern,mas[i]) is not None:#проверка слова на соответствие маске
                text += mas[i]+' '
        pattern = r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)(\s+(угли|кизи))?'#регулярное выражение для полных ФИО
        match = re.findall(pattern,text)
        if len(match) != 0:#если найденный текст полностью соответствует маске
            break
        if k%2==0:#если нет, изображение обрабатывается
            img_copy = cv.threshold(img,n,255,cv.THRESH_TOZERO)[1]
        elif k%2==1:
            img_copy = cv.threshold(img,n,255,cv.THRESH_TRUNC)[1]
            n+=1
        k+=1
    text = ''
    if len(match) != 0:
        for i in range(0,len(match)):
            if len(match[i][0]) <= 3 or len(match[i][1])<=3 or len(match[i][2]) <=3 or (len(match[i][4])!=0 and len(match[i][4]) <= 3):
                err = True#если что-то из ФИО длиной 3 символа, то, вероятно, считались помехи в качестве слова
            text += match[i][0]+' '+match[i][1]+' '+match[i][2]+' '+match[i][4] + '\n'
        text = text.split('\n')
    else:
        text = None  #не удалось найти ФИО студента
    if err:
        text[len(match)] = '!!!Возможна ошибка!!!'
    return text

def cut_theme(img):
    pattern = 'выпускная'
    num = '\d\d\.\d\d\.\d\d'
    w,h = img.size
    img = img.crop((0,h/3,w,2*h/3))
    w,h = img.size
    w*=2
    h*=2
    img = img.resize((w,h))
    n = 127
    copy = img.copy()
    first = False
    second = False #переменные, отвечающие за успешный поиск верхней и нижней границ
    up = -1
    down = -1
    while not first or not second:#пока проверка на неудачный поиск не обвалилась. 
        data = p.image_to_data(copy,'rus',output_type=p.Output.DICT)
        for j, word in enumerate(data['text']):
            match = re.search(pattern,word.lower())
            if not first and match is not None:
                up = data['top'][j]+data['height'][j]#поиск координаты верхнего предела
                first = True
            elif not second:
                match = re.search(num,word)
                if match is not None:
                    down = data['top'][j]#поиск координаты нижнего предела
                    second = True
            if first and second:
                break
        if first and second:
            break
        if n >=255:
            break
        if n==127:
            copy = Image.fromarray(cv.cvtColor(np.array(copy),cv.COLOR_BGR2GRAY))#если с первого раза не нашлось, то далее будем применять бинаризацию, пока не найдём
        copy = np.array(copy)
        copy = cv.threshold(copy,n,255,cv.THRESH_TOZERO)[1]
        n+=1
        copy = Image.fromarray(copy)
    if not first or not second:#если не удалось найти верхний предел
        return None
    img = img.crop((0,up,w,down))#обрезка изображения так, что только тема остаётся
    return img

def get_theme(img):
    pattern = '[«»А-ЯЁA-Z0-9\"\-.,:“”]+[«»\w\"\-.,:\s“”]*'#тема начинаеся с заглавной буквы или набора символов
    text = p.image_to_string(img,'eng+rus')
    themes = re.findall(pattern,text)
    theme = ''
    for i in themes:
        theme+=i
    theme = re.sub('\x0c','',theme)#тема содержит какие-то странные символы
    theme = theme.replace('\n',' ')
    theme = theme.strip(' ')
    theme = re.sub(' +',' ',theme)
    return theme
