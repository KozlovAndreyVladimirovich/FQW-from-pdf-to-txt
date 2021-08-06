import converter
import title
import os
import lit
import pg

#path = 'input\\'
path = 'IN\\'
out = 'txt\\'
if not os.path.isdir(out):
    os.makedirs(out)
mas = os.listdir(path)
for ii,i in enumerate(mas):
    print('{}/{}'.format(ii+1,len(mas)))
    name = os.path.splitext(i)
    if name[1] == '':
        m = os.listdir(path+i)
        for jj,j in enumerate( m):
            name = os.path.splitext(j)
            if name[1]=='.pdf':
                data = title.extract(path+i+'\\'+j)
                text = converter.convert(path+i+'\\'+j)
                literature = lit.count(text)

                output = out+name[0]+'.txt'
                file = open(output,'w',encoding='utf-8',errors='ignore')
                file.write(text)
                file.close()
                
                if data[0] is None:
                    pg.add([j,data[0],data[1],data[2],literature])
                    continue
                for k in range(0,len(data[0])-1):
                    if data[0][len(data[0])-1]!='':
                        data[0][k] = '!'+data[0][k]
                    pg.add([j,data[0][k],data[1],data[2],literature])
