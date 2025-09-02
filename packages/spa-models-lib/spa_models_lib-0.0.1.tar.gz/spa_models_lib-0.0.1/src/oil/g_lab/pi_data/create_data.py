# Библиотека обработки PI
# 01.09.21 - Создан
import json
import logging as logger
import os
from inspect import currentframe, getframeinfo

import matplotlib.pyplot as plt
import pandas as pd


# Параметры алгоритма
class CGlobClass:
    def __init__(self):
        self.tag_connection = []
        self.datawarning = dict()   # глобальный сбор нарушений по данным
        self.updownlimits = dict()  # глобальный сбор превышений лимитов

    def add_connection(self, tag_connection):
        self.tag_connection = tag_connection

    def logerror(self, frameinfo, msg):
        logger.error(f'{frameinfo.filename}  {frameinfo.lineno} {msg}')


# Конвертор
class CDataPIConverter:
    def __init__(self, glob_class, input_path='', file_construcor=''):
        getframeinfo(currentframe())
        self.gloabclass = glob_class
        self.dir_path = input_path
        self.conected_tag = []
        if len(self.dir_path) > 0:
            self.dir_path = self.dir_path + '/'
        if input_path == [] or file_construcor == []:
            msg = f"Can't create constructor {type(self)._class_name}"
            self.gloabclass.logerror(getframeinfo(currentframe()), msg)
            raise Exception(msg)

        pi_srcfileneme = self.dir_path + file_construcor['pi_data']
        if os.path.exists(pi_srcfileneme):
            self.srcdf = pd.read_json(pi_srcfileneme, encoding='ISO-8859-1')
        else:
            msg = f"Can't find file {pi_srcfileneme}"
            self.gloabclass.logerror(getframeinfo(currentframe()), msg)
            raise Exception(msg)

        self.conected_tag = []
        # totlist - получить список всех тегов по которым есть связь имен
        for i in self.gloabclass.tag_connection.values():
            tmpl = i.split('|')

            if len(tmpl) > 1:
                t = tmpl
                for k in t:
                    self.conected_tag.append(k)
            else:
                self.conected_tag.append(tmpl[0])

        self.srcUniqueTags = list(self.srcdf['TAG_NAME'].unique())
        if 'DATE_REQUEST' in self.srcdf.columns:
            self.srcdf['datetime'] = pd.to_datetime(self.srcdf.DATE_REQUEST)
        else:
            self.srcdf = self.srcdf.rename(columns={'TIME': 'datetime'})
            self.srcdf['datetime'] = pd.to_datetime(self.srcdf['datetime'])
        self.srcdf = self.srcdf.set_index('datetime')
        # self.srcdf=self.srcdf.loc[self.srcdf['TAG_NAME'] == 'KCA:PI001']

        self.curdfdict = dict()
        print(f'{self.srcUniqueTags}')
        self.red_lambdas = dict()
        self.red_up_lambdas = dict()
        self.red_down_lambdas = dict()

        """
        Для внешних параметров 

        self.red_lambdas['KCA:PI001']           =   (lambda x: x >0.03 or x<0.015)
        self.red_up_lambdas['KCA:PI001']        =   (lambda x: x >0.03 )
        self.red_down_lambdas['KCA:PI001']     =   (lambda x: x <0.015 )

        self.red_lambdas['KCA:PI002'] = (lambda x: x > 0.78 or x < 0.015)
        self.red_up_lambdas['KCA:PI002'] = (lambda x: x > 0.78)
        self.red_down_lambdas['KCA:PI002'] = (lambda x: x < 0.015)

        self.red_lambdas['KCA:PI004'] = (lambda x: x > 0.6 or x < 0.015)
        self.red_up_lambdas['KCA:PI004'] = (lambda x: x > 0.6)
        self.red_down_lambdas['KCA:PI004'] = (lambda x: x < 0.015)

        self.red_lambdas['KCA:TI018'] = (lambda x: x > 80 or x < 60)
        self.red_up_lambdas['KCA:TI018'] = (lambda x: x > 80)
        self.red_down_lambdas['KCA:TI018'] = (lambda x: x < 60)

        self.red_lambdas['KCA:TI019'] = (lambda x: x > 80 or x < 60)
        self.red_up_lambdas['KCA:TI019'] = (lambda x: x > 80)
        self.red_down_lambdas['KCA:TI019'] = (lambda x: x < 60)

        self.red_lambdas['KCA:TI020'] = (lambda x: x > 80 or x < 60)
        self.red_up_lambdas['KCA:TI020'] = (lambda x: x > 80)
        self.red_down_lambdas['KCA:TI020'] = (lambda x: x < 60)

        self.red_lambdas['KCA:TI023'] = (lambda x: x > 80 or x < 60)
        self.red_up_lambdas['KCA:TI023'] = (lambda x: x > 80)
        self.red_down_lambdas['KCA:TI023'] = (lambda x: x < 60)

        """

    # Создание расчета по часовикам дневного сигнала
    def create_indays_statistic(self, daystime=[], type_s='no', sens=0.5):
        if type_s == 'no':
            return []

        res = dict()
        for dday in daystime:   # Для каждого дня в ЛИМС найдем PI, если нет, то выдаем сообщение
            for i in self.srcUniqueTags:
                if not i in self.conected_tag:
                    continue
                if type_s == 'status':
                    if not i in res:
                        res[i] = {dday: 'NORM'}
                    else:
                        res[i][dday] = 'NORM'
                elif type_s == 'value':
                    if not i in res:
                        res[i] = {dday: None}
                    else:
                        res[i][dday] = None

                # Если интересует только последний день
                # l = len((self.srcdf[self.srcdf.TAG_NAME == i]['ZONE_RED']).resample('1D').mean())

                # Так как данные синхронны, то индексы совпадают!!!!!
                h = (self.srcdf[self.srcdf.TAG_NAME == i]['ZONE_RED']).resample('1D').mean()
                if dday in h:

                    k = h.index.get_loc(dday)
                    D_red = ((self.srcdf[self.srcdf.TAG_NAME == i]['ZONE_RED']).resample('1D').mean())[k]

                    D_count = ((self.srcdf[self.srcdf.TAG_NAME == i]['COUNT']).resample('1D').mean())[k]
                    D_red_up = ((self.srcdf[self.srcdf.TAG_NAME == i]['ZONE_RED_UP']).resample('1D').mean())[k]
                    D_red_down = ((self.srcdf[self.srcdf.TAG_NAME == i]['ZONE_RED_DOWN']).resample('1D').mean())[k]
                    D_mean = ((self.srcdf[self.srcdf.TAG_NAME == i]['MEAN']).resample('1D').mean())[k]
                    redup_p = D_red_up / D_count
                    reddw_p = D_red_down / D_count

                    if D_count > 50:
                        if type_s == 'status':
                            if redup_p > sens or reddw_p > sens:   # если достаточно дланных для возведения влага
                                if D_red_up > D_red_down:
                                    res[i][dday] = 'RED_UP'   # выход вверх
                                else:
                                    res[i][dday] = 'RED_DOWN'   # выход вниз
                        else:
                            res[i][dday] = D_mean  # выход вниз

                    else:
                        logger.error(f'Данные ЛИМС не синхронны с PI {i}')
                else:
                    msg = f'Недостаточно данных по статистике'
                    logger.error(msg + i + ' ' + dday)
        return res

    def create_statistic(self):
        df = pd.DataFrame()
        glob = pd.DataFrame(columns=['TAG_NAME', 'ZONE_RED', 'ZONE_RED_UP', 'ZONE_RED_DOWN', 'COUNT'])
        for i in self.srcUniqueTags:
            if not i in self.conected_tag:
                continue

            h = self.srcdf[self.srcdf.TAG_NAME == i]['TAG_VALUE']
            test1 = pd.DataFrame(columns=['TAG_NAME', 'ZONE_RED', 'ZONE_RED_UP', 'ZONE_RED_DOWN', 'COUNT'])
            red = h.apply(self.red_lambdas[i])
            red_up = h.apply(self.red_up_lambdas[i])
            red_down = h.apply(self.red_down_lambdas[i])
            self.srcdf['red'] = red
            self.srcdf['red_down'] = red_down
            self.srcdf['red_up'] = red_up
            h1_count = h.resample('1H').count()
            h1_count_red = (red[red == True]).resample('1H').sum().astype(int)
            h1_count_red_up = (red_up[red_up == True]).resample('1H').sum().astype(int)
            h1_count_red_down = (red_down[red_down == True]).resample('1H').sum().astype(int)

            test1['COUNT'] = h1_count
            test1['ZONE_RED'] = h1_count_red
            test1['ZONE_RED_UP'] = h1_count_red_up
            test1['ZONE_RED_DOWN'] = h1_count_red_down
            test1['MEAN'] = h.resample('1H').mean()

            test1['TAG_NAME'] = i

            glob = glob.append(test1, sort=True)
            res = list()

        glob = glob.fillna(0)
        # glob.index=pd.to_datetime(glob.index).
        glob.reset_index(inplace=True)
        glob = glob.rename(columns={'index': 'TIME'})
        glob['TIME'] = glob['TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
        result = glob.to_json(orient='records', date_format='iso')
        parsed = json.loads(result)
        q = json.dumps(parsed, indent=4)
        with open('result_pidata.json', 'w') as f:
            f.write(q)
        # for ir in df.iterrows():
        #         v = dict()
        #         v['TAG_NAE']=i
        #         v['MEAN']
        #         print(i)

        # parsed=df.to_json(orient="index")
        # q=json.dumps(parsed, indent=4)
        # with open('c:/tmp/file_name.json', 'w') as f:
        #     f.write(q)

        # h = h.resample('1H').mean()
        # self.curdfdict[i] = {'1H': h}

    def convert1H(self):
        totlist = []
        # totlist - получить список всех тегов по которым есть связь имен
        for i in self.gloabclass.tag_connection.values():
            tmpl = i.split('|')

            if len(tmpl) > 1:
                t = tmpl
                for k in t:
                    totlist.append(k)
            else:
                totlist.append(tmpl[0])

        for i in self.srcUniqueTags:
            if not i in totlist:
                continue

            h = self.srcdf[self.srcdf.TAG_NAME == i]['TAG_VALUE']
            h = h.resample('1H').mean()
            self.curdfdict[i] = {'1H': h}

    def ploting(self, name):
        if not name in self.gloabclass.tag_connection:
            return 'not name'
        alist = self.gloabclass.tag_connection[name].split('|')
        plt.figure()

        for i in alist:
            self.curdfdict[i]['1H'].plot()
            plt.grid()
            plt.title(alist)

    def plotingsource(self, name):
        if not name in self.gloabclass.tag_connection:
            return 'not name'
        alist = self.gloabclass.tag_connection[name].split('|')
        plt.figure()
        for i in alist:
            self.srcdf[self.srcdf['TAG_NAME'] == i]['TAG_VALUE'].plot()
            plt.grid()
            plt.title(alist)

    def getval(name, self):
        h = self.srcdf[self.srcdf.TAG_NAME == self.gloabclass.tag_connection[name]]
        return h

    def getTAGValue(self, name, type='ONE'):
        res = 0
        if type == 'AND':

            # h  = self.srcdf[self.srcdf.TAG_NAME == self.gloabclass.tag_connection[name]]
            for iname in self.gloabclass.tag_connection[name].split('|'):
                h = self.curdfdict[iname]
                res += h['1H'].mean()
                # Общее среднее
            res = res / len(self.gloabclass.tag_connection[name].split('|'))
        else:
            h = self.curdfdict[self.gloabclass.tag_connection[name]]
            res = h['1H'].mean()
        return res


# подготовка данных для тестирования.
# 1. Конвертируем данные от Володи, добавляем ,
# 2. Сохраняем данные в нужном формате
if __name__ == '__main__':
    # with open("inputdatapi.json", "r") as myfile:
    #     data = myfile.readlines()
    #
    # with open("input_pidata.json", "w") as myfile2:
    #     #data = myfile.readlines()
    #     i=0
    #     for line in data:
    #         line = line.strip()
    #         i=i+1
    #
    #         if i==len(data):
    #            myfile2.write(line+"\n")
    #         else:
    #            myfile2.write(line + ","+"\n")

    tag_connection = {
        'Давление масла P1': 'KCA:PI001',
        'Давление масла P2': 'KCA:PI002',
        'Давление масла P4': 'KCA:PI004',
        'Температура подшипника Вала Компрессора': 'KCA:TI018|KCA:TI019|KCA:TI020|KCA:TI023',
    }

    globVariable = CGlobClass()
    # назначим параметры
    globVariable.add_connection(tag_connection)

    A = CDataPIConverter(glob_class=globVariable, file_construcor={'pi_data': 'input_pidata.json'})
    A.create_statistic()
    A.convert1H()
    A.plotingsource('Давление масла P1')
    # A.plotingsource("Давление масла P2")
    # A.plotingsource("Давление масла P4")
    # A.plotingsource("Температура подшипника Вала Компрессора")

    A.ploting('Давление масла P1')
    A.ploting('Давление масла P2')
    A.ploting('Давление масла P4')
    A.ploting('Температура подшипника Вала Компрессора')

    # A.plotingsource("Давление масла P2"
    # A.getTAGValue("Давление масла P1")
    # A.ploting("Давление масла P1")
    # A.ploting("Температура подшипника Вала Компрессора")
    print()
    input('Press Enter to continue...')
