from email import header
from logging import exception
import os
import datetime
import pandas as pd

DataPath = 'D:\\FlawDataRec'  #保存缺陷数据的文件夹 绝对路径
PiciFloderIni = 0
PiciFlag = 1
DateFloder = ''

def CreatFloder():
    global DateOfFloder
    if os.path.exists(DataPath):
        print('文件夹存在')
    else:
        os.makedirs(DataPath)
        print('创建成功')

    # 创建日期文件夹
    todaystr = datetime.date.today().strftime('%y%m%d')
    yearsrt = todaystr[0:2]
    monthstr = todaystr[2:4]
    daysrt = todaystr[4:]
    if todaystr[2] == '1':
        if todaystr[3] == '0':
            monthstr = 'X'
        elif todaystr[3] == '1':
            monthstr = 'Y'        
        elif todaystr[3] == '2':
            monthstr = 'Z'
        DateOfFloder = yearsrt + monthstr + daysrt
    else:
        DateOfFloder = yearsrt + monthstr[1] + daysrt
    # 日期文件夹路径
    DateFloder = DataPath +'\\'+ DateOfFloder
        
    if os.path.exists(DateFloder):
        print('日期文件夹存在')
    else:
        os.makedirs(DateFloder)
        print('日期文件夹创建成功')

    if PiciFlag:
        global PiciFloderIni
        PiciFloderIni = PiciFloderIni + 1
        PiciFloder = DateFloder + '\\' + str(PiciFloderIni).zfill(3)
        try:
            os.makedirs(PiciFloder)
            print('批次文件夹创建成功','批次号',PiciFloderIni)
        except Exception as EX:
            print('异常信息',EX)
    return PiciFloder

# 创建001、002 文件夹
# PiciFlag = shoujuanClear_b_G
def WriteCsv():
    #处理Csv文件
    csvpath = CreatFloder()
    print('+++',csvpath)
    Gongwei = 1
    NameOfCsv = DateOfFloder + 'FF03' + str(Gongwei).zfill(2) + str(PiciFloderIni).zfill(3)+'.csv'
    SavePath = csvpath + '\\' + NameOfCsv
    print('-----------',NameOfCsv)
    Inidata = {"BiaoPos": [10,20,30,40],"JiePos":[60,70,80,90]}
    savedata = pd.DataFrame(Inidata)
    savedata.to_csv(SavePath,encoding='UTF-8')

WriteCsv()