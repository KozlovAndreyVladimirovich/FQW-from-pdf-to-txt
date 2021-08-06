import fitz
import os
def convert(path):
    name = os.path.splitext(path)
    text = ''
    if name[1] == '.pdf':
        pdf = fitz.open(path)#открывает pdf
        for i in range(1,len(pdf)):#0-я страница - изображение
            page = pdf.loadPage(i)#берёт конкретную страницу
            a = page.getText('text')#извлекает текст
            if(isinstance(a, str)):#если тип переменной строковый
                text += a + '\n'#присоединяет строку
    return text
