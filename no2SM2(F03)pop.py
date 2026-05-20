import csv
import datetime
import os
import re
import socket
import struct
import sys
import threading
import time
# from datetime import timedelta

import numpy as np
import pandas as pd
import pyqtgraph as pg
from pymodbus.client.sync import ModbusTcpClient
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import *
from pyqtgraph.Qt import QtCore, QtGui
from transitions.extensions import LockedMachine
from math import asin,acos,atan,sqrt,pi
from tkinter import filedialog
import tkinter as tk

from Ui_KnifeEdit import Ui_KnifeEdit
from Ui_NewUI import Ui_MainWindow
from Ui_peiFang import Ui_Form1
from flawDeal import Ui_DefectProcess
from shoujuanSet import Ui_ShouJuan

lock = threading.Lock()
_translate = QtCore.QCoreApplication.translate
# readPath = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
readPath = 'D:/no2Py'
flawPath = 'C:/Users/whscs/Desktop'
# print('readpath',readPath)
writePath = os.getcwd()
# writePath = 'D:/no2Py'
PLCfilepath = readPath + '/ModbusTCP.csv'
peifangPath = readPath + '/peifang.csv'
knifePath = readPath + '/KnifeFile.csv'
tempPath = readPath + '/tempData.csv'
chuandaiPath = readPath + '/chuandai.png'

flawFileFolderPath = flawPath + '\\SlitterCSVData'
flawPicFolderPath = flawPath + '\\SlitterCSVData'

# -------------------------
DataPath = 'D:\\FlawDataRec'  #保存缺陷数据的文件夹 绝对路径
PiciFloderIni = 0
# PiciFlag = 1
DateFloder = ''
# a = {1:[[3,4],[5]],2:[[],[7,8]],3:[[11,12,13],[]],4:[[22,33,44,55],[66,67,68,69,70]]}

def CreatFloder():
    global DateOfFloder,file_count,DateOfFloder,DateFloder
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

    # if PiciFlag:
    file_count = 0

    try:
        for file in os.walk(DateFloder):
            file_count = file_count + 1
        print('批次个数',file_count)
        PiciFloder = DateFloder + '\\' + str(file_count).zfill(3)
        os.makedirs(PiciFloder)
    except Exception as EX:
        print('异常信息',EX)
    return PiciFloder

# 创建001、002 文件夹
# PiciFlag = shoujuanClear_b_G
def WriteCsv():
    global file_count,DateOfFloder,DateFloder
    #处理Csv文件
    csvpath = CreatFloder()
    # api.shoujuanFlawInfo = {1:[[3,4],[5]],2:[[],[7,8]],3:[[11,12,13],[]],4:[[22,33,44,55],[66,67,68,69,70]]}
    for k in api.shoujuanFlawInfo.keys():#k是工位编号
        NameOfCsv = DateOfFloder + 'FF03' + str(k).zfill(2) + str(file_count).zfill(3)+'.csv'
        SavePath = csvpath + '\\' + NameOfCsv
        writeData = {}
        writeData['贴胶'] = api.shoujuanFlawInfo[k][0]
        writeData['接带'] = api.shoujuanFlawInfo[k][1]
        gongweiFlaw = pd.DataFrame()
        for j in writeData.keys():
            gongweiFlaw = pd.concat([gongweiFlaw,pd.DataFrame({j:writeData[j]})],axis=1)
        gongweiFlaw.loc[-1]=['sum:'+str(len(api.shoujuanFlawInfo[k][0])),'sum:'+str(len(api.shoujuanFlawInfo[k][1]))]
        # print(gongweiFlaw)
        gongweiFlaw.to_csv(SavePath,encoding='UTF_8_sig',mode='w',index=None)
    todayTotalPath = DateFloder + ('\\{}TotalFlaws.csv'.format(DateOfFloder))
    totalWriter = [['{}缺陷'.format(str(file_count).zfill(3))],['{}接头'.format(str(file_count).zfill(3))]]
    juannums = 0
    for i in range(1,len(api.shoujuanWidths)-1):
        if api.shoujuanWidths[i] > 0:
            juannums += 1
        else:
            break
    for i in range(1,juannums+1):
        if (i not in api.shoujuanFlawInfo.keys()):
            api.shoujuanFlawInfo[i] = [[],[]]
    for i in range(1,len(api.shoujuanFlawInfo)+1):
        # print('za huishi a',api.shoujuanFlawInfo)
        totalWriter[0].append(len(api.shoujuanFlawInfo[i][0]))
        totalWriter[1].append(len(api.shoujuanFlawInfo[i][1]))  
    if os.path.exists(todayTotalPath):
        f7 = open(todayTotalPath,'a+',newline='')
        csv.writer(f7).writerows(totalWriter)
    else:
        f7 = open(todayTotalPath,'a+',newline='')
        head = ['']
        for i in range(1,31):
            head.append('{}卷位'.format(i))
        csv.writer(f7).writerow(head)
        csv.writer(f7).writerows(totalWriter)
    f7.close()

    

# -------------------------

# def sendLastStop():         #发送预设停机米长之前最后一个停机位置
#     if len(api.stopStack) > 0:
#         if api.lengthSet > api.stopStack[0][1]:
#             client.write_registers (values=inverse(api.stopStack[0][1]), unit=2, address=306, data_format='!f')
#             print('ting zhe li',api.stopStack[0][1],api.lengthSet)
#         elif api.lengthSet <= api.stopStack[-1][1]:
#             client.write_registers (values=inverse(api.stopStack[-1][1]), unit=2, address=306, data_format='!f')
#             print('ting zhe li',api.stopStack[-1][1],api.lengthSet)
#         else:
#             for i in range(len(api.stopStack)-1):
#                 if (api.stopStack[i][1] >= api.lengthSet) & (api.stopStack[i+1][1] < api.lengthSet):
#                     client.write_registers (values=inverse(api.stopStack[i+1][1]), unit=2, address=306, data_format='!f')
#                     print('ting zhe li',api.stopStack[i][1],api.lengthSet)


def updateFlawFile(path):       #从指定文件夹获取最新的文件
    lists = os.listdir(path)
    lists.sort(key=lambda x:os.path.getmtime(path +'\\'+x))
    #把目录和文件名合成一个路径
    # print(lists)
    file_new = os.path.join(path,lists[-1])
    return file_new

def microTimer(t):      #毫秒定时器，t单位为毫秒
    start,end = 0,0
    start = time.time()
    # print(start)
    t = t/1000
    while end-start<t:
        end = time.time()
    # print(end-start)

def receive():
    global receive_count
    # for i in range(100):
    # if receive_count+9 >= length_data:
    #     receive_count = 0
    # for i in range(9):
    receive_count = api.receive_count+1
    if receive_count >= 1000:
        receive_count = 0
    api.containerData1.pop(0)
    api.containerData2.pop(0)
    api.containerData3.pop(0)
    api.containerData4.pop(0)
    api.containerData5.pop(0)
    api.containerData6.pop(0)

    api.containerData1.append(api.speedNow)
    api.containerData2.append(api.fangjuanActFUp)
    api.containerData3.append(api.fangjuanRUp)
    api.containerData4.append(api.lengthAct)
    api.containerData5.append(api.fangjuanActFDown)
    api.containerData6.append(api.fangjuanRDown)
    # 以下6行是测试用的数据，实际使用要注释掉
    # containerData1.append(data[receive_count][3])
    # containerData2.append(data[receive_count][0])
    # containerData3.append(data[receive_count][1])
    # containerData4.append(data[receive_count][2])
    # containerData5.append(data[receive_count][4])
    # containerData6.append(data[receive_count][5])

    # Timer(0.1,receive).start()


def dec_to_float(H,L):                #十进制转浮点数(从PLC读数据)
    if (H==24576) & ((L==48618)|(L==15850)):
        return(0)
    else:        
        A = str(hex(H).replace('0x','').zfill(4))
        B = str(hex(L).replace('0x','').zfill(4))
        s = B+A
        try:
            ret = struct.unpack('!f',bytes.fromhex(s))[0]
            return(ret)
        except Exception:
            print('Exception occurs:','H:',H,'L:',L,'A:',A,'B:',B)
            return 0


def inverse(a):                       #调换高低位(向PLC发数据)
    a0 = struct.pack('>f', float(a)).hex()
    a1 = a0[0:4]
    a2 = a0[4:8]
    return [int(a2,16),int(a1,16)]


def binlist_to_int(a):                #二进制数组转整数
    t = 0
    for i in range(len(a)):
        t = t + a[i]*(2**i)
    return(t)


def dec_to_binlist(a, t):             #十进制a转t位二进制
    ret = []
    for i in range(t):
        ret.append(a%2)
        a = a // 2
    # ret.reverse()
    return(ret)


def get_addr(name):                   #获取数据的地址
    with open(PLCfilepath, newline='', encoding='GBK') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 1:
                if row[1] == name:
                    return(int(row[7])-1)


def send_data_to_PLC():               #向PLC发送数 
    pass
    if api.uiEA:
        client.write_registers (values=inverse(api.SpeedLmitHigh)+ inverse(api.SpeedLmitLow)+ inverse(api.lengthSet)+ inverse(api.xintong_widthUp)+
                                        inverse(api.fangjuanFSetUp)+ inverse(api.Mo_WidthUp)+ inverse(api.Mo_thickUp)+ inverse(api.xintongTypeUp)+
                                        inverse(api.moTypeUp)+ inverse(api.xintong_widthDown)+ inverse(api.fangjuanFSetDown)+ inverse(api.Mo_WidthDown)+
                                        inverse(api.Mo_thickDown)+ inverse(api.xintongTypeDown)+inverse(api.moTypeDown)+inverse(api.Accelerate_time)+
                                        inverse(api.Slow_time)+ inverse(api.Stop_time), unit=2, address=28, data_format='!f')
        client.write_registers (values=inverse(api.xintongSizeUp) + inverse(api.xintongSizeDown) + inverse(api.didaoDingWei) + inverse(api.Meters_Stop), unit=2, address=98, data_format='!f')
        client.write_registers (values=inverse(api.speedJog), unit=2, address=110, data_format='!f')
        client.write_registers (values=inverse(api.tongkuanDown) + inverse(api.tongkuanUp), unit=2, address=138, data_format='!f')
        if api.MXlist[5][2]:
            client.write_registers (values=inverse(api.flawNums[api.badPoint]) + inverse(api.Amount_LeftFlaw) + inverse(api.Meters_NextFlaw), unit=2, address=188, data_format='!f')
        client.write_registers (values=inverse(api.shoujuanFSetUp) + inverse(api.shoujuanFSetDown) + inverse(api.zhuiduUp) + inverse(api.zhuiduDown), unit=2, address=416, data_format='!f')
        client.write_registers (values=inverse(api.targetUp) + inverse(api.targetDown) + inverse(api.circlesUp) + inverse(api.circlesDown), unit=2, address=444, data_format='!f')
    

def judgeNum():                       #数字判断
    global msagint
    global lastmsag
    msagint2 = msagint[:]
    # print('now',msagint2)
    lastmsag2 = lastmsag[:]
    # print('last',lastmsag2)
    s=api.ordertype                   #当确定识别顺序为升序后，给定s的值为1

    laststr = str(lastmsag2[1]+lastmsag2[2]+lastmsag2[3]+lastmsag2[4])
    lastnum = int(laststr.replace(' ',''))
    nowstr = str(msagint2[1]+msagint2[2]+msagint2[3]+msagint2[4])
    nownum = int(nowstr.replace(' ',''))
    deltaL = abs(msagint2[20]-lastmsag2[20])

    numpredict = int(lastnum + s*(deltaL//api.deltaP)*api.deltaP) if (deltaL%api.deltaP < (api.deltaP/2)) else int(lastnum + s*(deltaL//api.deltaP + 1)*api.deltaP) #预测这个标应为多少
    prestr = str(numpredict).zfill(4)

    # print(msagint2[18],lastmsag2[18],'delta',deltaL,laststr,nowstr,'pre:',prestr,(nownum-lastnum)*s*(api.deltaP*0.7),(nownum-lastnum)*s*(api.deltaP*1.3))
        
    # if (deltaL > ((nownum-lastnum)*s*(api.deltaP*0.6)))&(deltaL < ((nownum-lastnum)*s*(api.deltaP*1.4))):                 #米长符合
    if ((abs(msagint[5] - msagint[6]) >= 40) & (abs(msagint[5] - msagint[6]) <= 60)) & \
        ((abs(msagint[8] - msagint[9]) >= 8) & (abs(msagint[8] - msagint[9]) <= 50)) & \
        ((abs(msagint[10] - msagint[11]) >= 8) & (abs(msagint[10] - msagint[11]) <= 50)) & \
        ((abs(msagint[12] - msagint[13]) >= 8) & (abs(msagint[12] - msagint[13]) <= 50)) & \
        ((abs(msagint[14] - msagint[15]) >= 8) & (abs(msagint[14] - msagint[15]) <= 50)):

        numpredict = int(lastnum + s*(deltaL//api.deltaP)*api.deltaP) if (deltaL%api.deltaP < (api.deltaP/2)) else int(lastnum + s*(deltaL//api.deltaP + 1)*api.deltaP) #预测这个标应为多少
        prestr = str(numpredict).zfill(4)
        # print('预测标码：',prestr)

        if nownum != lastnum:
            # print('nowstr:',nowstr)5
            # print('predict:',prestr)
            if nowstr.replace(' ','') == prestr:
                # print('nowstr:',nowstr)
                # print('predict:',prestr)
                return('correct')
            else:
                return('Error')
        else:
            return('Error')
    else:
        return('Error')


def dataDeal(opendata):               #x42有数字再调用
    firstLen = api.oriLength
    deltaLen = firstLen%5

    TrainSample = pd.DataFrame()
    TrainSample['LenSum'] = ''
    TrainSample['CharWidth'] = ' '
    TrainSample['Gradient'] = ' '
    TrainSample['CharLen'] = ' '
    result = divmod(api.fangjuanL-deltaLen,5)     #获取米长的商和余数 判断条件1
    charWidth = abs(opendata[7]-opendata[6])      #X42-X14  字体宽度判断条件2
    gradient  = abs(opendata[7]-opendata[5])      #X42-X11  字体倾斜程度 判断条件3
    charLen1st = abs(opendata[8]-opendata[9])     #Y11-Y12  第1个字符长度 判断条件4
    charLen2rd = abs(opendata[14]-opendata[15])   #Y41-Y42  第4个字符长度 判断条件4    

    if  (result[1] >4) or (result[1]) == 0:
        TrainSample.loc[0,'LenSum'] = 1
    else:
        TrainSample.loc[0,'LenSum'] = 0
    #处理倾斜度
    if gradient <= 10:
        TrainSample.loc[0,'Gradient'] = 1
    else:
        TrainSample.loc[0,'Gradient'] = 0
    #处理第1第4个字的长度
    if  (charLen1st >= 5) & (charLen2rd >= 5):
        TrainSample.loc[0,'CharLen'] = 1
    else:
        TrainSample.loc[0,'CharLen'] = 0
    #处理字体宽度
    if charWidth < 30:
        TrainSample.loc[0,'CharWidth'] = 1
    else:
        TrainSample.loc[0,'CharWidth'] = 0
    return TrainSample


def makeDecision(flawFileName):       #生成决策表
    api.badMetersDone = []
    vHigh = (100/60) if api.SpeedLmitHigh == 0 else (api.SpeedLmitHigh/60)            # 设定高速运行的速度值，单位m/s
    vLow = (50/60) if api.SpeedLmitLow == 0 else (api.SpeedLmitLow/60)                # 设定低速运行的速度值，单位m/s
    tUp = 5 if api.Accelerate_time == 0 else api.Accelerate_time                     # 设定升速时间，单位s
    tDown = 5 if api.Slow_time == 0 else api.Slow_time                    # 设定降速时间，单位s
    api.aUp = vHigh / tUp           # 计算升速的加速度
    api.aDown = vHigh / tDown       # 计算降速的加速度
    # xHUp = vHigh**2 / (2*api.aUp)   # 计算速度从0升到高速走过的距离
    # xLUp = vLow**2 / (2*api.aUp)    # 计算速度从0升到低速走过的距离
    # xHDown = (vHigh**2 - vLow**2) / (2*api.aDown)   # 计算速度从高速降到低速走过的距离
    # xLDown = vLow**2 / (2*api.aDown)                # 计算速度从低速降到0走过的距离
    badMetersFilepath = flawFileName
    global badMetersdata,oriXlist
    badMetersdata = pd.read_csv(badMetersFilepath,encoding='GBK',header=None)
    api.flawNums = badMetersdata[0].values.tolist()
    api.badMeters = badMetersdata[4].values.tolist()
    api.badMetersX = badMetersdata[3].values.tolist()
    api.badPics = badMetersdata[6].values.tolist()
    api.zhengfan = badMetersdata[5].values.tolist()
    oriXlist = api.badMetersX[:]
    
    # api.zhengfan.insert(0,0)
    api.badMetersDone = []
    for i in range(len(api.badMeters)):
        api.flawNums[i] = int(api.flawNums[i])
        api.badMeters[i] = float(api.badMeters[i])/1000
        api.badMetersX[i] = float(api.badMetersX[i]) + api.offsetX
        api.zhengfan[i] = int(api.zhengfan[i])
        api.findPoint[api.flawNums[i]] = i
        if api.biaoliInverseFlag:
            api.zhengfan[i] = 1-api.zhengfan[i]
            if api.cutPPorNY == 0:  #表里反了，切PP面
                api.badMetersX[i] = api.Mo_WidthDown - api.badMetersX[i]
        else:
            if api.cutPPorNY == 1:  #表里没反，切NY面
                api.badMetersX[i] = api.Mo_WidthDown - api.badMetersX[i]

        if api.zhengfan[i] >= 1:
            api.badMeters[i] -= (api.offsetNY/1000)
        elif api.zhengfan[i] == 0:
            api.badMeters[i] -= (api.offsetPP/1000)
            

        # if api.zhengfan[i] == '正面':
        #     api.zhengfan[i] = 1
        # elif api.zhengfan[i] == '反面':
        #     api.zhengfan[i] = 0
    # api.badMeters = [0.6, 5.6, 15.7, 30.75, 43.2]       # 缺陷位置示例，单位m
    # print('bad points:', api.badMeters)

    # pos = []                    # 记录要做动作的位置
    # act = []                    # 记录要做的动作，1加速，0减速
    # tar = []                    # 记录做出这一动作的目标速度是多少，单位m/s
    # ————————————生成决策表————————————
    # api.badMeters.insert(0,0)
    # api.badMetersX.insert(0,0)
    # for i in range(1,len(api.badMeters)):
    #     if api.zhengfan[i] == 1:
    #         api.badMeters[i] -= (api.offsetNY/1000)
    #     elif api.zhengfan[i] == 0:
    #         api.badMeters[i] -= (api.offsetPP/1000)

    api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
    # api.jiedaiNow = (api.fangjuanL - api.lengthDelta - api.LJiedai)
    # print('delta',api.lengthDelta,api.jiedaiNow)

    # for i in range(len(api.badMeters)-1):
    #     if api.jiedaiNow <= 0:
    #         api.badPoint = 1
    #         break
    #     # print(api.jiedaiNow, api.badMeters[i], api.badMeters[i+1])
    #     if (api.jiedaiNow >= (api.badMeters[i])) & (api.jiedaiNow < api.badMeters[i+1]):    #当前位置在两个缺陷之间
    #         # print('camera',api.LCamera)
    #         api.badPoint = i+1      #缺陷编号
    #         print('flaw num:',api.badPoint)
    #         break
    # if api.MXlist[1][11] & (api.lengthAct <= api.Meters_NextFlaw) & (abs(api.lengthAct-api.Meters_NextFlaw)<=0.5):
    #     api.badPoint += 1
    # if api.badPoint >= len(api.badMeters):
    #     api.badPoint = len(api.badMeters)-1
    # api.Meters_NextFlaw = (api.badMeters[api.badPoint] + api.lengthDelta + api.LJiedai)  #缺陷位置米数
    # if api.Meters_NextFlaw <= 0:
    #     api.Meters_NextFlaw = api.badMeters[api.badPoint]
    # api.Amount_LeftFlaw = len(api.badMeters)-api.badPoint   #剩余缺陷数量
    # if api.badPoint == len(api.badMeters)-1:
    #     api.Amount_LeftFlaw = 0
    # client.write_registers (values=inverse(api.badPoint) + inverse(api.Amount_LeftFlaw) + inverse(api.Meters_NextFlaw), unit=2, address=188, data_format='!f')
    # client.write_coils(50,[api.zhengfan[api.badPoint]])

    # return([pos,act,tar])

def renewTargetsInStack():            #对栈内所有目标停机位置刷新一次
    if api.cutPPorNY == 0:       #切PP面
        x1x2 = sqrt(api.yagunBackUp*(api.yagunBackUp + 2*(api.houshoujuanR + 60)))/1000
        x3x4 = sqrt(6972.25 + (267.5 - api.yagunBackUp)**2 - 14400)/1000
        alpha = pi - acos((api.houshoujuanR + 60)/(api.yagunBackUp + api.houshoujuanR + 60)) \
                    - atan(x3x4/120) - atan(83.5/(267.5 - api.yagunBackUp))
        x5 = 60 * alpha / 1000
        beta = asin((api.houshoujuanR + 60)/(api.yagunBackUp + api.houshoujuanR + 60))
        x6 = api.houshoujuanR * (beta + pi/3) / 1000
        xleft = x1x2 + x3x4 + x5 + x6
        api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
        api.cam2knife = [[7.65229+api.offsetPPUp/1000,7.94342+api.offsetPPDown/1000],[7.65229-0.0978+api.offsetPPUp/1000,7.94342-0.0978+api.offsetPPDown/1000]]  # [[上相机到切刀后上收卷停机,上相机到切刀后下收卷停机],[下相机到切刀后上收卷停机,下相机到切刀后下收卷停机]]
        api.cam2wind1 = [[8.37763+api.offsetNYUp/1000,8.26452+api.offsetNYDown/1000],[8.37763-0.0978+api.offsetNYUp/1000,8.26452-0.0978+api.offsetNYDown/1000]]  # [[上相机到上收卷之前，上相机到下收卷之前],[下相机到上收卷之前，下相机到下收卷之前]]

        for item in api.stopStack:        #刷新公式：停机位置=收卷长度+目标到相机的绝对距离 + 升降序标志 x（瑕疵位置-相机米长）
            if item[0] != 0:
                p = api.findPoint[item[0]]
                if (item[2] == 0) | (item[2] == 1):     #第一、第二观察区
                    item[1] = api.lengthAct + api.cam2view[api.cameraPos][item[2]] + api.ordertype*(api.badMeters[p] - api.LCamera)
                elif (item[2] == 2) | (item[2] == 3):   #上轴 下轴贴标区
                    item[1] = api.lengthAct + api.cam2knife[api.cameraPos][item[2]-2] + api.ordertype*(api.badMeters[p] - api.LCamera)
                elif (item[2] == 4) | (item[2] == 5):   #上收卷、下收卷
                    item[1] = api.lengthAct + api.cam2wind1[api.cameraPos][item[2]-4] + xleft + api.ordertype*(api.badMeters[p] - api.LCamera)
    
    elif api.cutPPorNY == 1:       #切NY面
        x1x2 = sqrt(88542.5476 - (api.houshoujuanR + 60)**2)/1000
        beta = asin((api.houshoujuanR + 60)/297.561)
        x6 = api.houshoujuanR*(beta + pi/2)/1000
        xleft = x1x2 + x6 + 0.05268
        api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
        api.cam2knife = [[8.59438+api.offsetPPUp/1000,8.48128+api.offsetPPDown/1000],[8.59438-0.0978+api.offsetPPUp/1000,8.48128-0.0978+api.offsetPPDown/1000]]  # [[上相机到切刀后上收卷停机,上相机到切刀后下收卷停机],[下相机到切刀后上收卷停机,下相机到切刀后下收卷停机]]
        api.cam2wind1 = [[8.37763+api.offsetNYUp/1000,8.26452+api.offsetNYDown/1000],[8.37763-0.0978+api.offsetNYUp/1000,8.26452-0.0978+api.offsetNYDown/1000]]  # [[上相机到上收卷之前，上相机到下收卷之前],[下相机到上收卷之前，下相机到下收卷之前]]
        offsetNY = [api.offsetNYUp/1000,api.offsetNYDown/1000]

        for item in api.stopStack:        #刷新公式：停机位置=收卷长度+目标到相机的绝对距离 + 升降序标志 x（瑕疵位置-相机米长）
            if item[0] != 0:
                p = api.findPoint[item[0]]
                if (item[2] == 0) | (item[2] == 1):     #第一、第二观察区
                    item[1] = api.lengthAct + api.cam2view[api.cameraPos][item[2]] + api.ordertype*(api.badMeters[p] - api.LCamera)
                elif (item[2] == 2) | (item[2] == 3):   #上轴 下轴贴标区
                    item[1] = api.lengthAct + api.cam2knife[api.cameraPos][item[2]-2] + api.ordertype*(api.badMeters[p] - api.LCamera)
                elif (item[2] == 4) | (item[2] == 5):   #上收卷、下收卷
                    item[1] = api.lengthAct + api.cam2knife[api.cameraPos][item[2]-4] + xleft + api.ordertype*(api.badMeters[p] - api.LCamera) + offsetNY[item[2]-4]

    print('cam now',api.LCamera)
    api.stopStack.sort(key = lambda x:x[1], reverse = True)
    print('stack now:',api.stopStack)

    f = open(readPath + '\\stopStack.csv', 'w', newline='')
    csv.writer(f).writerows(api.stopStack)
    f.close()
    # 刀具文件保存放在这里
    try:
        daoData = pd.read_csv(knifePath,encoding='GBK',index_col=0)
        for i in api.daoRecs.keys():
            daoData.loc[i,'运行米长'] = api.daoRecs[i]
        daoData.to_csv(knifePath,encoding='GBK',index=True,header=True)
        dfdf = pd.DataFrame(columns=api.knifeUsing,index=None)
        dfdf.loc[1] = api.knifeEA
        dfdf.to_csv(readPath + '\\knifeUsing.csv',index=False)
    except Exception as e:
        print(e)

def calShoujuanPos(view,target):        #计算当前贴标或接带在收卷处的长度
    x1x2 = sqrt(api.yagunBackUp*(api.yagunBackUp + 2*(api.houshoujuanR + 60)))/1000
    x3x4 = sqrt(6972.25 + (267.5 - api.yagunBackUp)**2 - 14400)/1000
    alpha = pi - acos((api.houshoujuanR + 60)/(api.yagunBackUp + api.houshoujuanR + 60)) \
                - atan(x3x4/120) - atan(83.5/(267.5 - api.yagunBackUp))
    x5 = 60 * alpha / 1000
    beta = asin((api.houshoujuanR + 60)/(api.yagunBackUp + api.houshoujuanR + 60))
    x6 = api.houshoujuanR * (beta + pi/3) / 1000
    xleft = x1x2 + x3x4 + x5 + x6
    api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
    
    if view != -1:
        dist = api.fangjuanL + api.cam2wind1[0][target] - api.cam2view[0][view] + xleft
    elif view == -1:
        dist = api.fangjuanL + api.cam2wind1[0][target] - api.cam2view[0][0] + xleft - 0.5039
    return dist


def saveTempData():                   #保存临时数据
    if api.cutPPorNY == 0:     #切PP面
        api.stopTypeNames = ['第二观察区','第一观察区','PP面上轴贴标区','PP面下轴贴标区','上收卷','下收卷','预设长度停机']
        api.cam2view = [[3.11819,1.11167],[3.11819-0.0978,1.11167-0.0978,]]   # [[上相机到第二观察区,上相机到第一观察区]],[下相机到第二观察区,下相机到第一观察区]]
        api.cam2knife = [[7.65229+api.offsetPPUp/1000,7.94342+api.offsetPPDown/1000],[7.65229-0.0978+api.offsetPPUp/1000,7.94342-0.0978+api.offsetPPDown/1000]]  # [[上相机到切刀后上收卷停机,上相机到切刀后下收卷停机],[下相机到切刀后上收卷停机,下相机到切刀后下收卷停机]]
        api.cam2wind1 = [[8.37763+api.offsetNYUp/1000,8.26452+api.offsetNYDown/1000],[8.37763-0.0978+api.offsetNYUp/1000,8.26452-0.0978+api.offsetNYDown/1000]]  # [[上相机到上收卷之前，上相机到下收卷之前],[下相机到上收卷之前，下相机到下收卷之前]]
    elif api.cutPPorNY == 1:     #切NY面
        api.stopTypeNames = ['第一观察区','第二观察区','PP面上轴贴标区','PP面下轴贴标区','上收卷','下收卷','预设长度停机']
        api.cam2view = [[1.11167,3.11819],[1.11167-0.0978,3.11819-0.0978,]]   # [[上相机到第一观察区,上相机到第二观察区]],[下相机到第一观察区,下相机到第二观察区]]
        api.cam2knife = [[8.59438+api.offsetPPUp/1000,8.48128+api.offsetPPDown/1000],[8.59438-0.0978+api.offsetPPUp/1000,8.48128-0.0978+api.offsetPPDown/1000]]  # [[上相机到切刀后上收卷停机,上相机到切刀后下收卷停机],[下相机到切刀后上收卷停机,下相机到切刀后下收卷停机]]
        api.cam2wind1 = [[8.37763+api.offsetNYUp/1000,8.26452+api.offsetNYDown/1000],[8.37763-0.0978+api.offsetNYUp/1000,8.26452-0.0978+api.offsetNYDown/1000]]  # [[上相机到上收卷之前，上相机到下收卷之前],[下相机到上收卷之前，下相机到下收卷之前]]
        
    renew = pd.DataFrame([{'lastNum':api.numNow, 'lengthDelta':api.lengthDelta, 'ordertype':api.ordertype, \
                            'cameraPos':api.cameraPos, 'biaoliInverseFlag':api.biaoliInverseFlag, \
                                'offsetNY':api.offsetNY,'offsetPP':api.offsetPP,'offsetPPUp':api.offsetPPUp, \
                                    'offsetPPDown':api.offsetPPDown,'offsetX':api.offsetX,'lastPeiFangNum':api.lastPeiFangNum, \
                                        'knifeAlarmSet':api.knifeAlarmSet,'cutPPorNY':api.cutPPorNY, \
                                            'offsetNYUp':api.offsetNYUp,'offsetNYDown':api.offsetNYDown}])
    renew.to_csv(tempPath,mode='w',index=False,header=True)

class NaiveBeyes:                     #朴素贝叶斯类
    def  __init__(self):
        self.model = {}
    
    def fit(self,Xtrain,Ytrain = pd.Series()):
        if not Ytrain.empty:
            Xtrain = pd.concat([Xtrain, Ytrain], axis=1)
        self.model = self.buildNaiveBayes(Xtrain) 
        return self.model

    def buildNaiveBayes(self,Xtrain):
        Ytrain = Xtrain.iloc[:,-1]
        # Ytrain = Xtrain.loc[:,'CoE']
        a = len(Ytrain)
        # print(a)
        # print(type(Ytrain))
        yCounts = Ytrain.value_counts()
        yCounts = yCounts.apply(lambda x: (x+1)/(yCounts.size+a)) #拉普拉斯平滑，防止出现新特性使P=0
        
        #完成了对按键数量的统计
        retModel = {}
        for nameClass,val in yCounts.items():
            retModel[nameClass] = {'pClass':val,'pFeature':{}}   #对按键操作完毕
        
        #统计特性
        propNameAll = Xtrain.columns[:-1]          #返回列名 米长、速度差、面积
        allPropByFeature = {}
        for nameFeature in propNameAll:
            allPropByFeature[nameFeature] = list(Xtrain[nameFeature].value_counts().index)
        # print(allPropByFeature)
        for nameClass,group in Xtrain.groupby(Xtrain.columns[-1]):       #最后一列CoE
            for nameFeature in propNameAll:
                eachClassPFeature = {}
                propData = group[nameFeature]
                propClassSummary = propData.value_counts()
                
                for propName in allPropByFeature[nameFeature]:
                    if not propClassSummary.get(propName):
                        propClassSummary[propName] = 0
                Ni = len(allPropByFeature[nameFeature])
                propClassSummary = propClassSummary.apply(lambda x:(x+1)/(propData.size+Ni))
                for nameFeatureProp,valp in propClassSummary.items():
                        eachClassPFeature[nameFeatureProp] = valp
                retModel[nameClass]['pFeature'][nameFeature] = eachClassPFeature
        return retModel

    def prediceNaiveBayes(self,data):
        curMaxrate = None
        curClassSelect = None
        for nameClass , infoModel in self.model.items ():
            rate = 0
            rate += np.log(infoModel['pClass'])
            PFeature = infoModel['pFeature']

            for nameFeature , val in data.items():
                propsRate = PFeature.get(nameFeature)
                if not propsRate:
                    continue
                rate += np.log(propsRate.get(val,0))
            
            if curMaxrate == None or rate > curMaxrate:
                curMaxrate = rate
                curClassSelect = nameClass
        return curClassSelect
    
    def predict(self,data):
        if isinstance(data,pd.Series):
            return self.prediceNaiveBayes(data)
        # return data.apply(lambda d:self.prediceNaiveBayes(d),axis=1)
        asd = list(data.apply(lambda d:self.prediceNaiveBayes(d),axis=1))
        return asd[0]


class photoThread (threading.Thread):      #采集图像类
    def __init__(self, threadID, name, stopflag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stop = stopflag

        tempData = pd.read_csv(tempPath)
        api.numNow = str(int(tempData['lastNum'][0])).zfill(4)
        api.lengthDelta = float(tempData['lengthDelta'][0])
        api.ordertype = int(tempData['ordertype'][0])
        api.cameraPos = int(tempData['cameraPos'][0])
        api.biaoliInverseFlag = int(tempData['biaoliInverseFlag'][0])

    def close(self):
        self.stop = 1

    def run(self):
        # in_data = pd.read_csv("TrainingSample.csv",encoding='utf-8')
        # target_host = "192.168.1.113"
        # target_port = 8500
        # global client2
        # #建立socket对象
        # client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # #连接客户端
        # print('111111')
        # client2.connect((target_host,target_port))

        # naivebayes = NaiveBeyes()
        # naivebayes.fit(in_data)
        firstpush = True
        tt = 16
        global lastmsag
        global msagint
        
        lastmsag = []
        sparelast = []
        for i in range(tt+7):
            lastmsag.append(0)
            sparelast.append(0)

        speedBound = 80             #字符识别和面积检测的速度界限
        timeNow = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        path = readPath + '\\CameraData\\' + timeNow + 'CameraData.csv' 
        #f = open(path,'a+',newline='')
        with open(path, 'a+', newline='') as f:
            titles = ['Index', 'StartLine', '1', '2', '3', '4','X11','X14','X42','Y11','Y12','Y21','Y22','Y31','Y32','Y41','Y42','Judgement','Speed','LengthSum','jogSpeed','fangjuanL','stopStack','Time']
            total = 0
            if os.path.getsize(path) == 0:
                csv.writer(f).writerow(titles)
                total = 1
            else:
                total = len(open(path).readlines())
            
            msagint = []
            arealast = 1
            api.pointscount = 0
            lastx = 0
            for i in range(tt+7):
                msagint.append(0)
            last_mode = api.modetype
            while True:
                # print('yunxing moshi ',api.modetype)
                lines = []
                if (api.modetype == 1) & (api.speedNow > speedBound):              #速度超过界限时切换到面积检测
                    api.modetype = 0
                    if api.modetype != last_mode:       #如果运行模式要切换了就发送指令
                        mode0 = 'MW,#L0002,{0}'.format(1-api.modetype)
                        mode0 = bytes(mode0+'\r',encoding='utf-8')
                        client2.send(mode0)
                    last_mode = api.modetype
                elif (api.modetype == 0) & (api.speedNow <= speedBound):           #速度降到界限时切换到字符识别
                    api.modetype = 1
                    if api.modetype != last_mode:       #如果运行模式要切换了就发送指令
                        mode0 = 'MW,#L0002,{0}'.format(1-api.modetype)
                        mode0 = bytes(mode0+'\r',encoding='utf-8')
                        client2.send(mode0)
                    last_mode = api.modetype

                for j in range(50):
                    if api.modetype == 0:       #面积检测
                        msg = 'MR,#L0000[16],#L0000[0]'
                        msg = bytes(msg+'\r',encoding="utf-8")
                        client2.send(msg)
                        msag = client2.recv(4096).decode('utf-8')
                        msag = msag.split(',')
                        try:
                            xLable = float(re.findall(r"\d+\.?\d*", msag[2])[0]) 
                        except Exception:
                            xLable = 0         
                        api.pointscount = int(float(api.numNow))/api.deltaP
                        try:
                            areanow = int(msag[1][10]) 
                        except Exception:
                            areanow = 1
                        if (arealast == 1)&(areanow == 0):                      #出现面积符合的下降沿
                            if lastx == 0:                                      #第一个标，计数+1，更新上一个标的米数
                                api.pointscount = api.pointscount + api.ordertype*1
                                print('point1',str(int(api.pointscount*api.deltaP)).zfill(4))
                                lastx = api.fangjuanL
                                api.numNow = str(int(api.pointscount*api.deltaP)).zfill(4)
                                api.LCamera = int(float(api.numNow)) - api.ordertype*(api.LView/2 - api.LView*float(msagint[0])/api.pixX - api.timeDelay*api.speedNow/60)
                                api.lengthDelta = msagint[tt+4] - api.ordertype*api.LCamera
                            else:
                                deltax = abs(api.fangjuanL - lastx)                 #与上一个标的距离
                                if deltax >= (api.deltaP*2/3):                  #距离大于标志间距的2/3才可能是正确的标
                                    if deltax%api.deltaP >= (api.deltaP/2):
                                        e = api.deltaP*(deltax//api.deltaP+1)-deltax
                                    else:
                                        e = deltax-api.deltaP*(deltax//api.deltaP)
                                    if abs(e) <= 0.4*api.deltaP:                             #两个标的距离与附近的5的倍数之间的差值(用来判断当前面积是阴影还是真的标)
                                        if deltax%api.deltaP >= (api.deltaP/2):
                                            api.pointscount = api.pointscount + api.ordertype*(round(deltax)//api.deltaP)    #中间漏掉的点可以补回来
                                            api.numNow = str(int(api.pointscount*api.deltaP)).zfill(4)
                                            api.LCamera = int(float(api.numNow)) - api.ordertype*(api.LView/2 - api.LView*float(msagint[0])/api.pixX - api.timeDelay*api.speedNow/60)
                                            api.lengthDelta = msagint[tt+4] - api.ordertype*api.LCamera
                                            print('point2',str(int(api.pointscount*api.deltaP)).zfill(4))
                                        else:
                                            api.pointscount = api.pointscount + api.ordertype*(round(deltax)//api.deltaP)
                                            api.numNow = str(int(api.pointscount*api.deltaP)).zfill(4)
                                            api.LCamera = int(float(api.numNow)) - api.ordertype*(api.LView/2 - api.LView*float(msagint[0])/api.pixX - api.timeDelay*api.speedNow/60)
                                            api.lengthDelta = msagint[tt+4] - api.ordertype*api.LCamera
                                            print('point3',str(int(api.pointscount*api.deltaP)).zfill(4))
                                        lastx = api.fangjuanL
                        arealast = areanow
                        # api.numNow = str(int(api.pointscount*api.deltaP)).zfill(4)
                    
                    elif api.modetype == 1:     #字符识别
                        msg = 'MR'
                        msagint = []
                        for i in range(tt):
                            msg += ',#L0000[' + str(i) + ']'
                        for i in range(tt+7):
                            msagint.append(0)
                        # qq = (time.time())
                        msg = bytes(msg+'\r',encoding="utf-8")
                        try:
                            client2.send(msg)
                            msag = client2.recv(4096).decode('utf-8')
                        except ConnectionResetError:
                            time.sleep(2)
                            print('try again')
                            break
                        msag = msag.split(',')
                        # print(msag)
                        msagint[tt+1] = api.speedNow
                        api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
                        msagint[tt+2] = api.lengthAct
                        msagint[tt+3] = api.speedJog
                        msagint[tt+4] = api.fangjuanL
                        # print('length',api.lengthAct,api.LCamera)
                        
                        if len(msag)>=tt:
                            for i in range(tt):
                                if i == 0:
                                    # msagint[i] = int(msag[i+1][10])
                                    msagint[i] = float(re.findall(r"\d+\.?\d*", msag[i+1])[0])
                                elif (i > 0)&(i <= 4):
                                    msagint[i] = int(msag[i+1][9]+msag[i+1][10])
                                    msagint[i] = chr(msagint[i])
                                elif i > 4:
                                    msagint[i] = float(re.findall(r"\d+\.?\d*", msag[i+1])[0])
                        # print(msagint)
                        if firstpush:
                            f3 = open(readPath + '\\camTemp.csv','r',newline='')
                            firstpush = False
                            reader = csv.reader(f3)
                            for a in reader:
                                for i in range(23):
                                    if (i == 0) | ((i >= 5)&(i <= 15)) | ((i >= 17)&(i <= 20)):
                                        a[i] = float(a[i])
                                # print(a)
                            f3.close()
                            # print('msag now:',msagint)
                            if ((msagint[1] != ' ')&(msagint[2] != ' ')&(msagint[3] != ' ')&(msagint[4] != ' ')):  
                                # print('?') 
                                if ((msagint[1] != '\x00')&(msagint[2] != '\x00')&(msagint[3] != '\x00')&(msagint[4] != '\x00')&(msagint[5] != 0)):
                                    # print('??',abs(msagint[5] - msagint[6]),abs(msagint[8] - msagint[9]),abs(msagint[10] - msagint[11]),abs(msagint[12] - msagint[13]),abs(msagint[14] - msagint[15]))
                                    if ((abs(msagint[5] - msagint[6]) >= 40) & (abs(msagint[5] - msagint[6]) <= 60)) & \
                                        ((abs(msagint[8] - msagint[9]) >= 8) & (abs(msagint[8] - msagint[9]) <= 50)) & \
                                        ((abs(msagint[10] - msagint[11]) >= 8) & (abs(msagint[10] - msagint[11]) <= 50)) & \
                                        ((abs(msagint[12] - msagint[13]) >= 8) & (abs(msagint[12] - msagint[13]) <= 50)) & \
                                        ((abs(msagint[14] - msagint[15]) >= 8) & (abs(msagint[14] - msagint[15]) <= 50)):
                                        firstpush = False  
                                        msagint[tt] = 'correct' 
                                        print('firstpush done!')
                                        if api.pointscount > 0:             #第一个点在面积检测数过了，要减掉；如果第一次点击图像采集直接进入了字符识别则不用减
                                            api.pointscount -= 1
                                        lastmsag = msagint[:]  
                                        sparelast = msagint[:]
                                        # print(msagint)
                                    else:
                                        lastmsag = a
                                        sparelast = a
                                else:
                                    lastmsag = a
                                    sparelast = a
                            else:
                                lastmsag = a
                                sparelast = a
                        # print(lastmsag)
                        t = time.time()
                        t1 = datetime.datetime.now()
                        t1 = t1.strftime('%Y/%m/%d/%H:%M:%S')
                        t2 = str('%.3f'%(t-int(t)))
                        t3 = t1 + t2[1:5]
                        msagint[tt+5] = ('{},{},{}'.format(api.stopStack[-1][0],api.stopStack[-1][1],api.stopStack[-1][2])) if (len(api.stopStack) > 0) else -1
                        msagint[tt+6] = t3

                        if msagint[tt] != 'correct':
                            if (abs(msagint[5] - msagint[6]) >= 40) & (abs(msagint[5] - msagint[6]) <= 60):
                                if (str(msagint[1]).isnumeric() & str(msagint[2]).isnumeric() & str(msagint[3]).isnumeric() & (str(msagint[4]).isnumeric()|(msagint[4]==' '))):
                                    msagint[tt] = judgeNum()
                        if msagint[tt] == 'correct':
                            # api.pointscount += abs(int(msagint[1]+msagint[2]+msagint[3]+msagint[4])-int(lastmsag[1]+lastmsag[2]+lastmsag[3]+lastmsag[4]))
                            lastmsag = msagint[:]
                            sparelast = msagint[:]
                            # api.pointscount += 1
                            api.numNow = (msagint[1]+msagint[2]+msagint[3]+msagint[4]).zfill(4)
                            api.LCamera = int(api.numNow) - api.ordertype*(api.LView/2 - api.LView*float(msagint[0])/api.pixX - api.timeDelay*api.speedNow/60)
                            api.lengthDelta = msagint[tt+4] - api.ordertype*api.LCamera

                            # renew = pd.DataFrame([{'lastNum':api.numNow, 'lengthDelta':api.lengthDelta, 'ordertype':api.ordertype, \
                            #                         'cameraPos':api.cameraPos, 'biaoliInverseFlag':api.biaoliInverseFlag}])
                            # renew.to_csv(tempPath,mode='w',index=False,header=True)
                            saveTempData()
                            f3 = open(readPath + '\\camTemp.csv','w',newline='')
                            csv.writer(f3).writerow(msagint)
                            f3.close()
                            if len(api.stopStack) > 0:
                                if (api.Meters_NextFlaw - api.lengthAct)>=5:
                                    renewTargetsInStack()
                                    api.Meters_NextFlaw = api.stopStack[-1][1]
                                # if api.Meters_NextFlaw > api.lengthAct:
                                    client.write_registers (values=inverse(api.Meters_NextFlaw), unit=2, address=192, data_format='!f')
                            print('num:',api.numNow)
                            # print(msagint)
                            lastx = api.fangjuanL

                        elif msagint[tt] == 'Error':            #如果某一个标是错的，可以利用后面连续正确的标进行修正
                            sparestr = str(sparelast[1]+sparelast[2]+sparelast[3]+sparelast[4])
                            sparenum = int(sparestr.replace(' ',''))
                            nowstr = str(msagint[1]+msagint[2]+msagint[3]+msagint[4])
                            nownum = int(nowstr.replace(' ',''))
                            deltaL = abs(msagint[tt+4]-sparelast[tt+4])  
                            laststr = str(lastmsag[1]+lastmsag[2]+lastmsag[3]+lastmsag[4])
                            lastnum = int(laststr.replace(' ',''))    
                            if lastnum != sparenum:                          
                                if (deltaL > (abs(nownum-sparenum)*((api.deltaP*0.6))))&(deltaL < (abs(nownum-sparenum)*(api.deltaP*1.4))):
                                    msagint[tt] = 'correct'
                                    lastmsag = msagint[:]
                            sparelast = msagint[:]

                        line = [total] + msagint
                        total += 1
                        lines.append(line)
                        # csv.writer(f).writerow(lines)
                    if api.photoclose == 1:
                        break
                    microTimer(2)
                csv.writer(f).writerows(lines)
                if api.photoclose == 1:
                    break
        # client2.send(bytes('MW,#L0002,0\r',encoding='utf-8'))
        client2.close()

    def sendmode(self):
        mode0 = 'MW,#L0002,' + str(api.modetype)
        mode0 = bytes(mode0+'\r',encoding='utf-8')
        client2.send(mode0)


class Api:                                 #仅用于设定全局变量
    def __init__(self):
        self.b_start = False        #False停止，True启动
        self.b_firststart = True    #记录首次启动
        self.state = 0              #0保持，1升速，2降速,3停止
        self.Accelerate_time = 0    #升速时间
        self.Slow_time = 0          #降速时间
        self.Stop_time = 0          #停止时间
        self.aUp =  0.1          # 升速的加速度
        self.aDown = 0.1
        self.Up_D_Fj = 0            #上下放卷类型：1上放卷，2下放卷
        self.S_D_side = 0           #单双边放卷类型：1单边，2双边
        self.Mo_WidthUp = 0         #上隔膜宽度
        self.Mo_WidthDown = 0       #下隔膜宽度
        self.Mo_thickUp = 0         #上隔膜厚度
        self.Mo_thickDown = 0       #下隔膜厚度
        self.xintong_widthUp = 0    #上筒芯宽度
        self.xintong_widthDown = 0  #下筒芯宽度
        self.speedNow = 0           #当前速度
        self.SpeedLmitHigh = 0      #速度设定值高速
        self.SpeedLmitLow = 0       #速度设定值低速
        self.houshoujuanR = 0       #后收卷半径
        self.QianshoujuanR = 0      #前收卷半径
        self.LengthSum = 0          #收卷总长
        self.lengthAct = 0          #实际长度
        self.lengthSet = 0          #预设长度
        self.Z1_Z2_back = 0         #后臂纸筒：3寸，6寸
        self.Z1_Z2_front = 0        #前臂纸筒：3寸，6寸
        self.badMetersDone = []     #当前位置缺陷是否已处理
        self.badMeters = []         #缺陷数据库
        self.badMetersX = []        #缺陷x坐标
        self.badPics = []           #缺陷部位图像
        self.badPoint = 0           #缺陷位置指针
        self.flawPoint = 0          #缺陷位置编号
        self.zhengfan = []          #正反面
        self.command = 0            #指令1
        self.command2 = 0           #指令2
        self.command3 = 0           #指令3
        self.command4 = 0           #指令4
        self.buttonSend = 0         #按键指令
        self.commandList = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   #指令数组1``
                            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]   #指令数组2
        self.commandList3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #指令数组3
        self.commandList4 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]   #指令数组4
        self.buttonList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]     #按键数组
        self.deltaVUp = 0           #升速deltaV
        self.deltaVDown = 0         #降速deltaV
        self.deltaVStop = 0         #停止deltaV
        self.SF_Md0 = 0             #上放卷Md0
        self.SF_Md1 = 0             #上放卷Md1
        self.SF_Md2 = 0             #上放卷Md2
        self.XF_Md0 = 0             #下放卷Md0
        self.XF_Md1 = 0             #下放卷Md1
        self.XF_Md2 = 0             #下放卷Md2
        self.YS_Md0 = 0             #右收卷Md0
        self.YS_Md1 = 0             #右收卷Md1
        self.YS_Md2 = 0             #右收卷Md2
        self.starttime = 0          #开始时间
        self.endtime = 0            #结束时间
        self.stateConfirm = 0       #plc状态确认
        self.dataclose = 0          #数据保存退出标志
        self.photoclose = 0         #图像采集退出标志
        self.readPLCclose = 0       #读取PLC数据退出标志
        self.sendPLCclose = 0       #发送PLC数据退出标志
        self.showPicClose = 0       #图像显示退出标志
        self.modetype = 0           #拍摄模式，0面积判断，1字符识别
        self.jimitingji = 0         #记米停机
        self.shoujuanR = 0          #收卷半径
        self.fangjuanFSetUp = 0     #上放卷张力设定
        self.fangjuanActFUp = 0     #上放卷实际张力
        self.fangjuanFSetDown = 0   #下放卷张力设定
        self.fangjuanActFDown = 0   #下放卷实际张力
        self.fangjuanRUp = 0        #上放卷半径
        self.fangjuanRDown = 0      #下放卷半径
        self.avetension = 0         #平均张力
        self.ordertype = -1          #升降序类型，默认降序
        self.pointscount = 0        #统计点数
        self.oriLength = 0
        self.lengthDelta = 0        #读取米长与带子米长的差值
        self.lengthReal = 0         #修正后的米长
        self.lengthRead = 0         #读取的米长
        self.speedRead = 0          #读取的速度
        self.firstpoint = 0         #读到的第一个标
        self.shoujuanUpQiya = 0     #上收卷气压
        self.shoujuanDownQiya = 0   #下收卷气压
        self.jogspeed = 0           #点动速度
        self.ShangSJTension = 0     #上收卷张力
        self.XiaSJTension = 0       #下收卷张力
        self.totalMeter = 0         #设备运行总米长
        self.lights1 = []
        self.lights2 = []
        self.lights3 = []
        self.SpeedLmitHighRead = 0
        self.SpeedLmitLowRead = 0
        self.lengthSetRead = 0
        self.xintong_widthUpRead = 0
        self.xintong_widthDownRead = 0
        self.fangjuanFSetUpRead = 0
        self.fangjuanFSetDownRead = 0
        self.Mo_WidthUpRead = 0
        self.Mo_WidthDownRead = 0
        self.Mo_thickUpRead = 0
        self.Mo_thickDownRead = 0
        self.xintongTypeUp = 0
        self.xintongTypeDown = 0
        self.moTypeUp = 0
        self.moTypeDown = 0
        # self.No_NextFlaw = 0        #前方瑕疵号
        self.Amount_LeftFlaw = 0    #剩余瑕疵数
        self.Meters_NextFlaw = 0    #瑕疵位置米数
        self.offsetNY = 0           #NY面缺陷补偿
        self.offsetPP = 0           #PP面缺陷补偿
        self.jiedaijinchi = 0       #接带进尺

        #datacollect
        self.Omega_Axis1_REAL = 0
        self.Position_Axis1_Act_REAL = 0
        self.Torque_Axis1_Act_REAL = 0
        self.Omega_Axis2_REAL = 0
        self.Position_Axis2_Act_REAL = 0
        self.Torque_Axis2_Act_REAL = 0
        self.Omega_Axis3_REAL = 0
        self.Position_Axis3_Act_REAL = 0
        self.Torque_Axis3_Act_REAL = 0
        self.Omega_Axis6_REAL = 0
        self.Position_Axis6_Act_REAL = 0
        self.Torque_Axis6_Act_REAL = 0
        self.Omega_Axis8_REAL = 0
        self.Position_Axis8_Act_REAL = 0
        self.Torque_Axis8_Act_REAL = 0
        self.buttonCollect = 0
        self.QXlist = [0]*52
        self.MXlist = [[0]*16]*6         # MX寄存器
        self.didaoDingWei = 0       # 底刀定位调整
        self.Meters_Stop = 0        # 点动停机米数
        self.speedJog = 0           # 点动停机速度
        self.fangjuanSpeedRatio = 0 # 放卷牵引速比
        self.tongkuanUp = 0         # 筒宽上
        self.tongkuanDown = 0       # 筒宽下
        self.shoujuanFSetUp = 0     # 收卷张力设定上
        self.shoujuanFSetDown = 0   # 收卷张力设定下
        self.zhuiduUp = 0           # 锥度上
        self.zhuiduDown = 0         # 锥度下
        self.circlesUp = 0          # 滑差环数上
        self.circlesDown = 0        # 滑差环数下
        self.xintongSizeUp = 0      # 芯筒尺寸上
        self.xintongSizeDown = 0    # 芯筒尺寸下
        self.alarmR = 0             # 放卷报警半径
        self.fangjuanL = 0          # 放卷长度
        self.cameraPos = 1          # 相机位置，0上方，1下方，默认安装在下方

        self.yagunBackUp = 0        # 压辊后退上
        self.yagunBackDown = 0      # 压辊后退下
        self.targetUp = 0           # 目标值上
        self.targetDown = 0         # 目标值下

        #绘制曲线用
        # data = np.loadtxt('data20211102_2.txt')
        # length_data = len(data)
        self.xData = np.linspace(0,99,100)
        self.containerData1 = [0]*100
        self.containerData2 = [0]*100
        self.containerData3 = [0]*100
        self.containerData4 = [0]*100
        self.containerData5 = [0]*100
        self.containerData6 = [0]*100
        self.yData1 = [0]*100
        self.yData2 = [0]*100
        self.yData3 = [0]*100
        self.yData4 = [0]*100
        self.yData5 = [0]*100
        self.yData6 = [0]*100
        self.receive_count=0
        self.dataSaveFlag = 0

        #相机相关
        self.deltaP = 5      # 两个标志间的距离
        self.LSend = 0          # 发送给PLC的缺陷停机位置
        self.LCamera = 0        # 相机正下方所对应的米长
        self.LView = 0.165        # 相机视野范围，m
        self.LJiedai = 3.62209  # 相机正下方到接带处中间位置的距离，m;拍摄反面时，相机会向后移动0.0978m
        self.pixX = 2400        # 相机x方向总像素数
        self.timeDelay = 0.07   # 相机系统时延
        self.numNow = ''        # 当前读码结果
        self.jiedaiNow = 0      # 接带处的当前位置
        self.view1now = 0       
        self.view2now = 0
        self.knife1now = 0
        self.knife2now = 0
        self.wind1now = 0
        self.wind2now = 0
        self.Lcut = 0           # 缺陷裁剪长度

        self.uiEA = 0           # 是否允许界面操作

        #缺陷处理弹窗相关
        self.dealtype = 0       # 对缺陷的处理类型：0不处理，1确认，2裁剪，3双面贴胶，4NY面贴胶，5PP面贴胶
        self.dealDoneFlag = 0   # 对此次停机处理是否已经完成
        
        self.stopStack = []     # 停机位置栈，进栈元素为列表[瑕疵编号，停机位置，停机位置m，当前停机点是否已经完成]，其中
                                # m = 0观察点1，1观察点2，2切刀后1停机，3切刀后2停机，4上收卷停机，5下收卷停机
        self.lastStackPop = []  # 记录上次从栈内pop的数据
        
        self.flawNums = []      # 瑕疵文件里的瑕疵编号

        self.biaoliInverseFlag = 0  # 此卷膜料NY面与PP面是否反了
        self.findPoint = {}     # 找到这个缺陷是表格里的第几个
        self.firstUpOrDown = 0  # 1工位在0上收卷还是1下收卷
        self.shoujuanBorders = []   # 收卷每个小卷的边界坐标
        self.shoujuanWidths = []    # 收卷每个小卷的宽度
        # self.zeroOffset = 0.436     # 标码0000位置对应缺陷坐标系的y坐标值
        self.offsetPPDown = 0       # PP面下轴贴标补偿
        self.offsetPPUp = 0         # PP面上轴贴标补偿
        self.offsetX = 0            # 缺陷x坐标补偿
        self.offsetNYDown = 0       # 下收卷贴标补偿
        self.offsetNYUp = 0         # 上收卷贴标补偿

        self.shoujuanFlawInfo = {}  # 保存当前批次的所有瑕疵处理信息
        self.lastPeiFangNum = 0     # 上次使用的配方号
        self.flawFilePath = ''      # 上次使用的缺陷文件
        self.knifeAlarmSet = 0      # 刀具报警米数设定
        self.cutPPorNY = 0          # 0切PP面，1切NY面

        #读取上次关机前的内容
        tempData = pd.read_csv(tempPath)
        self.numNow = str(int(tempData['lastNum'][0])).zfill(4)
        self.lengthDelta = float(tempData['lengthDelta'][0])
        self.ordertype = int(tempData['ordertype'][0])
        self.cameraPos = int(tempData['cameraPos'][0])
        self.biaoliInverseFlag = int(tempData['biaoliInverseFlag'][0])
        self.offsetNY = float(tempData['offsetNY'][0])
        self.offsetPP = float(tempData['offsetPP'][0])
        self.offsetPPDown = float(tempData['offsetPPDown'][0])
        self.offsetPPUp = float(tempData['offsetPPUp'][0])
        self.offsetX = float(tempData['offsetX'][0])
        self.lastPeiFangNum = int(tempData['lastPeiFangNum'][0])
        self.knifeAlarmSet = int(tempData['knifeAlarmSet'][0])
        self.cutPPorNY = int(tempData['cutPPorNY'][0])
        self.offsetNYDown = float(tempData['offsetNYDown'][0])
        self.offsetNYUp = float(tempData['offsetNYUp'][0])

        if self.cutPPorNY == 0:     #切PP面
            self.stopTypeNames = ['第二观察区','第一观察区','PP面上轴贴标区','PP面下轴贴标区','上收卷','下收卷','预设长度停机']
            self.cam2view = [[3.11819,1.11167],[3.11819-0.0978,1.11167-0.0978,]]   # [[上相机到第二观察区,上相机到第一观察区]],[下相机到第二观察区,下相机到第一观察区]]
            self.cam2knife = [[7.65229+self.offsetPPUp/1000,7.94342+self.offsetPPDown/1000],[7.65229-0.0978+self.offsetPPUp/1000,7.94342-0.0978+self.offsetPPDown/1000]]  # [[上相机到切刀后上收卷停机,上相机到切刀后下收卷停机],[下相机到切刀后上收卷停机,下相机到切刀后下收卷停机]]
            self.cam2wind1 = [[8.37763+self.offsetNYUp/1000,8.26452+self.offsetNYDown/1000],[8.37763-0.0978+self.offsetNYUp/1000,8.26452-0.0978+self.offsetNYDown/1000]]  # [[上相机到上收卷之前，上相机到下收卷之前],[下相机到上收卷之前，下相机到下收卷之前]]
        elif self.cutPPorNY == 1:     #切NY面
            self.stopTypeNames = ['第一观察区','第二观察区','PP面上轴贴标区','PP面下轴贴标区','上收卷','下收卷','预设长度停机']
            self.cam2view = [[1.11167,3.11819],[1.11167-0.0978,3.11819-0.0978,]]   # [[上相机到第一观察区,上相机到第二观察区]],[下相机到第一观察区,下相机到第二观察区]]
            self.cam2knife = [[8.59438+self.offsetPPUp/1000,8.48128+self.offsetPPDown/1000],[8.59438-0.0978+self.offsetPPUp/1000,8.48128-0.0978+self.offsetPPDown/1000]]  # [[上相机到切刀后上收卷停机,上相机到切刀后下收卷停机],[下相机到切刀后上收卷停机,下相机到切刀后下收卷停机]]
            self.cam2wind1 = [[8.37763,8.26452],[8.37763-0.0978,8.26452-0.0978]]  # [[上相机到上收卷之前，上相机到下收卷之前],[下相机到上收卷之前，下相机到下收卷之前]]
        
        saverPath = readPath + '\\gongweiSet.csv'
        if os.path.exists(saverPath):
            f = open(saverPath,'r',newline='')
            reader = csv.reader(f)
            # print('length',len(reader))
            for i in reader:
                self.shoujuanWidths.append(float(i[0]))
            f.close()
            self.firstUpOrDown = self.shoujuanWidths.pop()
            self.shoujuanBorders=[0]#建立区间列表
            total = 0   
            for i in range(len(self.shoujuanWidths)):
                if self.shoujuanWidths[i] != 0:
                    total+=self.shoujuanWidths[i]
                    self.shoujuanBorders.append(total)
            # print('first borders',self.shoujuanBorders) 

        windInfoPath = readPath + '\\tempWindInfo.csv'
        if os.path.exists(windInfoPath):
            f2 = open(windInfoPath,'r',newline='')
            reader2 = csv.reader(f2)
            t = 0
            for oneline in reader2:
                if t == 0:
                    t += 1
                    juanNums = list(map(lambda x:int(x),oneline))
                else:
                    oneline = list(map(lambda x:x.replace('[','').replace(']','').split(','),oneline))    
                    # print('????',oneline)
                    for i in range(len(oneline)):
                        # try:
                        #     oneline[i] = list(map(lambda x:float(x),oneline[i][0]))
                        #     # oneline[i] = [float]
                        # except Exception:
                        #     oneline[i] = []
                        if oneline[i] == ['']:
                            oneline[i] = []
                        else:
                            for j in range(len(oneline[i])):
                                oneline[i][j] = float(oneline[i][j])
                    # print('1?',oneline)
                    if t == 1:
                        t += 1
                        jiaodai = oneline
                    elif t == 2:
                        jietou = oneline
            f2.close()
            self.shoujuanFlawInfo = {}
            for i in range(1,len(juanNums)+1):
                self.shoujuanFlawInfo[i] = [[],[]]
            for i in range(len(juanNums)):
                self.shoujuanFlawInfo[juanNums[i]] = [jiaodai[i],jietou[i]]
            # print('??',self.shoujuanFlawInfo)

        knifeUsePath = readPath + '\\KnifeFile.csv'
        self.daoRecs = {}
        self.knifeUsing = []
        self.knifeEA = []
        if os.path.exists(knifeUsePath):
            f3 = open(knifeUsePath,'r',newline='')
            reader = csv.reader(f3)
            tt = 0
            for a in reader:
                if tt == 0:
                    tt += 1
                elif tt == 1:
                    self.daoRecs[int(a[0])] = float(a[1])
            f3.close()

        f4 = open(readPath + '\\knifeUsing.csv','r',newline='')
        reader = csv.reader(f4)
        tt = 0
        for a in reader:
            for i in range(12):
                a[i] = int(a[i])
            if tt == 0:
                tt += 1
                self.knifeUsing = a
            elif tt == 1:
                self.knifeEA = a
            # print(a)
        f4.close()

        lastFlawPath = readPath + '\\flawPath.csv'
        if os.path.exists(lastFlawPath):
            f5 = open(lastFlawPath,'r',newline='')
            reader = csv.reader(f5)
            for a in reader:
                self.flawFilePath = a[0]
            f5.close()
            if not (os.path.exists(self.flawFilePath)):
                self.flawFilePath = updateFlawFile(flawFileFolderPath)
        else:
            self.flawFilePath = updateFlawFile(flawFileFolderPath)
        print('flawfile ',self.flawFilePath)
        
        self.shoujuanFlawStack = []     # 收卷贴标、接头记录栈[放卷长度，卷位，0贴标1接头, 瑕疵编号]
        shoujuanStackFile = readPath + '\\shoujuanStack.csv'
        if os.path.exists(shoujuanStackFile):
            f6 = open(shoujuanStackFile,'r',newline='')
            reader = csv.reader(f6)
            for a in reader:
                for i in range(len(a)):
                    a[0] = float(a[0])
                    a[1] = int(a[1])
                    a[2] = int(a[2])
                    a[3] = int(a[3])
                self.shoujuanFlawStack.append(a)
            f6.close()



class Ui_lineWindow(object):               #绘制曲线的界面布局
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 786)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.showLine = QtWidgets.QLabel(self.centralwidget)
        self.showLine.setGeometry(QtCore.QRect(30, 40, 72, 15))
        self.showLine.setObjectName("showLine")
        self.Velocity = QtWidgets.QCheckBox(self.centralwidget)
        self.Velocity.setGeometry(QtCore.QRect(110, 20, 71, 41))
        self.Velocity.setObjectName("Velocity")
        self.Tension1 = QtWidgets.QCheckBox(self.centralwidget)
        self.Tension1.setGeometry(QtCore.QRect(210, 20, 81, 41))
        self.Tension1.setObjectName("Tension1")
        self.Radius1 = QtWidgets.QCheckBox(self.centralwidget)
        self.Radius1.setGeometry(QtCore.QRect(320, 20, 81, 41))
        self.Radius1.setObjectName("Radius1")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 100, 980, 641))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.PicLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.PicLayout.setContentsMargins(0, 0, 0, 0)
        self.PicLayout.setObjectName("PicLayout")
        # self.dataSave = QtWidgets.QPushButton(self.centralwidget)
        # self.dataSave.setGeometry(QtCore.QRect(420, 40, 75, 23))
        # self.dataSave.setObjectName("dataSave")
        self.Tension2 = QtWidgets.QCheckBox(self.centralwidget)
        self.Tension2.setGeometry(QtCore.QRect(210, 50, 81, 41))
        self.Tension2.setObjectName("Tension2")
        self.meterLong = QtWidgets.QCheckBox(self.centralwidget)
        self.meterLong.setGeometry(QtCore.QRect(110, 50, 71, 41))
        self.meterLong.setObjectName("meterLong")
        self.Radius2 = QtWidgets.QCheckBox(self.centralwidget)
        self.Radius2.setGeometry(QtCore.QRect(320, 50, 81, 41))
        self.Radius2.setObjectName("Radius2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.showLine.setText(_translate("MainWindow", "曲线显示"))
        self.Velocity.setText(_translate("MainWindow", "实际速度"))
        self.Tension1.setText(_translate("MainWindow", "上放卷张力"))
        self.Radius1.setText(_translate("MainWindow", "上放卷半径"))
        # self.dataSave.setText(_translate("MainWindow", "数据保存"))
        self.Tension2.setText(_translate("MainWindow", "下放卷张力"))
        self.meterLong.setText(_translate("MainWindow", "实际长度"))
        self.Radius2.setText(_translate("MainWindow", "下放卷半径"))


class MyGraphWindow(QtWidgets.QMainWindow,Ui_lineWindow):   #绘制曲线窗口的函数
    def __init__(self):
        super(MyGraphWindow,self).__init__()
        self.setupUi(self)
        self.p1 = self.setP1ui()
        self.p2 = self.setP2ui()
        self.p3 = self.setP3ui()
        self.p4 = self.setP4ui()
        self.p5 = self.setP5ui()
        self.p6 = self.setP6ui()
        def aa():
            yData1 = api.containerData1 if self.Velocity.isChecked() else ([0]*100)
            yData2 = api.containerData2 if self.Tension1.isChecked() else ([0]*100)
            yData3 = api.containerData3 if self.Radius1.isChecked() else ([0]*100)
            yData4 = api.containerData4 if self.meterLong.isChecked() else ([0]*100)
            yData5 = api.containerData5 if self.Tension2.isChecked() else ([0]*100)
            yData6 = api.containerData6 if self.Radius2.isChecked() else ([0]*100)

            self.p1.plot(api.xData,yData1,pen='g',name='实际速度',clear=True)
            self.p2.plot(api.xData,yData2,pen='y',name='上放卷张力',clear=True)
            self.p3.plot(api.xData,yData3,pen='g',name='上放卷半径',clear=True)
            self.p4.plot(api.xData,yData4,pen='y',name='实际长度',clear=True)
            self.p5.plot(api.xData,yData5,pen='g',name='下放卷张力',clear=True)
            self.p6.plot(api.xData,yData6,pen='y',name='下放卷半径',clear=True)
            # print('*******')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(aa)
        self.timer.start(100)
    global win
    win = pg.GraphicsLayoutWidget()

    def setP1ui(self):
        pg.setConfigOptions(antialias=True)
        self.PicLayout.addWidget(win)
        global p1
        p1 =win.addPlot(title='实际速度')
        p1.setLabel('left',text='vel',color='#ffffff')
        p1.showGrid(x=True,y=True)
        p1.setLogMode(x=False,y=False)
        # p1.setLabel('bottom',text='time',units='s')
        return p1
    def setP2ui(self):
        pg.setConfigOptions(antialias=True)
        self.PicLayout.addWidget(win)
        global p2
        p2 =win.addPlot(title='上放卷张力')
        p2.setLabel('left',text='tensionUp',color='#ffffff')
        p2.showGrid(x=True,y=True)
        p2.setLogMode(x=False,y=False)
        # p2.setLabel('bottom',text='time',units='s')
        return p2
    def setP3ui(self):
        pg.setConfigOptions(antialias=True)
        self.PicLayout.addWidget(win)
        global p3
        p3 =win.addPlot(title='上放卷半径')
        p3.setLabel('left',text='radiusUp',color='#ffffff')
        p3.showGrid(x=True,y=True)
        p3.setLogMode(x=False,y=False)
        # p3.setLabel('bottom',text='time',units='s')
        return p3
    def setP4ui(self):
        pg.setConfigOptions(antialias=True)
        win.nextRow()
        self.PicLayout.addWidget(win)
        global p4
        p4 =win.addPlot(title='实际长度')
        p4.setLabel('left',text='length',color='#ffffff')
        p4.showGrid(x=True,y=True)
        p4.setLogMode(x=False,y=False)
        # p4.setLabel('bottom',text='time',units='s')
        return p4
    def setP5ui(self):
        pg.setConfigOptions(antialias=True)
        self.PicLayout.addWidget(win)
        global p5
        p5 =win.addPlot(title='下放卷张力')
        p5.setLabel('left',text='tensionDown',color='#ffffff')
        p5.showGrid(x=True,y=True)
        p5.setLogMode(x=False,y=False)
        # p5.setLabel('bottom',text='time',units='s')
        return p5
    def setP6ui(self):
        pg.setConfigOptions(antialias=True)
        self.PicLayout.addWidget(win)
        global p6
        p6 =win.addPlot(title='下放卷半径')
        p6.setLabel('left',text='radiusDown',color='#ffffff')
        p6.showGrid(x=True,y=True)
        p6.setLogMode(x=False,y=False)
        # p6.setLabel('bottom',text='time',units='s')
        return p6
    
    def createDataSave(self):       # 数据保存
        api.dataSaveFlag = 1 - api.dataSaveFlag
        if api.dataSaveFlag == 1:
            api.dataclose = 0
            thread1 = dataThread(1,'Thread1',0)
            print('保存数据开')
            thread1.start()
        elif api.dataSaveFlag == 0:
            api.dataclose = 1
            print('保存数据关')


class myMainWindow(QtWidgets.QMainWindow,Ui_MainWindow):    #主界面的函数
    def __init__(self):
        super(myMainWindow,self).__init__()
        self.setupUi(self)
        # makeDecision(updateFlawFile(flawFileFolderPath) + '\\ErrorData.csv')
        makeDecision(api.flawFilePath + '/ErrorData.csv')
        time.sleep(1)
        if api.flawPoint in api.findPoint.keys():
            api.badPoint = api.findPoint[api.flawPoint]
        self.dataShow()
        # self.timer500 = QtCore.QTimer()
        # self.timer500.timeout.connect(self.continueShow)
        # self.timer500.start(500)
        # self.timer100 = QtCore.QTimer()
        # self.timer100.timeout.connect(self.checkChange)
        # self.timer100.start(100)
        # readDataFromPLC()
        global last_qizhang
        global last_flawStop
        global now_qizhang
        global now_flawStop
        global qizhang_rise
        global flaw_rise
        now_qizhang = api.QXlist[15]
        last_qizhang = now_qizhang
        now_flawStop = api.MXlist[5][2]
        last_flawStop = now_flawStop
        qizhang_rise = 0
        flaw_rise = 0
        self.pushButton_23.clicked.connect(self.show_pic)           # 显示缺陷图片
        self.pushButton_16.clicked.connect(self.createDrawLine)     # 曲线绘制
        self.pushButton_17.clicked.connect(self.createDataSave)     # 数据保存
        self.pushButton_19.clicked.connect(self.changeOrder)        # 切换标码升降序
        self.pushButton_24.clicked.connect(self.openFlawFile)       # 打开缺陷文件
        self.knifeButton.clicked.connect(self.knifeOpen)
        self.peifangButton.clicked.connect(self.peifangOpen)
        self.pushButton_25.clicked.connect(self.readFlawFile)       # 读取缺陷文件
        self.pushButton_49.clicked.connect(self.openShoujuanSet)    # 打开收卷工位设置界面
        self.pushButton_26.clicked.connect(self.addFlaw)            # 新增贴标
        self.pushButton_27.clicked.connect(self.addJietou)          # 新增接头
        self.pushButton_28.clicked.connect(self.handyPop)           # 手动缺陷弹窗
        #按键按下时触发函数
        self.pushButton.pressed.connect(lambda:self.pressedFcn(3,13,1))
        self.pushButton_2.pressed.connect(lambda:self.pressedFcn(0,3,0))
        self.pushButton_3.pressed.connect(lambda:self.pressedFcn(0,5,0))
        self.pushButton_4.pressed.connect(lambda:self.pressedFcn(1,12,0))
        self.pushButton_5.pressed.connect(lambda:self.pressedFcn(0,6,0))
        self.pushButton_6.pressed.connect(lambda:self.pressedFcn(0,7,0))
        self.pushButton_7.pressed.connect(lambda:self.pressedFcn(1,7,1))
        self.pushButton_8.pressed.connect(lambda:self.pressedFcn(0,8,0))
        self.pushButton_9.pressed.connect(lambda:self.pressedFcn(1,15,1))
        self.pushButton_10.pressed.connect(lambda:self.pressedFcn(3,14,1))
        self.pushButton_11.pressed.connect(lambda:self.pressedFcn(999,1053,1))
        self.pushButton_12.pressed.connect(lambda:self.pressedFcn(999,1054,1))
        self.pushButton_13.pressed.connect(lambda:self.pressedFcn(3,15,1))
        self.pushButton_14.pressed.connect(lambda:self.pressedFcn(4,2,0))
        # self.pushButton_15.pressed.connect(lambda:self.pressedFcn(4,1,0))
        self.pushButton_20.pressed.connect(lambda:self.pressedFcn(3,13,1))
        self.pushButton_21.pressed.connect(lambda:self.pressedFcn(1,1,0))
        self.pushButton_22.pressed.connect(lambda:self.pressedFcn(9,2,1))
        #按键松开时触发函数
        self.pushButton.released.connect(lambda:self.releasedFcn(3,13,1))
        self.pushButton_2.released.connect(lambda:self.releasedFcn(0,3,0))
        self.pushButton_3.released.connect(lambda:self.releasedFcn(0,5,0))
        self.pushButton_4.released.connect(lambda:self.releasedFcn(1,12,0))
        self.pushButton_5.released.connect(lambda:self.releasedFcn(0,6,0))
        self.pushButton_6.released.connect(lambda:self.releasedFcn(0,7,0))
        self.pushButton_7.released.connect(lambda:self.releasedFcn(1,7,1))
        self.pushButton_8.released.connect(lambda:self.releasedFcn(0,8,0))
        self.pushButton_9.released.connect(lambda:self.releasedFcn(1,15,1))
        self.pushButton_10.released.connect(lambda:self.releasedFcn(3,14,1))
        self.pushButton_11.released.connect(lambda:self.releasedFcn(999,1053,1))
        self.pushButton_12.released.connect(lambda:self.releasedFcn(999,1054,1))
        self.pushButton_13.released.connect(lambda:self.releasedFcn(3,15,1))
        self.pushButton_14.released.connect(lambda:self.releasedFcn(4,2,0))
        # self.pushButton_15.released.connect(lambda:self.releasedFcn(4,1,0))
        self.pushButton_20.released.connect(lambda:self.releasedFcn(3,13,1))
        self.pushButton_21.released.connect(lambda:self.releasedFcn(1,1,0))
        self.pushButton_22.released.connect(lambda:self.releasedFcn(9,2,1))
        #单选
        self.radioButton.toggled.connect(lambda:self.radioBtnChange(1))
        self.radioButton_3.toggled.connect(lambda:self.radioBtnChange(3))
        self.radioButton_5.toggled.connect(lambda:self.radioBtnChange(5))
        self.radioButton_13.toggled.connect(lambda:self.radioBtnChange(7))
        self.radioButton_14.toggled.connect(lambda:self.radioBtnChange(7))
        #输入
        self.spinBox.editingFinished.connect(lambda:self.qtInput('Meters_Stop_R_G'))
        # spinbox数组
        self.spinBoxName = [self.spinBox,self.spinBox_3,self.spinBox_4,self.spinBox_5,self.spinBox_6,self.spinBox_7,self.spinBox_8,self.spinBox_9,\
            self.spinBox_10,self.spinBox_11,self.spinBox_12,self.spinBox_13,self.spinBox_14,self.spinBox_15,self.spinBox_16,self.spinBox_17,self.spinBox_18,self.spinBox_19,\
                self.spinBox_20,self.spinBox_22,self.spinBox_23,self.spinBox_24,self.spinBox_27,self.spinBox_28,self.spinBox_29,self.spinBox_25,self.spinBox_30,\
                    self.textEdit_2,self.textEdit_3,self.textEdit_10,self.textEdit_9,self.textEdit_11,self.textEdit_12,self.textEdit_13]
        self.displayData=[api.Meters_Stop,api.lengthSet,api.xintong_widthDown,api.fangjuanFSetDown,api.Mo_WidthDown,api.Mo_thickDown,api.tongkuanUp,api.circlesUp,\
            api.shoujuanFSetUp,api.zhuiduUp,api.shoujuanFSetDown,api.zhuiduDown,api.circlesDown,api.tongkuanDown,api.SpeedLmitHigh,api.Accelerate_time,api.Slow_time,api.Stop_time,\
                api.flawNums[api.badPoint],api.speedJog,api.didaoDingWei,int(api.Amount_LeftFlaw),api.badMeters[api.badPoint],api.alarmR,api.jiedaijinchi,api.deltaP,api.Meters_NextFlaw,\
                    api.offsetNY,api.offsetPP,api.offsetPPUp,api.offsetPPDown,api.offsetX,api.offsetNYUp,api.offsetNYDown]
        # self.spinBox_2.editingFinished.connect(self.qtInput)
        self.spinBox_3.editingFinished.connect(lambda:self.qtInput('MeterLongSet_DWORD_GM'))
        self.spinBox_4.editingFinished.connect(lambda:self.qtInput('D5_CoreWidth_DWORD_FromPC_GM'))
        self.spinBox_5.editingFinished.connect(lambda:self.qtInput('D92_TensionAxis1_DWORD_FromPC_GM'))
        self.spinBox_6.editingFinished.connect(lambda:self.qtInput('D4_DiaWidth_DWORD_FromPC_GM'))
        self.spinBox_7.editingFinished.connect(lambda:self.qtInput('D1_DiaThick__DWORD_FromPC_GM'))
        self.spinBox_8.editingFinished.connect(lambda:self.qtInput('H8_Axis_4_DWORD_FromPC_GM'))
        self.spinBox_9.editingFinished.connect(lambda:self.qtInput('HuanCount_SJ_H_REAL_G'))
        self.spinBox_10.editingFinished.connect(lambda:self.qtInput('T_g_ShouJuan_DWORD_GM'))
        self.spinBox_11.editingFinished.connect(lambda:self.qtInput('Taper_ShouJuanRight_LREAL_G'))
        self.spinBox_12.editingFinished.connect(lambda:self.qtInput('T_g_ShouJuanLeft_DWORD_GM'))
        self.spinBox_13.editingFinished.connect(lambda:self.qtInput('Taper_ShouJuanLeft_LREAL_G'))
        self.spinBox_14.editingFinished.connect(lambda:self.qtInput('HuanCount_SJ_Q_REAL_G'))
        self.spinBox_15.editingFinished.connect(lambda:self.qtInput('H1_Axis_4_DWORD_FromPC_GM'))
        self.spinBox_16.editingFinished.connect(lambda:self.qtInput('D93_SpeedLMT_DWORD_FromPC_GM'))
        self.spinBox_17.editingFinished.connect(lambda:self.qtInput('TimeUp_DWORD_GM'))
        self.spinBox_18.editingFinished.connect(lambda:self.qtInput('TimeDown_DWORD_GM'))
        self.spinBox_19.editingFinished.connect(lambda:self.qtInput('TimeStop_DWORD_GM'))
        self.spinBox_20.editingFinished.connect(lambda:self.qtInput('No_NextFlaw_R_G'))
        # self.spinBox_21.editingFinished.connect(lambda:self.qtInput('D98_V_Diff_main_DWORD_FrmPC_GM'))
        self.spinBox_22.editingFinished.connect(lambda:self.qtInput('Speed_JOG_R_G'))
        self.spinBox_23.editingFinished.connect(lambda:self.qtInput('DiDaoDingWeiAdjust_R_G'))
        self.spinBox_24.editingFinished.connect(lambda:self.qtInput('Amount_LeftFlaw_R_G'))
        # self.spinBox_25.editingFinished.connect(lambda:self.qtInput(''))
        self.spinBox_30.editingFinished.connect(lambda:self.qtInput('Meters_NextFlaw_R_G'))
        self.spinBox_28.editingFinished.connect(lambda:self.qtInput('D98_3RadiusTingJi_Delta_DWORD_GM'))
        self.spinBox_29.editingFinished.connect(lambda:self.qtInput('Meters_Stop_axis2_R_G'))
        # self.textEdit_2.editingFinished.connect(lambda:self.qtInput('OffsetLen_Front_R_G'))
        self.textEdit_2.editingFinished.connect(lambda:self.qtInput('OffsetLen_Front_R_G'))
        self.textEdit_3.editingFinished.connect(lambda:self.qtInput('OffsetLen_Back_R_G'))
        self.textEdit_10.editingFinished.connect(lambda:self.qtInput(-1))
        self.textEdit_9.editingFinished.connect(lambda:self.qtInput(-1))
        self.textEdit_11.editingFinished.connect(lambda:self.qtInput(-1))
        self.textEdit_12.editingFinished.connect(lambda:self.qtInput(-1))
        self.textEdit_13.editingFinished.connect(lambda:self.qtInput(-1))
        if api.uiEA:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
        if api.cameraPos == 0:
            self.radioButton_13.setChecked(True)
        elif api.cameraPos == 1:
            self.radioButton_14.setChecked(True)
        self.checkBox_3.setChecked(api.biaoliInverseFlag)
        self.checkBox.toggled.connect(self.uiEnable)
        self.checkBox_3.toggled.connect(self.biaoliInverse)
        self.spinBox_26.editingFinished.connect(self.cutFinished)
        self.ChuandaiPic.clicked.connect(self.ChuandaiPicOpen)
        
        self.drawLineFlag = 0
        self.newTape = 1        #新料
        self.showDataCount = 0
        self.knifeSetFlag = 0
        self.peifangSetFlag = 0
        self.mainState = 0      #主循环状态
        self.laststate = 0      #主循环上一个状态
        self.qianOrHou = 0      #当前位置在当前缺陷前还是后，前1后0
        self.numPush = ''       #打开气胀或缺陷检测时的标码
        self.totalFlaws = api.Amount_LeftFlaw
        self.cutStart = 0       #接带平台中心开始裁剪的位置
        self.cutEnd = 0         #接带平台中心结束裁剪的位置
        self.lastDeal = 0       #上一个缺陷的处理方式
        self.firstStart = True  #首次启动
        self.lastLCamera = api.LCamera
        self.lastPointCount = [0,0]#记录当前停机点停了几次
        self.handyPopFlag = 0   #手动缺陷弹窗标志为0
        
        print('当前文件内瑕疵位置：',api.badMeters)
        if os.path.exists(readPath + '\\stopStack.csv'):
            f = open(readPath + '\\stopStack.csv', 'r', newline='')
            reader = csv.reader(f)
            for i in reader:
                api.stopStack.append([int(i[0]), float(i[1]), int(i[2]), int(i[3])])
            print('in_------',api.stopStack)
        self.dataShow()
        self.timer200 = QtCore.QTimer()
        self.timer200.timeout.connect(self.mainTimer200)
        self.timer200.start(200)

    def ChuandaiPicOpen(self):
        try:
            # os.rename('PA1013穿带原理图.png','PA1013穿带原理图.png')
            os.startfile(chuandaiPath)
        except:
            msg = QMessageBox(QMessageBox.Warning,'提示','穿带图不存在')
            msg.exec_()    

    def cutFinished(self):      #输入裁剪长度
        api.Lcut = self.spinBox_26.value()
        # api.lengthDelta += api.Lcut
    
    def uiEnable(self):         #是否允许界面操作
        if self.checkBox.isChecked():
            api.uiEA = 1
        else:
            api.uiEA = 0
    
    def biaoliInverse(self):
        if self.checkBox_3.isChecked():
            api.biaoliInverseFlag = 1
        else:
            api.biaoliInverseFlag = 0
        saveTempData()

    def mainTimer200(self):     # 主循环
        # readDataFromPLC()
        self.continueShow()
        if api.fangjuanL != 0:
            self.lastLCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
        try:
            self.displayData=[api.Meters_Stop,api.lengthSet,api.xintong_widthDown,api.fangjuanFSetDown,api.Mo_WidthDown,api.Mo_thickDown,api.tongkuanUp,api.circlesUp,\
                api.shoujuanFSetUp,api.zhuiduUp,api.shoujuanFSetDown,api.zhuiduDown,api.circlesDown,api.tongkuanDown,api.SpeedLmitHigh,api.Accelerate_time,api.Slow_time,api.Stop_time,\
                    int(api.flawNums[api.badPoint]),api.speedJog,api.didaoDingWei,int(api.Amount_LeftFlaw),api.badMeters[api.badPoint],api.alarmR,api.jiedaijinchi,api.deltaP,api.Meters_NextFlaw,\
                        api.offsetNY,api.offsetPP,api.offsetPPUp,api.offsetPPDown,api.offsetX,api.offsetNYUp,api.offsetNYDown]
            for k in range(len(self.spinBoxName)):
                if self.spinBoxName[k].hasFocus():
                    # print("正在输入")
                    pass
                else:
                    self.spinBoxName[k].setValue(self.displayData[k])
        except Exception as e:
            print(e)
        global last_qizhang
        global last_flawStop
        global now_qizhang
        global now_flawStop
        global qizhang_rise
        global flaw_rise


        if api.MXlist[5][0] == 1:       #自动停机选择打开，把这一米数入栈
                if api.lengthAct < api.lengthSet:
                    yusheCount = 0
                    for i in range(len(api.stopStack)):
                        if api.stopStack[i][2] == 6:
                            yusheCount += 1
                            api.stopStack[i][1] = api.lengthSet
                            break
                    if yusheCount == 0:
                        api.stopStack.append([0,api.lengthSet,6,0])
                    api.stopStack.sort(key = lambda x:x[1], reverse = True)
                    f = open(readPath + '\\stopStack.csv', 'w', newline='')
                    csv.writer(f).writerows(api.stopStack)
                    f.close()

        elif api.MXlist[5][0] == 0:      #自动停机选择关闭，米数出栈
            for i in range(len(api.stopStack)):
                if api.stopStack[i][2] == 6:
                    del api.stopStack[i]
                    f = open(readPath + '\\stopStack.csv', 'w', newline='')
                    csv.writer(f).writerows(api.stopStack)
                    f.close()
                    break

        if self.mainState == 0:     #准备阶段
            # if self.mainState != self.laststate:
            #     print('mainState:',self.mainState)
            # self.laststate = self.mainState

            now_qizhang = api.QXlist[15]
            now_flawStop = api.MXlist[5][2]
            # print('last',last_flawStop,'now',now_flawStop)
            qizhang_rise = 1 if ((last_qizhang == 0)&(now_qizhang == 1)) else 0
            flaw_rise = 1 if ((last_flawStop == 0)&(now_flawStop == 1)) else 0
            # print('flaw rise',flaw_rise)
            if api.MXlist[5][2]:
                if self.firstStart:
                    self.mainState = 11
                    self.firstStart = False
                else:
                    self.mainState = 1
            elif not api.MXlist[5][2]:
                self.mainState = 0
                # api.badMetersDone = [0]*len(api.badMeters)
            # last_flawStop = now_flawStop
            last_qizhang = now_qizhang
            last_flawStop = now_flawStop
            

        elif self.mainState == 1:   #检查是否刚打开气胀或瑕疵停机
            # if self.mainState != self.laststate:
            #     print('mainState:',self.mainState)
            # self.laststate = self.mainState
            if qizhang_rise or flaw_rise:
                if self.lastDeal == 2:
                    self.mainState = 14
                else:
                    self.mainState = 11
            else:
                self.mainState = 0
            
        elif self.mainState == 11:  #检查当前缺陷位置
            if self.laststate != self.mainState:
                print('mainState:',self.mainState)
            self.laststate = self.mainState 
            
            api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
            api.view1now = api.LCamera + api.cam2view[api.cameraPos][0]
            api.view2now = api.LCamera + api.cam2view[api.cameraPos][1]
            # print('v1v2',api.view1now,api.view2now,api.LCamera)
            # print('----------',api.stopStack,len(api.stopStack))
            if len(api.stopStack) == 0:     #空栈，进状态12，所有缺陷的目标停机位置进栈，排序
                self.mainState = 12

            else:                           #非空栈，则PLC内一定有一个目标停机位置，
                renewTargetsInStack()
                # if (api.lengthAct >= api.Meters_NextFlaw) | (api.lengthAct == 0):     #如果PLC已经过了当前目标位置，则遍历栈，重新找下一个位置;否则直接升速即可
                if api.lengthAct >= api.stopStack[0][1]:        #如果后面没有缺陷了，直接跑完剩下的膜料 
                    self.mainState = 0
                    # print('???')
                else:
                    if api.lengthAct < api.stopStack[-1][1]:
                        api.Meters_NextFlaw = api.stopStack[-1][1]
                        # print('????')
                    else:
                        for j in range(len(api.stopStack)-1):
                            if (api.lengthAct < api.stopStack[j][1]) & (api.lengthAct >= api.stopStack[j+1][1]):
                                api.Meters_NextFlaw = api.stopStack[j][1]
                                api.stopStack = api.stopStack[0:j+1]
                                break
                    if api.stopStack[-1][0] != 0:
                        api.badPoint = api.findPoint[api.stopStack[-1][0]]
                    if api.ordertype == 1:
                        self.totalFlaws = len(api.badMeters) - api.badPoint
                    elif api.ordertype == -1:
                        self.totalFlaws = api.badPoint
                    api.Amount_LeftFlaw = self.totalFlaws
                    print('m next',api.Meters_NextFlaw)
                    if api.Meters_NextFlaw > api.lengthAct:
                        client.write_registers (values=inverse(api.stopStack[-1][0]) + inverse(api.Amount_LeftFlaw) + inverse(api.Meters_NextFlaw), unit=2, address=188, data_format='!f')
                        client.write_registers (values=inverse(api.zhengfan[api.badPoint]), unit=2, address=300, data_format='!f')
                    # client.write_coils(50,[api.zhengfan[api.badPoint]])
                print('delta',api.lengthDelta)
                print('whole stack:',api.stopStack)
                self.mainState = 2

        elif self.mainState == 12:          #空栈时候，或者新读取了缺陷文件之后，重新把当前位置后的所有缺陷进栈
            if self.laststate != self.mainState:
                print('mainState:',self.mainState)
            self.laststate = self.mainState 
            
            api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
            api.view1now = api.LCamera + api.cam2view[api.cameraPos][0]
            api.view2now = api.LCamera + api.cam2view[api.cameraPos][1]
            # print('v1v2',api.view1now,api.view2now,api.LCamera)
            api.stopStack = []
            for i in range(len(api.badMeters)):
                if (api.zhengfan[i] == 0):
                    if ((api.badMeters[i] - api.view1now) * api.ordertype) >= 0:
                        if (findGongWeiNum(api.badMetersX[i]) != -1):
                            api.stopStack.append([api.flawNums[i], 0, 0, 0])
                elif (api.zhengfan[i] == 1) or (api.zhengfan[i] == 2):
                    if ((api.badMeters[i] - api.view2now) * api.ordertype) >= 0:
                        if (findGongWeiNum(api.badMetersX[i]) != -1):
                            api.stopStack.append([api.flawNums[i], 0, 1, 0])
            renewTargetsInStack()
            # print('whole stack:',api.stopStack)
            f = open(readPath + '\\stopStack.csv', 'w', newline='')
            csv.writer(f).writerows(api.stopStack)
            f.close()

            if api.lengthAct >= api.stopStack[0][1]:        #如果后面没有缺陷了，直接跑完剩下的膜料 
                self.mainState = 0
                # print('???')
            else:
                if api.lengthAct < api.stopStack[-1][1]:
                    api.Meters_NextFlaw = api.stopStack[-1][1]
                    # print('????')
                else:
                    for j in range(len(api.stopStack)-1):
                        if (api.lengthAct < api.stopStack[j][1]) & (api.lengthAct >= api.stopStack[j+1][1]):
                            api.Meters_NextFlaw = api.stopStack[j][1]
                            api.stopStack = api.stopStack[0:j+1]
                            break
                if api.stopStack[-1][0] != 0:
                    api.badPoint = api.findPoint[api.stopStack[-1][0]]

            self.totalFlaws = (len(api.badMeters) - api.badPoint) if (api.ordertype == 1) else api.badPoint
            if len(api.stopStack) > 0:
                self.popTargetPos()
            if api.MXlist[5][2]:
                self.mainState = 2
            elif not api.MXlist[5][2]:
                self.mainState = 0
            # self.mainState = 2

        elif self.mainState == 13:          #补偿值更新后的状态
            if self.laststate != self.mainState:
                print('mainState:',self.mainState)
            self.laststate = self.mainState

            # makeDecision(updateFlawFile(flawFileFolderPath) + '\\ErrorData.csv')
            makeDecision(api.flawFilePath + '/ErrorData.csv')

            api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
            api.view1now = api.LCamera + api.cam2view[api.cameraPos][0]
            api.view2now = api.LCamera + api.cam2view[api.cameraPos][1]
            # print('v1v2',api.view1now,api.view2now,api.LCamera)
            api.stopStack = []
            for i in range(len(api.badMeters)):
                if (api.zhengfan[i] == 0):
                    if ((api.badMeters[i] - api.view1now) * api.ordertype) >= 0:
                        if (findGongWeiNum(api.badMetersX[i]) != -1):
                            api.stopStack.append([api.flawNums[i], 0, 0, 0])
                elif (api.zhengfan[i] == 1) or (api.zhengfan[i] == 2):
                    if ((api.badMeters[i] - api.view2now) * api.ordertype) >= 0:
                        if (findGongWeiNum(api.badMetersX[i]) != -1):
                            api.stopStack.append([api.flawNums[i], 0, 1, 0])
            f = open(readPath + '\\stopStack.csv','r',newline='')
            reader = csv.reader(f)
            temp = []
            for i in reader:
                if int(i[2]) > 1:
                    temp = [int(i[0]), float(i[1]), int(i[2]), int(i[3])]
                    # 重新校正修改x补偿值后当前缺陷要停的上下卷位置
                    if temp[0] != 0:
                        self.shoujuanPosNum = findGongWeiNum(api.badMetersX[api.findPoint[temp[0]]])
                        self.upOrDown = int(abs((api.firstUpOrDown - (1 - self.shoujuanPosNum%2))))
                        if (temp[2] == 2) | (temp[2] == 3):     #PP面贴标
                            if not self.upOrDown:       #上收卷
                                temp[2] = 2
                            else:                       #下收卷
                                temp[2] = 3
                        elif (temp[2] == 4) | (temp[2] == 5):   #NY面贴标
                            if not self.upOrDown:       #上收卷
                                temp[2] = 4
                            else:                       #下收卷
                                temp[2] = 5
                    api.stopStack.append(temp)
            f.close()
            renewTargetsInStack()
            self.mainState = 11

        elif self.mainState == 14:          #裁剪后，删除裁掉的缺陷
            api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
            self.cutEnd = api.LCamera + 3.62209
            if self.cutStart > self.cutEnd:
                self.cutStart, self.cutEnd = self.cutEnd, self.cutStart     #令start <= end
            cutNums = []
            for i in range(len(api.badMeters)):     #找出哪些瑕疵是在裁剪掉的范围内的
                if (api.badMeters[i] > self.cutStart) & (api.badMeters[i] < self.cutEnd):
                    cutNums.append(api.flawNums[i])
            for i in range(len(api.stopStack)-1,-1,-1):     #停机任务栈中清除掉这些瑕疵
                if api.stopStack[i][0] in cutNums:
                    api.stopStack.pop(i)
            for i in range(len(api.shoujuanFlawStack)-1,-1,-1):     #收卷计数栈中清除这些瑕疵
                if api.shoujuanFlawStack[i][3] in cutNums:
                    api.shoujuanFlawStack.pop(i)
            count1 = 0
            for width in range(1,len(api.shoujuanWidths)-1):
                if api.shoujuanWidths[width] > 0:
                    count1 += 1
            for ii in range(1,count1+1):            #收卷计数新增接头
                self.upOrDown = int(abs((api.firstUpOrDown - (1 - ii%2))))
                api.shoujuanFlawStack.append([calShoujuanPos(-1, self.upOrDown),ii,1,0])

            if len(api.stopStack) == 0:
                self.mainState = 0
            else:                           #非空栈，则PLC内一定有一个目标停机位置，
                # renewTargetsInStack()
                if api.lengthAct >= api.stopStack[0][1]:        #如果后面没有缺陷了，直接跑完剩下的膜料 
                    self.mainState = 0
                else:
                    if api.lengthAct < api.stopStack[-1][1]:
                        api.Meters_NextFlaw = api.stopStack[-1][1]
                    else:
                        for j in range(len(api.stopStack)-1):
                            if (api.lengthAct < api.stopStack[j][1]) & (api.lengthAct >= api.stopStack[j+1][1]):
                                api.Meters_NextFlaw = api.stopStack[j][1]
                                api.stopStack = api.stopStack[0:j+1]
                                break
                    if api.stopStack[-1][0] != 0:
                        api.badPoint = api.findPoint[api.stopStack[-1][0]]
                    if api.ordertype == 1:
                        self.totalFlaws = len(api.badMeters) - api.badPoint
                    elif api.ordertype == -1:
                        self.totalFlaws = api.badPoint
                    api.Amount_LeftFlaw = self.totalFlaws
                    print('m next',api.Meters_NextFlaw)
                    if api.Meters_NextFlaw > api.lengthAct:
                        client.write_registers (values=inverse(api.stopStack[-1][0]) + inverse(api.Amount_LeftFlaw) + inverse(api.Meters_NextFlaw), unit=2, address=188, data_format='!f')
                        client.write_registers (values=inverse(api.zhengfan[api.badPoint]), unit=2, address=300, data_format='!f')
                    # client.write_coils(50,[api.zhengfan[api.badPoint]])
                print('whole stack:',api.stopStack)
                self.mainState = 2

        elif self.mainState == 2:           #判断当前目标停机是否完成  
            if self.laststate != self.mainState:
                print('mainState:',self.mainState)
            self.laststate = self.mainState 
            if len(api.stopStack) > 0:
                if (api.MXlist[1][11] & (not api.stopStack[-1][3])) | (self.handyPopFlag == 1):  #瑕疵停机已经完成，或手动打开瑕疵停机弹窗
                    if ((api.stopStack[-1][2] <= 1) & (abs(api.lengthAct-api.Meters_NextFlaw)<=0.5)) | \
                        ((api.stopStack[-1][2] > 1) & (abs(api.lengthAct-api.Meters_NextFlaw)<=0.2)) | \
                        (self.handyPopFlag == 1):   #观察区停机误差0.5，处理区停机误差0.2
                    # api.badMetersDone[api.badPoint] = 1
                        if (self.lastPointCount[0] != api.stopStack[-1][0]) | (self.lastPointCount[1] != api.stopStack[-1][2]):
                            self.lastPointCount = [api.stopStack[-1][0],api.stopStack[-1][2]]
                        
                        if api.stopStack[-1][2] > 1:
                            client.write_registers (values=inverse(api.stopStack[-1][2]), unit=2, address=560, data_format='!f')  # DealType_r_g 写入停机区代号
                            request1 = client.read_holding_registers(9,1).registers
                            buttonList = dec_to_binlist(request1[0],16)
                            buttonList[4] = 0       # DealDone
                            buttonList[5] = 1       # PopStart
                            buttonList[6] = api.cutPPorNY
                            buttonList[7] = 0       # CloseSubWin
                            command = binlist_to_int(buttonList)
                            client.write_register (value=command, unit=2, address=9)  # PopStart_b_g置1，分切机主屏弹窗

                        self.flawDealWin = flawDealPopup()
                        self.flawDealWin.show()
                        self.mainState = 3
                else:
                    pass
            elif len(api.stopStack) == 0:
                self.mainState = 0
            
        elif self.mainState == 3:           #等待工人对弹窗的操作完成     
            if self.laststate != self.mainState:
                print('mainState:',self.mainState)
            self.laststate = self.mainState    

            # if not api.dealDoneFlag:
            #     pass
            # else:
            #     api.dealDoneFlag = 0
            #     api.stopStack[-1][3] = 1
            #     self.mainState = 4

            self.handyPopFlag = 0
            request1 = client.read_holding_registers(9,1).registers
            buttonList = dec_to_binlist(request1[0],16)         
            if api.dealDoneFlag and (not buttonList[4]):        # 在上位机点击了完成
                print('上位机点击“完成”')
                api.dealDoneFlag = 0
                api.stopStack[-1][3] = 1
                buttonList[7] = 1       
                command = binlist_to_int(buttonList)
                client.write_register (value=command, unit=2, address=9)    # 关闭主屏幕弹窗
                self.mainState = 4
            elif buttonList[4] and (not api.dealDoneFlag):      # 在主屏幕点击了完成
                print('主屏幕点击“完成”')
                self.flawDealWin.destroy()
                result1 = client.read_holding_registers(562,2).registers
                api.dealtype = int(dec_to_float(result1[0],result1[1]))
                api.stopStack[-1][3] = 1
                buttonList[4] = 0       # %MW9.4 DealDone_b_g
                command = binlist_to_int(buttonList)
                client.write_register (value=command, unit=2, address=9)
                self.mainState = 4
            elif buttonList[4] and api.dealDoneFlag:            # 在上位机和主屏幕都点击了完成，以上位机的操作为准
                print('上位机与主屏幕点击“完成”')
                api.dealDoneFlag = 0
                api.stopStack[-1][3] = 1
                buttonList[4] = 0       # %MW9.4 DealDone_b_g
                command = binlist_to_int(buttonList)
                client.write_register (value=command, unit=2, address=9)
                self.mainState = 4
            else:       # 未完成处理
                pass
        
        elif self.mainState == 4:           #根据工人在弹窗中的操作，确定对当前停机的处理方式
            if self.laststate != self.mainState:
                print('mainState:',self.mainState)
            self.laststate = self.mainState
            if api.stopStack[-1][3]:
                api.lastStackPop = api.stopStack.pop()      #出栈
                print('after pop:',api.stopStack)
                if len(api.stopStack) >= 0:          #还有剩余停机点
                    if api.lastStackPop[0] != 0:
                        self.shoujuanPosNum = findGongWeiNum(api.badMetersX[api.findPoint[api.lastStackPop[0]]])
                    self.upOrDown = int(abs((api.firstUpOrDown - (1 - self.shoujuanPosNum%2))))     #根据x坐标判断收卷在第几工位，进而判断在上收卷还是下收卷
                    if (api.lastStackPop[2] == 0) | (api.lastStackPop[2] == 1):
                        if self.totalFlaws > 0:
                            self.totalFlaws -= 1
                    if api.dealtype == 0:           #不处理，直接走
                        pass

                    elif api.dealtype == 1:         #确认，瑕疵计数
                        pass

                    elif api.dealtype == 2:         #裁剪，接带计数
                        api.LCamera = (api.fangjuanL - api.lengthDelta) * api.ordertype
                        self.cutStart = api.LCamera + 3.62209

                    elif api.dealtype == 3:         #双面贴标，瑕疵计数，push两个停机点
                        if not self.upOrDown:       #上收卷
                            api.stopStack.append([api.lastStackPop[0], 0, 2, 0])
                            # if api.cutPPorNY == 0:  #如果切PP面，则收卷位置也要停机；切NY面则不用
                            api.stopStack.append([api.lastStackPop[0], 0, 4, 0])
                        else:                       #下收卷
                            api.stopStack.append([api.lastStackPop[0], 0, 3, 0])
                            # if api.cutPPorNY == 0:  #如果切PP面，则收卷位置也要停机；切NY面则不用
                            api.stopStack.append([api.lastStackPop[0], 0, 5, 0])

                    elif api.dealtype == 4:         #NY面贴标，瑕疵计数，push收卷处停机点
                        if not self.upOrDown:       #上收卷
                            api.stopStack.append([api.lastStackPop[0], 0, 4, 0])
                        else:                       #下收卷
                            api.stopStack.append([api.lastStackPop[0], 0, 5, 0])

                    elif api.dealtype == 5:         #PP面贴标，瑕疵计数，push切刀处停机点
                        if not self.upOrDown:       #上收卷
                            api.stopStack.append([api.lastStackPop[0], 0, 2, 0])
                        else:                       #下收卷
                            api.stopStack.append([api.lastStackPop[0], 0, 3, 0])
                    
                    if api.dealtype != 0:
                        if api.lastStackPop[2] <= 1:    #如果停在观察区
                            if api.dealtype != 2:       #接带，每个卷位的接带数量都要加1
                            #     count1 = 0
                            #     for width in range(1,len(api.shoujuanWidths)-1):
                            #         if api.shoujuanWidths[width] > 0:
                            #             count1 += 1
                            #     for ii in range(1,count1+1):
                            #         self.upOrDown = int(abs((api.firstUpOrDown - (1 - ii%2))))
                            #         api.shoujuanFlawStack.append([calShoujuanPos(api.lastStackPop[2], self.upOrDown),ii,1])

                            # else:
                                api.shoujuanFlawStack.append([calShoujuanPos(api.lastStackPop[2], self.upOrDown),self.shoujuanPosNum,0,api.lastStackPop[0]])
                            api.shoujuanFlawStack.sort(key = lambda x:x[0], reverse = True)
                            f6 = open(readPath + '\\shoujuanStack.csv','w',newline='')
                            csv.writer(f6).writerows(api.shoujuanFlawStack)
                            f6.close()

                    renewTargetsInStack()
                    self.popTargetPos()             #向PLC弹出新的目标位置
                    if api.dealtype != 2:
                        request1 = client.read_holding_registers(9,1).registers
                        buttonList = dec_to_binlist(request1[0],16)
                        buttonList[2] = 1
                        command = binlist_to_int(buttonList)
                    
                        client.write_register (value=command, unit=2, address=9)    #自动打开瑕疵停机选择  
                        if len(api.stopStack) > 0: 
                            if api.lengthAct-api.stopStack[-1][1] > 0.35:
                                self.mainState = 11
                            else:
                                self.mainState = 2
                        elif len(api.stopStack) == 0:
                            self.mainState = 0
                    elif api.dealtype == 2:
                        self.mainState = 0

                    self.lastDeal = api.dealtype    
                    api.dealtype = 0
                    client.write_registers (values=inverse(0), unit=2, address=562, data_format='!f')  # DealType_r_g 复位为0
                    request1 = client.read_holding_registers(9,1).registers
                    buttonList = dec_to_binlist(request1[0],16)
                    buttonList[4] = 0       # %MW9.4 DealDone_b_g
                    command = binlist_to_int(buttonList)
                    client.write_register (value=command, unit=2, address=9)
                    # if len(api.stopStack) > 0: 
                    #     self.mainState = 11
                    # elif len(api.stopStack) == 0:
                    #     self.mainState = 0
                else:                               #无其他停机点，回到初始状态，等剩余膜料跑完
                    self.mainState = 0
            else:
                self.mainState = 11

        # print('state',self.mainState)

    def popTargetPos(self):     # 向PLC发送目标停机位置
        if api.stopStack[-1][0] != 0:
            api.badPoint = api.findPoint[api.stopStack[-1][0]]
        api.Meters_NextFlaw = api.stopStack[-1][1]
        api.Amount_LeftFlaw = self.totalFlaws if (self.totalFlaws >= 0) else 0
        if api.Meters_NextFlaw > api.lengthAct:
            client.write_registers (values=inverse(api.stopStack[-1][0]) + inverse(api.Amount_LeftFlaw) + inverse(api.Meters_NextFlaw), unit=2, address=188, data_format='!f')
            client.write_registers (values=inverse(api.zhengfan[api.badPoint]), unit=2, address=300, data_format='!f')
        # client.write_coils(50,[api.zhengfan[api.badPoint]])
        api.lastStackPop = api.stopStack[-1]      #出栈

    def dataShow(self):         # 显示数据
        #spinbox
        self.spinBox.setRange(0,10000)
        # self.spinBox_2.setRange(0,10000)
        self.spinBox_3.setRange(0,10000)
        self.spinBox_4.setRange(0,10000)
        self.spinBox_5.setRange(0,10000)
        self.spinBox_6.setRange(0,10000)
        self.spinBox_7.setRange(0,10000)
        self.spinBox_8.setRange(0,10000)
        self.spinBox_9.setRange(0,10000)
        self.spinBox_10.setRange(0,10000)
        self.spinBox_11.setRange(0,10000)
        self.spinBox_12.setRange(0,10000)
        self.spinBox_13.setRange(0,10000)
        self.spinBox_14.setRange(0,10000)
        self.spinBox_15.setRange(0,10000)
        self.spinBox_16.setRange(0,10000)
        self.spinBox_17.setRange(0,10000)
        self.spinBox_18.setRange(0,10000)
        self.spinBox_19.setRange(0,10000)
        self.spinBox_20.setRange(0,100000000)
        # self.spinBox_21.setRange(0,10000)
        self.spinBox_22.setRange(0,10000)
        self.spinBox_23.setRange(0,10000)
        self.spinBox_24.setRange(0,10000)
        self.spinBox_25.setRange(0,10000)
        self.spinBox_26.setRange(0,10000)
        self.spinBox_27.setRange(0,10000)
        self.spinBox_28.setRange(0,10000)
        self.spinBox_29.setRange(0,10000)
        self.spinBox_30.setRange(0,10000)
        self.textEdit_2.setRange(-1000000,1000000)
        self.textEdit_3.setRange(-1000000,1000000)
        self.textEdit_9.setRange(-1000000,1000000)
        self.textEdit_10.setRange(-1000000,1000000)
        self.textEdit_11.setRange(-1000000,1000000)
        self.textEdit_4.setRange(0,10000)
        self.textEdit_12.setRange(-1000000,1000000)
        self.textEdit_13.setRange(-1000000,1000000)

        # for k in range(len(self.spinBoxName)):
        #     if self.spinBoxName[k].hasFocus():
        #         print("正在输入")
        #     else:
        #         self.spinBoxName[k].setValue(self.displayData[k])


        self.textEdit_2.setValue(api.offsetNY)
        self.textEdit_3.setValue(api.offsetPP)
        #radioButton
        if api.MXlist[5][1] == 0:           #上放卷
            self.radioButton.setChecked(True)
            self.radioButton_2.setChecked(False)
            # print('上放卷')
        elif api.MXlist[5][1] == 1:         #下放卷
            self.radioButton.setChecked(False)
            self.radioButton_2.setChecked(True)
            # print('下放卷')
        if api.xintongSizeUp == 0:      #上芯筒3寸
            self.radioButton_3.setChecked(True)
            self.radioButton_4.setChecked(False)
        elif api.xintongSizeUp == 4:    #上芯筒6寸
            self.radioButton_3.setChecked(False)
            self.radioButton_4.setChecked(True)
        if api.xintongSizeDown == 0:    #下芯筒3寸
            self.radioButton_5.setChecked(True)
            self.radioButton_6.setChecked(False)
        elif api.xintongSizeDown == 4:  #下芯筒6寸
            self.radioButton_5.setChecked(False)
            self.radioButton_6.setChecked(True)
        
    def continueShow(self):
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        #LCDNumber
        self.lcdNumber.setPlainText(str(round(api.speedNow,2)))
        self.lcdNumber_2.setPlainText(str(round(api.lengthAct,2)))
        self.lcdNumber_3.setPlainText(str(round(api.LengthSum,2)))
        self.lcdNumber_4.setPlainText(str(round(api.fangjuanRDown,2)))
        try:
            self.lcdNumber_5.setPlainText(str(round(api.fangjuanActFDown/api.Mo_WidthDown,2)))
        except ZeroDivisionError:
            self.lcdNumber_5.setPlainText(str(round(api.fangjuanActFDown,2)))
        self.lcdNumber_6.setPlainText(str(round(api.fangjuanActFDown,2)))
        self.lcdNumber_7.setPlainText(str(round(api.houshoujuanR,2)))   #上收卷半径
        self.lcdNumber_8.setPlainText(str(round(api.yagunBackUp,2)))    #上跟随后退距离
        self.lcdNumber_9.setPlainText(str(round(api.yagunBackDown,2)))  #下跟随后退距离
        self.lcdNumber_10.setPlainText(str(round(api.QianshoujuanR,2))) #下收卷半径
        try:
            self.lcdNumber_11.setPlainText(str(round(api.shoujuanFSetUp/api.Mo_WidthDown,2)))
        except ZeroDivisionError:
            self.lcdNumber_11.setPlainText(str(round(api.shoujuanFSetUp,2)))
        self.lcdNumber_12.setPlainText(str(round(api.targetUp,2)))
        try:
            self.lcdNumber_13.setPlainText(str(round(api.shoujuanFSetDown/api.Mo_WidthDown,2)))
        except ZeroDivisionError:
            self.lcdNumber_13.setPlainText(str(round(api.shoujuanFSetDown,2)))
        self.lcdNumber_14.setPlainText(str(round(api.targetDown,2)))
        self.lcdNumber_15.setPlainText(str(round(api.SpeedLmitHigh,2)))

        # pushButton
        if api.MXlist[3][13] == 1:          #换底刀
            self.pushButton.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[3][13] == 0:
            self.pushButton.setStyleSheet("background-color: #ffffff")
        if api.QXlist[19] == 1:             #伺服使能
            self.pushButton_2.setStyleSheet("background-color: #00ff00")
        elif api.QXlist[19] == 0:
            self.pushButton_2.setStyleSheet("background-color: #ffffff")
        if api.MXlist[1][7] == 1:           #张力开
            self.pushButton_7.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[1][7] == 0:
            self.pushButton_7.setStyleSheet("background-color: #ffffff")
        if api.MXlist[1][15] == 1:          #预收紧
            self.pushButton_9.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[1][15] == 0:
            self.pushButton_9.setStyleSheet("background-color: #ffffff")
        if api.MXlist[3][14] == 1:          #上跟随关
            self.pushButton_10.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[3][14] == 0:
            self.pushButton_10.setStyleSheet("background-color: #ffffff")
        if api.MXlist[3][15] == 1:          #下跟随关
            self.pushButton_13.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[3][15] == 0:
            self.pushButton_13.setStyleSheet("background-color: #ffffff")
        if api.QXlist[12] == 1:             #点动
            self.pushButton_14.setStyleSheet("background-color: #00ff00")
        elif api.QXlist[12] == 0:
            self.pushButton_14.setStyleSheet("background-color: #ffffff")
        if api.QXlist[50] == 1:             #上压带
            self.pushButton_11.setStyleSheet("background-color: #00ff00")
        elif api.QXlist[50] == 0:
            self.pushButton_11.setStyleSheet("background-color: #ffffff")
        if api.QXlist[51] == 1:             #下压带
            self.pushButton_12.setStyleSheet("background-color: #00ff00")
        elif api.QXlist[51] == 0:
            self.pushButton_12.setStyleSheet("background-color: #ffffff")
        if api.MXlist[3][13] == 1:          #底刀定位停机
            self.pushButton_20.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[3][13] == 0:
            self.pushButton_20.setStyleSheet("background-color: #ffffff")
        if api.MXlist[5][2] == 1:          #瑕疵停机选择
            self.pushButton_22.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[5][2] == 0:
            self.pushButton_22.setStyleSheet("background-color: #ffffff")
        if self.drawLineFlag==1:
            receive()
        try:
            if (api.zhengfan[api.badPoint] == 0):
                self.textEdit.setPlainText('PP面')
            elif (api.zhengfan[api.badPoint] == 1):
                self.textEdit.setPlainText('NY面')
            elif (api.zhengfan[api.badPoint] == 2):
                self.textEdit.setPlainText('针孔')
            self.textEdit_4.setValue(api.badMetersX[api.badPoint])
        except Exception:
            print('e',api.badPoint,api.zhengfan)
        self.textBrowser.setText(api.numNow)

        if api.ordertype == 1:
            self.pushButton_19.setStyleSheet("background-color: #ffffff")
            self.pushButton_19.setText(_translate("MainWindow", "升序"))
        elif api.ordertype == -1:
            self.pushButton_19.setStyleSheet("background-color: #00ff00")
            self.pushButton_19.setText(_translate("MainWindow", "降序"))
            

    def pressedFcn(self,mw,mx,stay):     # 鼠标按下的函数
        print('pressed:',mw,mx,stay)
        if mw!=999:
            request1 = client.read_holding_registers(mw,1).registers
            buttonList = dec_to_binlist(request1[0],16)
            if stay:    #如果是取反的按键
                buttonList[mx] = 1 - buttonList[mx]
            else:       #按1松0的按键
                buttonList[mx] = 1
            command = binlist_to_int(buttonList)
            if api.uiEA:
                client.write_register (value=command, unit=2, address=mw)  

                if mw == 9:
                    if buttonList[mx] == 1:
                        self.mainState = 11
                    else:
                        self.mainState = 0

        elif mw==999:   #要操作的是输出继电器
            onebit = client.read_coils(mx,1).bits
            if stay:
                onebit[0] = 1 - onebit[0]
            else:
                onebit[0] = 1
            if api.uiEA:
                client.write_coils(mx,onebit)

    def releasedFcn(self,mw,mx,stay):    # 鼠标抬起的函数
        print('released:',mw,mx,stay)
        if mw!= 999:
            request1 = client.read_holding_registers(mw,1).registers
            buttonList = dec_to_binlist(request1[0],16)
            if (mw == 9):
                if buttonList[2] == 1:
                    print('重新校正目标位置')
                    self.mainState = 11
            if not stay:    #如果是按1松0的按键，就发个0回去
                buttonList[mx] = 0
                command = binlist_to_int(buttonList)
                if api.uiEA:
                    client.write_register (value=command, unit=2, address=mw)  
        elif mw == 999:
            onebit = client.read_coils(mx,1).bits
            if not stay:
                pass
                if api.uiEA:
                    client.write_coils(mx,onebit)

    def radioBtnChange(self,a):
        print(a,'is changed')
        if a == 1:
            if self.radioButton.isChecked():
                print('上放卷')
                request1 = client.read_holding_registers(9,1).registers
                buttonList = dec_to_binlist(request1[0],16)
                buttonList[1] = 0
                command = binlist_to_int(buttonList)
                if api.uiEA:
                    client.write_register (value=command, unit=2, address=9)
            elif self.radioButton_2.isChecked():
                print('下放卷')
                request1 = client.read_holding_registers(9,1).registers
                buttonList = dec_to_binlist(request1[0],16)
                buttonList[1] = 1
                command = binlist_to_int(buttonList)
                if api.uiEA:
                    client.write_register (value=command, unit=2, address=9)
        elif a == 3:
            if self.radioButton_3.isChecked():
                print('上收卷3寸')
                if api.uiEA:
                    client.write_registers(values=[0], unit=2, address=98, data_format='!f')
            elif self.radioButton_4.isChecked():
                print('上收卷6寸')
                if api.uiEA:
                    client.write_registers(values=inverse(4), unit=2, address=98, data_format='!f')
        elif a == 5:
            if self.radioButton_5.isChecked():
                print('下收卷3寸')
                if api.uiEA:
                    client.write_registers(values=[0], unit=2, address=100, data_format='!f')
            elif self.radioButton_6.isChecked():
                print('下收卷6寸')
                if api.uiEA:
                    client.write_registers(values=inverse(4), unit=2, address=100, data_format='!f')
        elif a == 7:
            if self.radioButton_13.isChecked():
                print('相机安装在上方')
                api.cameraPos = 0
            elif self.radioButton_14.isChecked():
                print('相机安装在下方')
                api.cameraPos = 1
            saveTempData()

    def qtInput(self,a):
        if api.uiEA:
            print(a,' is changed.')
            api.Meters_Stop        = self.spinBox.value()
            # api.SpeedLmitHigh       = self.spinBox_2.value()
            api.lengthSet           = self.spinBox_3.value()
            api.xintong_widthDown   = self.spinBox_4.value()
            api.fangjuanFSetDown    = self.spinBox_5.value()
            api.Mo_WidthDown        = self.spinBox_6.value()
            api.Mo_thickDown        = self.spinBox_7.value()
            api.tongkuanUp          = self.spinBox_8.value()
            api.circlesUp           = self.spinBox_9.value()
            api.shoujuanFSetUp      = self.spinBox_10.value()
            api.zhuiduUp            = self.spinBox_11.value()
            api.shoujuanFSetDown    = self.spinBox_12.value()
            api.zhuiduDown          = self.spinBox_13.value()
            api.circlesDown         = self.spinBox_14.value()
            api.tongkuanDown        = self.spinBox_15.value()
            api.SpeedLmitHigh       = self.spinBox_16.value()
            api.Accelerate_time     = self.spinBox_17.value()
            api.Slow_time           = self.spinBox_18.value()
            api.Stop_time           = self.spinBox_19.value()
            api.badPoint            = api.findPoint[self.spinBox_20.value()] if (self.spinBox_20.value() != 0) else api.badPoint
            # api.fangjuanSpeedRatio  = self.spinBox_21.value()
            api.speedJog            = self.spinBox_22.value()
            api.didaoDingWei        = self.spinBox_23.value()
            api.deltaP              = self.spinBox_25.value()
            api.Lcut                = self.spinBox_26.value()
            api.alarmR              = self.spinBox_28.value()
            api.jiedaijinchi        = self.spinBox_29.value()
            api.offsetNY            = self.textEdit_2.value()
            api.offsetPP            = self.textEdit_3.value()
            api.offsetPPUp          = self.textEdit_10.value()
            api.offsetPPDown        = self.textEdit_9.value()
            api.offsetX             = self.textEdit_11.value()
            api.offsetNYUp          = self.textEdit_12.value()
            api.offsetNYDown        = self.textEdit_13.value()
            
            # if (a == -1) | (self.sender() == self.textEdit_2) | (self.sender() == self.textEdit_3):
            #     self.mainState = 13
            #     saveTempData()
            if (self.sender() == self.textEdit_2) | (self.sender() == self.textEdit_3):
                self.mainState = 13
                saveTempData()
            if (a == -1):
                if self.sender() == self.textEdit_11:  #x补偿
                    global oriXlist
                    api.badMetersX = oriXlist[:]
                    for i in range(len(api.badMeters)):
                        api.badMetersX[i] = float(api.badMetersX[i]) + api.offsetX
                        if api.biaoliInverseFlag:
                            api.zhengfan[i] = 1-api.zhengfan[i]
                            if api.cutPPorNY == 0:  #表里反了，切PP面
                                api.badMetersX[i] = api.Mo_WidthDown - api.badMetersX[i]
                        else:
                            if api.cutPPorNY == 1:  #表里没反，切NY面
                                api.badMetersX[i] = api.Mo_WidthDown - api.badMetersX[i]
                    for i in api.stopStack:
                    # 重新校正修改x补偿值后当前缺陷要停的上下卷位置
                        if i[0] != 0:
                            self.shoujuanPosNum = findGongWeiNum(api.badMetersX[api.findPoint[i[0]]])
                            print(i[0],api.badMetersX[api.findPoint[i[0]]])
                            self.upOrDown = int(abs((api.firstUpOrDown - (1 - self.shoujuanPosNum%2))))
                            if (i[2] == 2) | (i[2] == 3):     #PP面贴标
                                if not self.upOrDown:       #上收卷
                                    i[2] = 2
                                else:                       #下收卷
                                    i[2] = 3
                            elif (i[2] == 4) | (i[2] == 5):   #NY面贴标
                                if not self.upOrDown:       #上收卷
                                    i[2] = 4
                                else:                       #下收卷
                                    i[2] = 5
                renewTargetsInStack()
                saveTempData()

            if a != -1:
                client.write_registers (values=inverse(self.sender().value()), unit=2, address=get_addr(a), data_format='!f')
            if self.sender() == self.spinBox_20:    #手动选择瑕疵编号
                for i in range(len(api.stopStack)-1, -1, -1):
                    if api.stopStack[i][0] == self.spinBox_20:
                        api.Meters_NextFlaw =  api.stopStack[i][1]
                api.Amount_LeftFlaw = (len(api.badMeters)-api.badPoint) if (api.ordertype == 1) else api.badPoint  #剩余缺陷数量
                self.dataShow()
                if len(api.stopStack) > 0:
                    for i in range(len(api.stopStack)):
                        if api.stopStack[i][0] != 0:
                            if api.findPoint[api.stopStack[i][0]] > api.badPoint:
                                api.stopStack = api.stopStack[0:i]
                
                if api.Meters_NextFlaw > api.lengthAct:
                    client.write_registers (values=inverse(api.flawNums[api.badPoint]) + inverse(api.Amount_LeftFlaw) + inverse(api.Meters_NextFlaw), unit=2, address=188, data_format='!f')

    def createDataSave(self):       # 数据保存
        api.dataSaveFlag = 1 - api.dataSaveFlag
        if api.dataSaveFlag == 1:
            self.pushButton_17.setStyleSheet("background-color: #00ff00")
            self.pushButton_17.setFont(QtGui.QFont("新宋体",10,QtGui.QFont.Bold))
            api.dataclose = 0
            thread1 = dataThread(1,'Thread1',0)
            thread1.setDaemon(True)
            print('保存数据开')
            thread1.start()
        elif api.dataSaveFlag == 0:
            self.pushButton_17.setStyleSheet("background-color: #ffffff")
            self.pushButton_17.setFont(QtGui.QFont("新宋体",10,QtGui.QFont.Bold))
            api.dataclose = 1
            print('保存数据关')

    def createDrawLine(self):       # 曲线绘制
        self.drawLineFlag = 1 - self.drawLineFlag
        if self.drawLineFlag == 1:
            self.pushButton_16.setStyleSheet("background-color: #00ff00")
            self.pushButton_16.setFont(QtGui.QFont("新宋体",10,QtGui.QFont.Bold))
            lineWin.show()
            
            print('图像绘制开')
        elif self.drawLineFlag == 0:
            self.pushButton_16.setStyleSheet("background-color: #ffffff")
            self.pushButton_16.setFont(QtGui.QFont("新宋体",10,QtGui.QFont.Bold))
            lineWin.close()
            print('图像绘制关')

    def show_pic(self):              # 显示缺陷图片
        # imagePath0 = updateFlawFile(flawPicFolderPath) + '\\{0}.bmp'.format(str(api.badPics[api.badPoint]).zfill(6))
        imagePath0 = api.flawFilePath + '\\{0}.bmp'.format(str(api.badPics[api.badPoint]).zfill(6))
        print('当前第',api.badPoint)
        print('image path',imagePath0)
        os.startfile(imagePath0)
    
    def openFlawFile(self):         # 打开缺陷文件
        # flawFilePath = updateFlawFile(flawFileFolderPath) + '\\ErrorData.csv'
        flawFilePath = api.flawFilePath + '/ErrorData.csv'
        os.startfile(flawFilePath)
    
    def readFlawFile(self):         # 读取缺陷文件
        api.photoclose = 1
        # makeDecision(updateFlawFile(flawFileFolderPath) + '\\ErrorData.csv')
        request1 = client.read_holding_registers(9,1).registers
        buttonList = dec_to_binlist(request1[0],16)
        buttonList[2] = 0
        command = binlist_to_int(buttonList)
    
        client.write_register (value=command, unit=2, address=9)    #自动关闭瑕疵停机选择  

        root = tk.Tk()
        root.withdraw()
        tempread = filedialog.askdirectory(initialdir=flawFileFolderPath)
        if (tempread != ''):
            api.flawFilePath = tempread
        print(api.flawFilePath)
        makeDecision(api.flawFilePath + '/ErrorData.csv')
        f5 = open(readPath + '\\flawPath.csv','w',newline='')
        csv.writer(f5).writerow([api.flawFilePath])
        f5.close()

        time.sleep(0.5)
        api.photoclose = 0
        target_host = "10.30.76.27"
        target_port = 8500
        global client2
        #建立socket对象
        socket.setdefaulttimeout(3)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #连接客户端
        print('正在与相机建立连接...')
        try:
            client2.connect((target_host,target_port))
        except Exception:
            print('连接失败！请检查网线连接与相机状态')
            time.sleep(3)
        thread3 = photoThread(3,'Thread3',0)
        thread3.setDaemon(True)
        thread3.start()
        print('正在读取相机数据...')
        self.mainState = 12

    def openShoujuanSet(self):
        self.shoujuanSetWin = shoujuanGongwei()
        self.shoujuanSetWin.show()
        
    def addFlaw(self):              #新增贴标
        if int(self.spinBox_21.value()) > 0:
            self.shoujuanPosNum = int(self.spinBox_21.value())
            self.upOrDown = int(abs((api.firstUpOrDown - (1 - self.shoujuanPosNum%2))))
            if self.shoujuanPosNum in api.shoujuanFlawInfo.keys():
                # print('???',api.shoujuanFlawInfo[self.shoujuanPosNum])
                api.shoujuanFlawInfo[self.shoujuanPosNum][0].append(api.lengthAct)
            else:
                api.shoujuanFlawInfo[self.shoujuanPosNum] = [[api.lengthAct],[]]
            df = pd.DataFrame(api.shoujuanFlawInfo)
            df.to_csv(readPath + '\\tempWindInfo.csv',encoding='utf-8',mode='w',index=False,header=True)
            print('wind info:',api.shoujuanFlawInfo)
    
    def addJietou(self):            #新增接头
        count1 = 0
        for width in range(1,len(api.shoujuanWidths)-1):
            if api.shoujuanWidths[width] > 0:
                count1 += 1
        for ii in range(1,count1+1):
            self.upOrDown = int(abs((api.firstUpOrDown - (1 - ii%2))))
            api.shoujuanFlawStack.append([calShoujuanPos(-1,self.upOrDown),ii,1,0])
        api.shoujuanFlawStack.sort(key = lambda x:x[0], reverse = True)
        print(api.shoujuanFlawStack)
        f6 = open(readPath + '\\shoujuanStack.csv','w',newline='')
        csv.writer(f6).writerows(api.shoujuanFlawStack)
        f6.close()
    
    def handyPop(self):
        self.handyPopFlag = 1   # 启动手动弹窗

    def changeOrder(self):  #切换标码升降序
        if api.ordertype == 1:
            api.ordertype = -1
            self.pushButton_19.setStyleSheet("background-color: #00ff00")
            self.pushButton_19.setText(_translate("MainWindow", "降序"))
            print('当前标码降序')
        elif api.ordertype == -1:
            api.ordertype = 1
            self.pushButton_19.setStyleSheet("background-color: #ffffff")
            self.pushButton_19.setText(_translate("MainWindow", "升序"))
            print('当前标码升序')
        saveTempData()

    def knifeOpen(self):  #弹出刀库
        self.knifeSetFlag = 1 - self.knifeSetFlag
        knifeUsePath = readPath + '\\KnifeFile.csv'
        api.daoRecs = {}
        if os.path.exists(knifeUsePath):
            f3 = open(knifeUsePath,'r',newline='')
            reader = csv.reader(f3)
            tt = 0
            for a in reader:
                if tt == 0:
                    tt += 1
                elif tt == 1:
                    api.daoRecs[int(a[0])] = float(a[1])
            f3.close()
        if self.knifeSetFlag == 1:
            self.knifeButton.setStyleSheet("background-color: #00ff00")
            knifeWin.show()
            # print('------------------------')
        elif self.knifeSetFlag == 0:
            self.knifeButton.setStyleSheet("background-color: #ffffff")
            knifeWin.close()  

    def peifangOpen(self):
        self.peifangSetFlag = 1-self.peifangSetFlag
        if self.peifangSetFlag == 1:
            self.peifangButton.setStyleSheet("background-color: #00ff00")
            peiFangWin.show()
        elif self.peifangSetFlag == 0:
            self.peifangButton.setStyleSheet("background-color: #ffffff")
            peiFangWin.close()


class myKnifeAndPeifang(QtWidgets.QMainWindow,Ui_KnifeEdit):  #刀具操作界面
    def __init__(self):
        super(myKnifeAndPeifang,self).__init__()
        self.setupUi(self)

        self.pushButton_17.clicked.connect(self.OpenKnifeFile)
        self.pushButton_5.clicked.connect(lambda:self.meterClickedButton(self.spinBox_2.value()))
        self.pushButton_6.clicked.connect(lambda:self.meterClickedButton(self.spinBox_3.value()))
        self.pushButton_7.clicked.connect(lambda:self.meterClickedButton(self.spinBox_4.value()))
        self.pushButton_8.clicked.connect(lambda:self.meterClickedButton(self.spinBox_5.value()))
        self.pushButton_9.clicked.connect(lambda:self.meterClickedButton(self.spinBox_6.value()))
        self.pushButton_10.clicked.connect(lambda:self.meterClickedButton(self.spinBox_7.value()))
        self.pushButton_11.clicked.connect(lambda:self.meterClickedButton(self.spinBox_8.value()))
        self.pushButton_12.clicked.connect(lambda:self.meterClickedButton(self.spinBox_9.value()))
        self.pushButton_13.clicked.connect(lambda:self.meterClickedButton(self.spinBox_10.value()))
        self.pushButton_14.clicked.connect(lambda:self.meterClickedButton(self.spinBox_11.value()))
        self.pushButton_15.clicked.connect(lambda:self.meterClickedButton(self.spinBox_12.value()))
        self.pushButton_16.clicked.connect(lambda:self.meterClickedButton(self.spinBox_13.value()))

        self.fileFlag = 0
        self.daoNum = [self.spinBox_2,self.spinBox_3,self.spinBox_4,self.spinBox_5,self.spinBox_6,\
            self.spinBox_7,self.spinBox_8,self.spinBox_9,self.spinBox_10,self.spinBox_11,self.spinBox_12,self.spinBox_13]
        self.doubleSpinBoxNum = [self.doubleSpinBox,self.doubleSpinBox_2,self.doubleSpinBox_3,self.doubleSpinBox_4,self.doubleSpinBox_5,self.doubleSpinBox_6,\
            self.doubleSpinBox_7,self.doubleSpinBox_8,self.doubleSpinBox_9,self.doubleSpinBox_10,self.doubleSpinBox_11,self.doubleSpinBox_12]
        self.checkboxes = [self.checkBox,self.checkBox_2,self.checkBox_3,self.checkBox_4,self.checkBox_5,self.checkBox_6,\
                            self.checkBox_7,self.checkBox_8,self.checkBox_9,self.checkBox_10,self.checkBox_11,self.checkBox_12]
        self.pushbuttons = [self.pushButton_5,self.pushButton_6,self.pushButton_7,self.pushButton_8,self.pushButton_9,self.pushButton_10,\
                            self.pushButton_11,self.pushButton_12,self.pushButton_13,self.pushButton_14,self.pushButton_15,self.pushButton_16]

        # self.daoFile = pd.read_csv(knifePath,encoding='GBk',index_col=0)
        
        for i in range(len(self.daoNum)):
            self.daoNum[i].editingFinished.connect(self.D1)
            self.daoNum[i].setRange(0,10000)
            self.doubleSpinBoxNum[i].setRange(0,1000000)

        for i in range(12):
            self.daoNum[i].setValue(api.knifeUsing[i])
            # print('ttttte_',api.daoRecs,'\n',api.knifeUsing)
            self.doubleSpinBoxNum[i].setValue(api.daoRecs[int(api.knifeUsing[i])])
            self.daoNum[i].setEnabled(api.knifeEA[i])
            self.doubleSpinBoxNum[i].setEnabled(api.knifeEA[i])
            self.pushbuttons[i].setEnabled(api.knifeEA[i])
            self.checkboxes[i].setChecked(api.knifeEA[i])
        self.alarmMeter()
        self.checkboxes[0].toggled.connect(lambda: self.renewEAState(0))
        self.checkboxes[1].toggled.connect(lambda: self.renewEAState(1))
        self.checkboxes[2].toggled.connect(lambda: self.renewEAState(2))
        self.checkboxes[3].toggled.connect(lambda: self.renewEAState(3))
        self.checkboxes[4].toggled.connect(lambda: self.renewEAState(4))
        self.checkboxes[5].toggled.connect(lambda: self.renewEAState(5))
        self.checkboxes[6].toggled.connect(lambda: self.renewEAState(6))
        self.checkboxes[7].toggled.connect(lambda: self.renewEAState(7))
        self.checkboxes[8].toggled.connect(lambda: self.renewEAState(8))
        self.checkboxes[9].toggled.connect(lambda: self.renewEAState(9))
        self.checkboxes[10].toggled.connect(lambda: self.renewEAState(10))
        self.checkboxes[11].toggled.connect(lambda: self.renewEAState(11))

        self.spinBox_14.setRange(0,10000000)
        self.spinBox_14.setValue(api.knifeAlarmSet)
        self.spinBox_14.editingFinished.connect(self.alarmSet)

        self.lastMeter = api.lengthAct
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.mainTimer)
        self.timer.start(5000)

    def mainTimer(self):
        # print('one sec')
        for i in range(12):
            if self.checkboxes[i].isChecked():
                api.knifeUsing[i] = int(self.daoNum[i].value())
                if api.lengthAct > self.lastMeter:
                    api.daoRecs[api.knifeUsing[i]] += (api.lengthAct - self.lastMeter)
                    self.doubleSpinBoxNum[i].setValue(api.daoRecs[api.knifeUsing[i]])
        self.lastMeter = api.lengthAct
        # try:
        #     daoData = pd.read_csv(knifePath,encoding='GBK',index_col=0)
        #     for i in api.daoRecs.keys():
        #         daoData.loc[i,'运行米长'] = api.daoRecs[i]
        #     daoData.to_csv(knifePath,encoding='GBK',index=True,header=True)
        #     dfdf = pd.DataFrame(columns=api.knifeUsing,index=None)
        #     dfdf.loc[1] = api.knifeEA
        #     dfdf.to_csv(readPath + '\\knifeUsing.csv',index=False)
        # except Exception as e:
        #     print(e)
        self.alarmMeter()
        # dfdf = pd.DataFrame(columns=api.knifeUsing,index=None)
        # dfdf.loc[1] = api.knifeEA
        # dfdf.to_csv(readPath + '\\knifeUsing.csv',index=False)

    def alarmSet(self):
        api.knifeAlarmSet = int(self.spinBox_14.value())
        saveTempData()

    def renewEAState(self,a):     #更新界面上的使能信息
        if self.sender().isChecked():
            self.daoNum[a].setValue(api.knifeUsing[a])
            # self.doubleSpinBoxNum[a].setValue(self.daoFile.loc[api.knifeUsing[a],'运行米长'])
            self.doubleSpinBoxNum[a].setValue(api.daoRecs[api.knifeUsing[a]])
            for i in range(12):
                if api.knifeEA[i]:
                    if (self.daoNum[i].value() == self.daoNum[a].value()) & (self.daoNum[a] != self.daoNum[i]):
                        QMessageBox.about(self,'刀具重复使用提醒','刀具{}已使用！请更换其他刀具。'.format(self.daoNum[a].value()))

        self.daoNum[a].setEnabled(self.sender().isChecked())
        self.doubleSpinBoxNum[a].setEnabled(self.sender().isChecked())
        self.pushbuttons[a].setEnabled(self.sender().isChecked())
        self.alarmMeter()
        for i in range(12):
            api.knifeUsing[i] = int(self.daoNum[i].value())
            api.knifeEA[i] = int(self.checkboxes[i].isChecked())

    def OpenKnifeFile(self): #打开文件
        try:
            os.rename(knifePath,knifePath)
            os.startfile(knifePath)
        except:
            msgBox = QMessageBox(QMessageBox.Warning,'提示','文件已打开')
            msgBox.exec_()
    def D1(self):
        # self.daoFile = pd.read_csv(knifePath,encoding='GBk',index_col=0)
        # print(self.sender() == self.daoNum[0])
        for i in range(12):
            # self.doubleSpinBoxNum[i].setValue(self.daoFile.loc[self.daoNum[i].value(),'运行米长'])
            if api.knifeEA[i]:
                self.doubleSpinBoxNum[i].setValue(api.daoRecs[api.knifeUsing[i]])
                try:
                    if (self.daoNum[i].value() == self.sender().value()) & (self.sender() != self.daoNum[i]):
                        QMessageBox.about(self,'刀具重复使用提醒','刀具{}已使用！请更换其他刀具。'.format(self.sender().value()))
                except Exception:
                    pass

    def alarmMeter(self):
        alarmlist = '报警刀具：'
        for i in range(12):
            if self.checkboxes[i].isChecked:
                if self.doubleSpinBoxNum[i].value()>api.knifeAlarmSet:
                    alarmlist = alarmlist+'/'+str(self.daoNum[i].value())
                    mainWin.knifeButton.setStyleSheet("background-color: #ffff00")
        self.textEdit.setPlainText(alarmlist)

    def meterClickedButton(self,daoNum):
        # daoData = pd.read_csv(knifePath,encoding='GBK',index_col=0)
        # daoData.loc[daoNum,'运行米长'] = 0
        # daoData.to_csv(knifePath,encoding='GBK',index=True,header=True)
        ans = QMessageBox.question(self,'米长清零确认','确认将刀具{}运行长度清零？'.format(daoNum),QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        if ans == QMessageBox.Yes:
            api.daoRecs[daoNum] = 0
            self.D1()
        elif ans == QMessageBox.No:
            pass
        


class peiFang(QtWidgets.QWidget,Ui_Form1):  #配方编辑
    def __init__(self):
        super(peiFang,self).__init__()
        self.setupUi(self)
        self.spinBox_2.setRange(0,200) #速度限定
        self.spinBox_3.setRange(0,10000) #芯筒宽度
        self.spinBox_4.setRange(0,2000)  #张力设定
        self.spinBox_5.setRange(0,10000) #膜宽
        self.spinBox_6.setRange(0,3000)  #膜厚
        self.spinBox_7.setRange(0,8000) #预设长度
        self.spinBox_8.setRange(0,1000)  #点动停机米数(m)
        self.spinBox_9.setRange(0,100)  #点动停机速度(m/min)
        self.spinBox_10.setRange(0,10)  #上收卷芯筒尺寸
        self.spinBox_11.setRange(0,5000) #上收卷芯筒宽度
        self.spinBox_12.setRange(0,100) #上滑差环数
        self.spinBox_13.setRange(0,200) #收卷上张力
        self.spinBox_14.setRange(0,100) #上锥度
        self.spinBox_15.setRange(0,10)  #下收卷芯筒尺寸
        self.spinBox_16.setRange(0,5000) #下收卷芯筒宽度
        self.spinBox_17.setRange(0,100) #下滑差环数
        self.spinBox_18.setRange(0,200) #收卷下张力
        self.spinBox_19.setRange(0,10)  #下锥度
        self.spinBox_20.setRange(0,100) #升速时间
        self.spinBox_21.setRange(0,100) #降速时间
        self.spinBox_22.setRange(0,100) #停止时间
        self.pushButton_4.clicked.connect(self.peiFangNow)
        self.pushButton.clicked.connect(self.modifyPeifang)
        self.pushButton_5.clicked.connect(self.openPeiFangFlie)
        # self.spinBox.editingFinished.connect(self.selectPeiFang)
        self.pushButton_2.clicked.connect(self.modifyPeifang)
        self.peifang_del.clicked.connect(self.PfDel)
        # self.peifangApplication.editingFinished.connect(self.peifangApp)   #配方编号，用于显示配方
        self.peifangApplication.editingFinished.connect(self.selectPeiFang)
        self.pushButton_6.clicked.connect(self.applicationBtn)   #点击应用将数据写入
        self.peifangApplication.setRange(0,201)
        # self.textEditName = [self.textEdit_22,self.textEdit,self.textEdit_2,self.textEdit_3,self.textEdit_4,self.textEdit_5,self.textEdit_6,self.textEdit_7,self.textEdit_8,\
        #     self.textEdit_9,self.textEdit_10,self.textEdit_11,self.textEdit_12,self.textEdit_13,self.textEdit_14,self.textEdit_15,self.textEdit_16,self.textEdit_17,\
        #         self.textEdit_18,self.textEdit_19,self.textEdit_20,self.textEdit_21]
        self.NowValue = [0,api.SpeedLmitHigh,api.xintong_widthDown,api.fangjuanFSetDown,api.lengthSet,api.Mo_WidthDown,\
                api.Mo_thickDown,api.Meters_Stop,api.speedJog,api.xintongSizeUp,api.tongkuanUp,\
                    api.circlesUp,api.shoujuanFSetUp,api.zhuiduUp,api.xintongSizeDown,api.tongkuanDown,\
                        api.circlesDown,api.shoujuanFSetDown,api.zhuiduDown,api.Accelerate_time,api.Slow_time,\
                            api.Stop_time]
        self.peifangSpinBox = [self.textEdit_22,self.spinBox_2,self.spinBox_3,self.spinBox_4,self.spinBox_7,self.spinBox_5,self.spinBox_6,self.spinBox_8,\
            self.spinBox_9,self.spinBox_10,self.spinBox_11,self.spinBox_12,self.spinBox_13,self.spinBox_14,self.spinBox_15,self.spinBox_16,self.spinBox_17,\
                self.spinBox_18,self.spinBox_19,self.spinBox_20,self.spinBox_21,self.spinBox_22]
    def PfDel(self,event):#弹窗确定——清除配方——刷新显示
        NumPeiFang = peiFangWin.peifangApplication.value()
        s = '将要删除配方' + str(NumPeiFang)
        msg_box  = QMessageBox.question(self,'警告',s,QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        if msg_box == QMessageBox.Yes:
            indexName = ['配方名','速度限定','芯筒宽度','张力设定','预设长度','膜宽','膜厚','点动停机米数','点动停机速度',\
            '上收芯筒尺寸','上筒宽','SJ上滑差环数','SJ上张力','上锥度',\
                '下收芯筒尺寸','下筒宽','下滑差环数','下张力','下锥度','加速时间','减速时间','停止时间']
            PfDel = readCsv()
            for k in range(22):
                    PfDel.loc[NumPeiFang,str(indexName[k])] = 0
            try:   
                PfDel.to_csv(peifangPath,encoding='GBK',index=True,header=True)
                msgBox = QMessageBox(QMessageBox.Warning,'配方删除提示','配方删除成功')
                msgBox.exec_()
            except:
                msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件被占用，请先关闭文件')
                msgBox.exec_()
            self.selectPeiFang()
        else:
            pass


    def peiFangNow(self):       #显示当前配方
        self.label_46.setText('当前运行配方')
        # self.label_46.styleSheet("color:#00ff00")
        # self.peifangApplication.setValue(api.lastPeiFangNum)
        # self.peifangApplication.setValue(0)
        print('last peifang',api.lastPeiFangNum)
        self.label_46.setStyleSheet("color:blue;border:1px solid blue")
        for i in range(1,len(self.peifangSpinBox)):
                self.peifangSpinBox[i].setValue(self.NowValue[i])
        # print(list(readCsv().loc[5]))
        self.textEdit_22.setPlainText(str(readCsv().loc[api.lastPeiFangNum,'配方名']))

    def peifangApp(self):  #显示选择的配方
        NumPeiFang = peiFangWin.peifangApplication.value()
        self.label_46.setText('请检查将要应用的配方是否正确')
        self.label_46.setStyleSheet('color:#ff0000;border:1px solid #ff0000')
        NumRead = list(readCsv().loc[NumPeiFang])
        for k in range(22):
            self.textEditName[k].setPlainText(str(NumRead[k]))
    # def modifiyPeiFang(self):
    #     NumPeiFang = self.spinBox.value()
    #     peifang = pd.read_csv('')

    def applicationBtn(self):
        NumPeiFang = self.peifangApplication.value()
        api.lastPeiFangNum = NumPeiFang
        NumRead = list(readCsv().loc[NumPeiFang])
        # print(NumRead)
        # for k in range(21):
        #     WriteValue[k] = NumRead[k]
        api.SpeedLmitHigh = NumRead[0+1]
        api.xintong_widthDown= NumRead[1+1]
        api.fangjuanFSetDown= NumRead[2+1]
        api.lengthSet= NumRead[3+1]
        api.Mo_WidthDown= NumRead[4+1]
        api.Mo_thickDown= NumRead[5+1]
        api.Meters_Stop= NumRead[6+1]
        api.speedJog= NumRead[7+1]
        api.xintongSizeUp= NumRead[8+1]
        api.tongkuanUp= NumRead[9+1]
        api.circlesUp= NumRead[10+1]
        api.shoujuanFSetUp= NumRead[11+1]
        api.zhuiduUp= NumRead[12+1]
        api.xintongSizeDown= NumRead[13+1]
        api.tongkuanDown= NumRead[14+1]
        api.circlesDown= NumRead[15+1]
        api.shoujuanFSetDown= NumRead[16+1]
        api.zhuiduDown= NumRead[17+1]
        api.Accelerate_time= NumRead[18+1]
        api.Slow_time= NumRead[19+1]
        api.Stop_time= NumRead[20+1]
        send_data_to_PLC()
        msgBox = QMessageBox(QMessageBox.Warning,'提示','配方应用成功')
        self.NowValue = [0,api.SpeedLmitHigh,api.xintong_widthDown,api.fangjuanFSetDown,api.lengthSet,api.Mo_WidthDown,\
                api.Mo_thickDown,api.Meters_Stop,api.speedJog,api.xintongSizeUp,api.tongkuanUp,\
                    api.circlesUp,api.shoujuanFSetUp,api.zhuiduUp,api.xintongSizeDown,api.tongkuanDown,\
                        api.circlesDown,api.shoujuanFSetDown,api.zhuiduDown,api.Accelerate_time,api.Slow_time,\
                            api.Stop_time]
        saveTempData()
        msgBox.exec_()
            # print(len(NumRead),NumRead[k])

    def selectPeiFang(self):
        peifangSpinBox = [self.spinBox_2,self.spinBox_3,self.spinBox_4,self.spinBox_7,self.spinBox_5,self.spinBox_6,self.spinBox_8,\
            self.spinBox_9,self.spinBox_10,self.spinBox_11,self.spinBox_12,self.spinBox_13,self.spinBox_14,self.spinBox_15,self.spinBox_16,self.spinBox_17,\
                self.spinBox_18,self.spinBox_19,self.spinBox_20,self.spinBox_21,self.spinBox_22]
        NumPeiFang = peiFangWin.peifangApplication.value()
        if NumPeiFang==0:#机器上的配方
            self.peiFangNow()
        else:
            NumRead = list(readCsv().loc[NumPeiFang])
            for k in range(22):
                if k == 0:
                    # self.peifangSpinBox[k].setPlainText(list(readCsv().loc[5])[0])
                    self.peifangSpinBox[k].setPlainText(str(readCsv().loc[NumPeiFang,'配方名']))
                else:
                    self.peifangSpinBox[k].setValue(NumRead[k])
        # csvfile.loc[NumPeiFang,str(indexName[k])]=setPeiFangValue[k]
    def modifyPeifang(self):
        indexName = ['配方名','速度限定','芯筒宽度','张力设定','预设长度','膜宽','膜厚','点动停机米数','点动停机速度',\
            '上收芯筒尺寸','上筒宽','SJ上滑差环数','SJ上张力','上锥度',\
                '下收芯筒尺寸','下筒宽','下滑差环数','下张力','下锥度','加速时间','减速时间','停止时间']
        peifangSpinBox = [self.textEdit_22,self.spinBox_2,self.spinBox_3,self.spinBox_4,self.spinBox_7,self.spinBox_5,self.spinBox_6,self.spinBox_8,\
            self.spinBox_9,self.spinBox_10,self.spinBox_11,self.spinBox_12,self.spinBox_13,self.spinBox_14,self.spinBox_15,self.spinBox_16,self.spinBox_17,\
                self.spinBox_18,self.spinBox_19,self.spinBox_20,self.spinBox_21,self.spinBox_22]
        NumPeiFang = peiFangWin.peifangApplication.value()
        
        modifiedPeiFang = readCsv()
        for k in range(22):
            if k == 0:
                modifiedPeiFang.loc[NumPeiFang,str(indexName[k])] = self.peifangSpinBox[k].toPlainText()
            else:
                modifiedPeiFang.loc[NumPeiFang,str(indexName[k])] = self.peifangSpinBox[k].value()
        try:   
            modifiedPeiFang.to_csv(peifangPath,encoding='GBK',index=True,header=True)
            msgBox = QMessageBox(QMessageBox.Warning,'配方修改提示','配方修改成功')
            msgBox.exec_()
        except:
            msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件被占用，请先关闭文件')
            msgBox.exec_()
    def openPeiFangFlie(self):
        if os.path.exists(peifangPath):
            try:
                os.rename(peifangPath,peifangPath)
                os.startfile(peifangPath)
                # self.pushButton_4.setStyleSheet("background-color: #00ff00")
            except:
                msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件已被打开')
                # self.pushButton_4.setStyleSheet("background-color: #ffffff")
                msgBox.exec_()
                print('wnejianzhanyong')
            # if os.rename(peifangPath,peifangPath):
            #      self.pushButton_4.setStyleSheet("background-color: #ffffff")
        else:
            msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件不存在')
            # self.pushButton_4.setStyleSheet("background-color: #ffffff")
            msgBox.exec_()
            print('文件不存在')  

    def savePeifang(self):  #配方保存
        indexName = ['配方名','速度限定','芯筒宽度','张力设定','预设长度','膜宽','膜厚','点动停机米数','点动停机速度',\
            '上收芯筒尺寸','上筒宽','SJ上滑差环数','SJ上张力','上锥度',\
                '下收芯筒尺寸','下筒宽','下滑差环数','下张力','下锥度','加速时间','减速时间','停止时间']
        peifangSpinBox = [self.textEdit_22,self.spinBox_2,self.spinBox_3,self.spinBox_4,self.spinBox_7,self.spinBox_5,self.spinBox_6,self.spinBox_8,\
            self.spinBox_9,self.spinBox_10,self.spinBox_11,self.spinBox_12,self.spinBox_13,self.spinBox_14,self.spinBox_15,self.spinBox_16,self.spinBox_17,\
                self.spinBox_18,self.spinBox_19,self.spinBox_20,self.spinBox_21,self.spinBox_22]
        NumPeiFang = peiFangWin.peifangApplication.value()
        
        modifiedPeiFang = readCsv()
        for k in range(22):
            if k == 0:
                modifiedPeiFang.loc[NumPeiFang,str(indexName[k])] = self.peifangSpinBox[k].toPlainText()
            else:
                modifiedPeiFang.loc[NumPeiFang,str(indexName[k])] = self.peifangSpinBox[k].value()
        try:   
            modifiedPeiFang.to_csv(peifangPath,encoding='GBK',index=True,header=True)
            msgBox = QMessageBox(QMessageBox.Warning,'配方修改提示','配方修改成功')
            msgBox.exec_()
        except:
            msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件被占用，请先关闭文件')
            msgBox.exec_()
    # # try:
    # #     os.rename(peifangPath,peifangPath)
    #     if os.path.exists(peifangPath):
    #         try:
    #             os.rename(peifangPath,peifangPath)
    #             # indexCount = pd.read_csv(peifangPath,encoding='GBK',index_col=0)

    #             # indexCount = readCsv()
    #             # PdPF = pd.DataFrame([{"配方号":len(indexCount.index.values)+1,"配方名":self.textEdit_22.toPlainText(),"速度限定":api.SpeedLmitHigh,"芯筒宽度":api.xintong_widthDown,"张力设定":api.fangjuanFSetDown,"预设长度":api.lengthSet,\
    #             #     "膜宽":api.Mo_WidthDown,"膜厚":api.Mo_thickDown,"点动停机米数":api.Meters_Stop,"点动停机速度":api.speedJog,\
    #             #     "上收芯筒尺寸":api.xintongSizeUp,"上筒宽":api.tongkuanUp,"SJ上滑差环数":api.circlesUp,"SJ上张力":api.shoujuanFSetUp,"上锥度":api.zhuiduUp,\
    #             #         "下收芯筒尺寸":api.xintongSizeDown,"下筒宽":api.tongkuanDown,"下滑差环数":api.circlesDown,"下张力":api.shoujuanFSetDown,"下锥度":api.zhuiduDown,\
    #             #             "加速时间":api.Accelerate_time,"减速时间":api.Slow_time,"停止时间":api.Stop_time}])
    #             PdPF = pd.DataFrame([{"配方号":self.peifangApplication.value(),"配方名":self.textEdit_22.toPlainText(),"速度限定":self.peifangSpinBox[1].value(),"芯筒宽度":self.peifangSpinBox[2].value(),"张力设定":self.peifangSpinBox[3].value(),"预设长度":api.lengthSet,\
    #                 "膜宽":self.peifangSpinBox[4].value(),"膜厚":self.peifangSpinBox[5].value(),"点动停机米数":self.peifangSpinBox[6].value(),"点动停机速度":self.peifangSpinBox[7].value(),\
    #                 "上收芯筒尺寸":self.peifangSpinBox[8].value(),"上筒宽":self.peifangSpinBox[9].value(),"SJ上滑差环数":self.peifangSpinBox[10].value(),"SJ上张力":self.peifangSpinBox[11].value(),"上锥度":self.peifangSpinBox[12].value(),\
    #                     "下收芯筒尺寸":self.peifangSpinBox[13].value(),"下筒宽":self.peifangSpinBox[14].value(),"下滑差环数":self.peifangSpinBox[15].value(),"下张力":self.peifangSpinBox[16].value(),"下锥度":self.peifangSpinBox[17].value(),\
    #                         "加速时间":self.peifangSpinBox[18].value(),"减速时间":self.peifangSpinBox[19].value(),"停止时间":self.peifangSpinBox[20].value()}])
    #             PdPF.to_csv(peifangPath,encoding='GBK',mode='a',index=False,header=False)
    #             msgBox = QMessageBox(QMessageBox.Warning,'Noting','配方记录成功')
    #             msgBox.exec_()
    #         except:
    #             print("文件被占用，请先关闭文件")
    #             msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件被占用，请先关闭文件')
    #             msgBox.exec_()
    #     else:
    #         PdPF = pd.DataFrame([{"配方号":1,"配方名":self.textEdit_22.toPlainText(),"速度限定":api.SpeedLmitHigh,"芯筒宽度":api.xintong_widthDown,"张力设定":api.fangjuanFSetDown,"预设长度":api.lengthSet,\
    #             "膜宽":api.Mo_WidthDown,"膜厚":api.Mo_thickDown,"点动停机米数":api.Meters_Stop,"点动停机速度":api.speedJog,\
    #                 "上收芯筒尺寸":api.xintongSizeUp,"上筒宽":api.tongkuanUp,"SJ上滑差环数":api.circlesUp,"SJ上张力":api.shoujuanFSetUp,"上锥度":api.zhuiduUp,\
    #                     "下收芯筒尺寸":api.xintongSizeDown,"下筒宽":api.tongkuanDown,"下滑差环数":api.circlesDown,"下张力":api.shoujuanFSetDown,"下锥度":api.zhuiduDown,\
    #                         "加速时间":api.Accelerate_time,"减速时间":api.Slow_time,"停止时间":api.Stop_time}])
    #         PdPF.to_csv(peifangPath,encoding='GBK',mode='a',index=False,header=True)
    #         msgBox = QMessageBox(QMessageBox.Warning,'Noting','配方记录成功')
    #         msgBox.exec_() 
def readCsv():
    indexCsv = pd.read_csv(peifangPath,encoding='GBK',index_col=0)
    return indexCsv

# def savePeifang():  #配方保存
#     # try:
#     #     os.rename(peifangPath,peifangPath)
#         if os.path.exists(peifangPath):
#             try:
#                 os.rename(peifangPath,peifangPath)
#                 # indexCount = pd.read_csv(peifangPath,encoding='GBK',index_col=0)

#                 indexCount = readCsv()
#                 PdPF = pd.DataFrame([{"配方号":len(indexCount.index.values)+1,"速度限定":api.SpeedLmitHigh,"芯筒宽度":api.xintong_widthDown,"张力设定":api.fangjuanFSetDown,"预设长度":api.lengthSet,\
#                     "膜宽":api.Mo_WidthDown,"膜厚":api.Mo_thickDown,"点动停机米数":api.Meters_Stop,"点动停机速度":api.speedJog,\
#                     "上收芯筒尺寸":api.xintongSizeUp,"上筒宽":api.tongkuanUp,"SJ上滑差环数":api.circlesUp,"SJ上张力":api.shoujuanFSetUp,"上锥度":api.zhuiduUp,\
#                         "下收芯筒尺寸":api.xintongSizeDown,"下筒宽":api.tongkuanDown,"下滑差环数":api.circlesDown,"下张力":api.shoujuanFSetDown,"下锥度":api.zhuiduDown,\
#                             "加速时间":api.Accelerate_time,"减速时间":api.Slow_time,"停止时间":api.Stop_time}])
#                 PdPF.to_csv(peifangPath,encoding='GBK',mode='a',index=False,header=False)
#                 msgBox = QMessageBox(QMessageBox.Warning,'Noting','配方记录成功')
#                 msgBox.exec_()
#             except:
#                 print("文件被占用，请先关闭文件")
#                 msgBox = QMessageBox(QMessageBox.Warning,'Warning','文件被占用，请先关闭文件')
#                 msgBox.exec_()
#         else:
#             PdPF = pd.DataFrame([{"配方号":1,"速度限定":api.SpeedLmitHigh,"芯筒宽度":api.xintong_widthDown,"张力设定":api.fangjuanFSetDown,"预设长度":api.lengthSet,\
#                 "膜宽":api.Mo_WidthDown,"膜厚":api.Mo_thickDown,"点动停机米数":api.Meters_Stop,"点动停机速度":api.speedJog,\
#                     "上收芯筒尺寸":api.xintongSizeUp,"上筒宽":api.tongkuanUp,"SJ上滑差环数":api.circlesUp,"SJ上张力":api.shoujuanFSetUp,"上锥度":api.zhuiduUp,\
#                         "下收芯筒尺寸":api.xintongSizeDown,"下筒宽":api.tongkuanDown,"下滑差环数":api.circlesDown,"下张力":api.shoujuanFSetDown,"下锥度":api.zhuiduDown,\
#                             "加速时间":api.Accelerate_time,"减速时间":api.Slow_time,"停止时间":api.Stop_time}])
#             PdPF.to_csv(peifangPath,encoding='GBK',mode='a',index=False,header=True)
#             msgBox = QMessageBox(QMessageBox.Warning,'Noting','配方记录成功')
#             msgBox.exec_()


class flawDealPopup(QtWidgets.QMainWindow,Ui_DefectProcess):  #缺陷处理弹窗
    def __init__(self):
        super(flawDealPopup,self).__init__()
        self.setupUi(self)
        self.flawShow = api.stopStack[-1][:]
        self.pushButton.clicked.connect(self.openFlawStop)
        self.pushButton_2.clicked.connect(self.show_pic)
        self.pushButton_3.clicked.connect(self.openFlawFile)
        self.pushButton_4.pressed.connect(self.popDealDone)
        self.radioButton.toggled.connect(lambda:self.chooseDealType(0))
        self.radioButton_2.toggled.connect(lambda:self.chooseDealType(3))
        self.radioButton_3.toggled.connect(lambda:self.chooseDealType(1))
        self.radioButton_4.toggled.connect(lambda:self.chooseDealType(2))
        self.radioButton_5.toggled.connect(lambda:self.chooseDealType(4))
        self.radioButton_6.toggled.connect(lambda:self.chooseDealType(5))
        self.spinBox.setRange(0,100000000)
        self.doubleSpinBox.setRange(0,100000000)
        self.doubleSpinBox_3.setRange(0,100000000)
        self.doubleSpinBox_2.setRange(0,100000000)
        self.spinBox.setValue(int(api.stopStack[-1][0]))
        self.doubleSpinBox.setValue(float(api.stopStack[-1][1]))
        self.textEdit.setPlainText(api.stopTypeNames[api.stopStack[-1][2]])
        # if api.stopStack[-1][0] != 0:
        #     self.doubleSpinBox_3.setValue(float(api.badMetersX[api.findPoint[api.stopStack[-1][0]]]))
        #     self.doubleSpinBox_2.setValue(float(api.badMeters[api.findPoint[api.stopStack[-1][0]]]))
        #     self.textEdit_2.setPlainText('{}卷位'.format(findGongWeiNum(api.badMetersX[api.findPoint[api.stopStack[-1][0]]])))
        if self.flawShow[0] != 0:
            self.doubleSpinBox_3.setValue(float(api.badMetersX[api.findPoint[self.flawShow[0]]]))
            self.doubleSpinBox_2.setValue(float(api.badMeters[api.findPoint[self.flawShow[0]]]))
            self.textEdit_2.setPlainText('{}卷位'.format(findGongWeiNum(api.badMetersX[api.findPoint[self.flawShow[0]]])))

        if api.MXlist[5][2] == 1:          #瑕疵停机选择
            self.pushButton.setStyleSheet("background-color: #00ff00")
        elif api.MXlist[5][2] == 0:
            self.pushButton.setStyleSheet("background-color: #ffffff")

        if self.flawShow[2] > 1:
        # if api.stopStack[-1][2] > 1:        # 如果是两个观察区后面的停机位置，则不需要选择处理方式
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            self.radioButton_3.setEnabled(False)
            self.radioButton_4.setEnabled(False)
            self.radioButton_5.setEnabled(False)
            self.radioButton_6.setEnabled(False)

    def openFlawStop(self):         # 瑕疵停机选择
        request1 = client.read_holding_registers(9,1).registers
        buttonList = dec_to_binlist(request1[0],16)
        buttonList[2] = 1 - buttonList[2]
        command = binlist_to_int(buttonList)
        client.write_register (value=command, unit=2, address=9)  

    def show_pic(self):              # 显示缺陷图片
        # imagePath0 = updateFlawFile(flawPicFolderPath) + '\\{0}.bmp'.format(str(api.badPics[api.badPoint]).zfill(6))
        # imagePath0 = api.flawFilePath + '\\{0}.bmp'.format(str(api.badPics[api.findPoint[api.stopStack[-1][0]]]).zfill(6))
        imagePath0 = api.flawFilePath + '\\{0}.bmp'.format(str(api.badPics[api.findPoint[self.flawShow[0]]]).zfill(6))
        # print('当前第',api.badPoint)
        print('image path',imagePath0)
        os.startfile(imagePath0)

    def openFlawFile(self):         # 打开缺陷文件
        # flawFilePath = updateFlawFile(flawFileFolderPath) + '\\ErrorData.csv'
        flawFilePath = api.flawFilePath + '/ErrorData.csv'
        os.startfile(flawFilePath)
    
    def popDealDone(self):
        api.dealDoneFlag = 1
        # mainWin.shoujuanSetWin.close()
    
    def chooseDealType(self,a):
        api.dealtype = a
        dealTypeNames = ['不处理','确认','裁剪','双面贴胶','NY面贴胶','PP面贴胶']
        print('缺陷编号：{}，处理方式：{}'.format(api.stopStack[-1][0],dealTypeNames[a]))


class shoujuanGongwei(QtWidgets.QMainWindow,Ui_ShouJuan):  #收卷工位设置
    def __init__(self):
        super(shoujuanGongwei,self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.confirm)
        self.pushButton_2.clicked.connect(self.cancel)
        self.pushButton_3.clicked.connect(self.clearAll)
        self.radioButton.toggled.connect(self.upDownChange)
        self.radioButton_2.toggled.connect(self.upDownChange)
        self.radioButton_5.toggled.connect(self.cutSurfaceChange)
        self.radioButton_6.toggled.connect(self.cutSurfaceChange)

        self.dsbNames = [self.doubleSpinBox_16,self.doubleSpinBox,self.doubleSpinBox_2,self.doubleSpinBox_3,self.doubleSpinBox_4,\
            self.doubleSpinBox_5,self.doubleSpinBox_6,self.doubleSpinBox_7,self.doubleSpinBox_8,
            self.doubleSpinBox_9,self.doubleSpinBox_10,self.doubleSpinBox_11,self.doubleSpinBox_12,
            self.doubleSpinBox_13,self.doubleSpinBox_14,self.doubleSpinBox_15,
            self.doubleSpinBox_19,self.doubleSpinBox_20,self.doubleSpinBox_27,self.doubleSpinBox_21,
            self.doubleSpinBox_26,self.doubleSpinBox_24,self.doubleSpinBox_32,self.doubleSpinBox_22,
            self.doubleSpinBox_29,self.doubleSpinBox_23,self.doubleSpinBox_18,self.doubleSpinBox_17,
            self.doubleSpinBox_28,self.doubleSpinBox_25,self.doubleSpinBox_31,self.doubleSpinBox_30]
        for item in self.dsbNames:
            item.setRange(0,10000)
            # self.pushButton_3.clicked.connect(item.clear)
        print('qie  {}'.format(api.cutPPorNY))
        if api.cutPPorNY == 0:
            self.radioButton_5.setChecked(True)
            self.radioButton_6.setChecked(False)
        elif api.cutPPorNY == 1:
            self.radioButton_5.setChecked(False)
            self.radioButton_6.setChecked(True)

        self.saverPath = readPath + '\\gongweiSet.csv'
        if os.path.exists(self.saverPath):
            parameters = []
            f = open(self.saverPath,'r',newline='')
            reader = csv.reader(f)
            # print('length',len(reader))
            for i in reader:
                parameters.append(float(i[0])) 
            f.close()
            api.firstUpOrDown = parameters[-1]
            for i in range(len(self.dsbNames)):
                self.dsbNames[i].setValue(parameters[i])
            if parameters[-1] == 0:
                self.radioButton.setChecked(True)
                self.radioButton_2.setChecked(False)
            elif parameters[-1] == 1:
                self.radioButton.setChecked(False)
                self.radioButton_2.setChecked(True)

    def clearAll(self):         #页面清零
        for i in self.dsbNames:
            i.setValue(0)

    def upDownChange(self):     #1工位上下收卷
        if self.sender() == self.radioButton:
            api.firstUpOrDown = 0
            print('1工位上收卷')
        elif self.sender() == self.radioButton_2:
            api.firstUpOrDown = 1
            print('1工位下收卷')
    
    def cutSurfaceChange(self):     #切换分切表面
        if self.radioButton_5.isChecked():
            api.cutPPorNY = 0
            print('切PP面')
        elif self.radioButton_6.isChecked():
            api.cutPPorNY = 1
            print('切NY面')

    def confirm(self):          #确认
        api.shoujuanWidths=[self.doubleSpinBox_16.value(),self.doubleSpinBox.value(),self.doubleSpinBox_2.value(),self.doubleSpinBox_3.value(),self.doubleSpinBox_4.value(),\
                            self.doubleSpinBox_5.value(),self.doubleSpinBox_6.value(),self.doubleSpinBox_7.value(),self.doubleSpinBox_8.value(),
                            self.doubleSpinBox_9.value(),self.doubleSpinBox_10.value(),self.doubleSpinBox_11.value(),self.doubleSpinBox_12.value(),
                            self.doubleSpinBox_13.value(),self.doubleSpinBox_14.value(),self.doubleSpinBox_15.value(),
                            self.doubleSpinBox_19.value(),self.doubleSpinBox_20.value(),self.doubleSpinBox_27.value(),self.doubleSpinBox_21.value(),
                            self.doubleSpinBox_26.value(),self.doubleSpinBox_24.value(),self.doubleSpinBox_32.value(),self.doubleSpinBox_22.value(),
                            self.doubleSpinBox_29.value(),self.doubleSpinBox_23.value(),self.doubleSpinBox_18.value(),self.doubleSpinBox_17.value(),
                            self.doubleSpinBox_28.value(),self.doubleSpinBox_25.value(),self.doubleSpinBox_31.value(),self.doubleSpinBox_30.value()]
                            # 左边料doubleSpinBox_16，右边料doubleSpinBox_30
        
        api.shoujuanBorders=[0]#建立区间列表
        self.saver = []
        total = 0              #d对输入列表求和
        for i in range(len(api.shoujuanWidths)):     #通过求和生成区间列表
            self.saver.append([api.shoujuanWidths[i]])
            if api.shoujuanWidths[i] != 0:
                total+=api.shoujuanWidths[i]
                api.shoujuanBorders.append(total)
        # print('边界：',api.shoujuanBorders)
        # for i in range(len(api.shoujuanBorders)-1):
        #     if (api.shoujuanBorders[i]<=500) & (500<api.shoujuanBorders[i+1]):
        #         print('gongwei num',i,abs((api.firstUpOrDown - (1 - i%2))))
        # x=int(input('请输入x坐标值：'))
        if self.radioButton.isChecked():
            api.firstUpOrDown = 0
        elif self.radioButton_2.isChecked():
            api.firstUpOrDown = 1
        else:
            pass
        f = open(readPath + '\\gongweiSet.csv','w',newline='')
        csv.writer(f).writerows(self.saver)
        csv.writer(f).writerow([api.firstUpOrDown])
        f.close()
        mainWin.shoujuanSetWin.close()
    
    def cancel(self):           #取消
        mainWin.shoujuanSetWin.close()

def findGongWeiNum(x):          #根据缺陷x坐标找到它在收卷的第几工位
    # print('borders',api.shoujuanBorders,api.shoujuanWidths)
    if len(api.shoujuanBorders) <= 1:
        return api.firstUpOrDown
    else:
        # if x < api.shoujuanBorders[1]:      #x小于左边料边界，认为在左边料
        #     return -1
        # elif x >= api.shoujuanBorders[-2]:  #x超过右边料边界，认为在右边料
        #     return -1
        # else:
        #     for i in range(1,len(api.shoujuanBorders)-2):
        #         if (api.shoujuanBorders[i]<=x) & (x<api.shoujuanBorders[i+1]):
        #             if api.shoujuanWidths[0] > 0:       #有左边料
        #                 if api.shoujuanWidths[-1] >= 0:
        #                     return i
        #             elif api.shoujuanWidths[0] == 0:
        #                 return i+1
        if (api.shoujuanWidths[0] > 0) & (api.shoujuanWidths[-1] == 0):       #有左边料，无右边料
            if (x >= api.shoujuanBorders[0]) & (x < api.shoujuanBorders[1]):
                return -1
            else:
                for i in range(1,len(api.shoujuanBorders)-1):
                    if (api.shoujuanBorders[i]<=x) & (x<api.shoujuanBorders[i+1]):
                        return i

        elif (api.shoujuanWidths[0] == 0) & (api.shoujuanWidths[-1] > 0):     #无左边料，有右边料
            if (x >= api.shoujuanBorders[-2]) & (x <= api.shoujuanBorders[-1]):
                return -1
            else:
                for i in range(0,len(api.shoujuanBorders)-1):
                    if (api.shoujuanBorders[i]<=x) & (x<api.shoujuanBorders[i+1]):
                        return i+1
        
        elif (api.shoujuanWidths[0] == 0) & (api.shoujuanWidths[-1] == 0):    #无左边料，无右边料
            for i in range(0,len(api.shoujuanBorders)-1):
                if (api.shoujuanBorders[i]<=x) & (x<api.shoujuanBorders[i+1]):
                    return i+1
        
        elif (api.shoujuanWidths[0] > 0) & (api.shoujuanWidths[-1] > 0):      #有左边料，有右边料
            if (x >= api.shoujuanBorders[0]) & (x < api.shoujuanBorders[1]):
                return -1
            elif (x >= api.shoujuanBorders[-2]) & (x <= api.shoujuanBorders[-1]):
                return -1
            else:
                for i in range(1,len(api.shoujuanBorders)-2):
                    if (api.shoujuanBorders[i]<=x) & (x<api.shoujuanBorders[i+1]):
                        return i



class readPLCThread (threading.Thread):    #连续读取PLC数据
    def __init__(self, threadID, name, stopflag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stop = stopflag

        self.lastShoujuan = 0
        self.lastFangjuan = 0

    def close(self):
        self.stop = 1

    def run(self):
        while True:
            #输出继电器
            # global last_qizhang
            # global last_flawStop
            # global now_qizhang
            # last_qizhang = api.QXlist[15]
            # last_flawStop = api.MXlist[5][2]
            try:
                api.QXlist = client.read_coils(0,50).bits
                yadaiUD = client.read_coils(1053,2).bits
            except Exception as e:
                print(e)
                api.QXlist = [0]*50
                yadaiUD = [0,0]

            # print ('yadaiUD',yadaiUD)
            for i in range(len(api.QXlist)):
                api.QXlist[i] = int(api.QXlist[i])
            api.QXlist += [int(yadaiUD[0]),int(yadaiUD[1])]
            # print('qxlist:',api.QXlist)
            
            # now_qizhang = api.QXlist[15]
            
            # #MX寄存器
            # request0 = client.read_holding_registers(0,10).registers
            # api.MXlist[0] = dec_to_binlist(request0[0],16)
            # api.MXlist[1] = dec_to_binlist(request0[1],16)
            # api.MXlist[2] = dec_to_binlist(request0[2],16)
            # api.MXlist[3] = dec_to_binlist(request0[3],16)
            # api.MXlist[4] = dec_to_binlist(request0[4],16)
            # api.MXlist[5] = dec_to_binlist(request0[9],16)
            # # print('mxlist:',api.MXlist)
            # global now_flawStop
            # now_flawStop = api.MXlist[5][2]
            try:
                    #MX寄存器
                request0 = client.read_holding_registers(0,10).registers
                api.MXlist[0] = dec_to_binlist(request0[0],16)
                api.MXlist[1] = dec_to_binlist(request0[1],16)
                api.MXlist[2] = dec_to_binlist(request0[2],16)
                api.MXlist[3] = dec_to_binlist(request0[3],16)
                api.MXlist[4] = dec_to_binlist(request0[4],16)
                api.MXlist[5] = dec_to_binlist(request0[9],16)
                # print('mxlist:',api.MXlist)
                # global now_flawStop
                # now_flawStop = api.MXlist[5][2]
                result1 = client.read_holding_registers(10,54).registers
                result2 = client.read_holding_registers(98,18).registers
                result3 = client.read_holding_registers(416,8).registers
                result4 = client.read_holding_registers(444,8).registers
                result5 = client.read_holding_registers(132,10).registers
                result6 = client.read_holding_registers(188,10).registers
                result7 = client.read_holding_registers(470,2).registers
            except Exception as e:
                print(e)
                time.sleep(1) 
                # continue
            # print('result1',result1)

            # real型变量
            api.speedNow = api.speedNow if (dec_to_float(result1[0],result1[1]) == None) else dec_to_float(result1[0],result1[1])
            api.lengthAct = api.lengthAct if (dec_to_float(result1[2],result1[3]) == None) else dec_to_float(result1[2],result1[3])
            api.LengthSum = api.LengthSum if (dec_to_float(result1[4],result1[5]) == None) else dec_to_float(result1[4],result1[5])
            api.houshoujuanR = api.houshoujuanR if (dec_to_float(result1[6],result1[7]) == None) else dec_to_float(result1[6],result1[7])
            api.QianshoujuanR = api.QianshoujuanR if (dec_to_float(result1[8],result1[9]) == None) else dec_to_float(result1[8],result1[9])
            api.fangjuanActFUp = api.fangjuanActFUp if (dec_to_float(result1[10],result1[11]) == None) else dec_to_float(result1[10],result1[11])
            api.fangjuanRUp = api.fangjuanRUp if (dec_to_float(result1[12],result1[13]) == None) else dec_to_float(result1[12],result1[13])
            api.fangjuanActFDown = api.fangjuanActFDown if (dec_to_float(result1[14],result1[15]) == None) else dec_to_float(result1[14],result1[15])
            api.fangjuanRDown = api.fangjuanRDown if (dec_to_float(result1[16],result1[17]) == None) else dec_to_float(result1[16],result1[17])
            api.SpeedLmitHigh = api.SpeedLmitHigh if (dec_to_float(result1[18],result1[19]) == None) else dec_to_float(result1[18],result1[19])
            api.SpeedLmitLow = api.SpeedLmitLow if (dec_to_float(result1[20],result1[21]) == None) else dec_to_float(result1[20],result1[21])
            api.lengthSet = api.lengthSet if (dec_to_float(result1[22],result1[23]) == None) else dec_to_float(result1[22],result1[23])
            api.xintong_widthUp = api.xintong_widthUp if (dec_to_float(result1[24],result1[25]) == None) else dec_to_float(result1[24],result1[25])
            api.fangjuanFSetUp = api.fangjuanFSetUp if (dec_to_float(result1[26],result1[27]) == None) else dec_to_float(result1[26],result1[27])
            api.Mo_WidthUp = api.Mo_WidthUp if (dec_to_float(result1[28],result1[29]) == None) else dec_to_float(result1[28],result1[29])
            api.Mo_thickUp = api.Mo_thickUp if (dec_to_float(result1[30],result1[31]) == None) else dec_to_float(result1[30],result1[31])
            api.xintongTypeUp = api.xintongTypeUp if (dec_to_float(result1[32],result1[33]) == None) else dec_to_float(result1[32],result1[33])
            api.moTypeUp = api.moTypeUp if (dec_to_float(result1[34],result1[35]) == None) else dec_to_float(result1[34],result1[35])
            api.xintong_widthDown = api.xintong_widthDown if (dec_to_float(result1[36],result1[37]) == None) else dec_to_float(result1[36],result1[37])
            api.fangjuanFSetDown = api.fangjuanFSetDown if(dec_to_float(result1[38],result1[39]) == None) else dec_to_float(result1[38],result1[39])
            api.Mo_WidthDown = api.Mo_WidthDown if(dec_to_float(result1[40],result1[41]) == None) else dec_to_float(result1[40],result1[41])
            api.Mo_thickDown = api.Mo_thickDown if(dec_to_float(result1[42],result1[43]) == None) else dec_to_float(result1[42],result1[43])
            api.xintongTypeDown = api.xintongTypeDown if(dec_to_float(result1[44],result1[45]) == None) else dec_to_float(result1[44],result1[45])
            api.moTypeDown = api.moTypeDown if(dec_to_float(result1[46],result1[47]) == None) else dec_to_float(result1[46],result1[47])
            api.Accelerate_time = api.Accelerate_time if (dec_to_float(result1[48],result1[49]) == None) else dec_to_float(result1[48],result1[49])
            api.Slow_time = api.Slow_time if (dec_to_float(result1[50],result1[51]) == None) else dec_to_float(result1[50],result1[51])
            api.Stop_time = api.Stop_time if (dec_to_float(result1[52],result1[53]) == None) else dec_to_float(result1[52],result1[53])

            api.xintongSizeUp = api.xintongSizeUp if (dec_to_float(result2[0],result2[1]) == None) else dec_to_float(result2[0],result2[1])
            api.xintongSizeDown = api.xintongSizeDown if (dec_to_float(result2[2],result2[3]) == None) else dec_to_float(result2[2],result2[3])
            api.didaoDingWei = api.didaoDingWei if (dec_to_float(result2[4],result2[5]) == None) else dec_to_float(result2[4],result2[5])
            api.Meters_Stop = api.Meters_Stop if (dec_to_float(result2[6],result2[7]) == None) else dec_to_float(result2[6],result2[7])
            api.yagunBackUp = api.yagunBackUp if (dec_to_float(result2[8],result2[9]) == None) else dec_to_float(result2[8],result2[9])
            api.yagunBackDown = api.yagunBackDown if (dec_to_float(result2[10],result2[11]) == None) else dec_to_float(result2[10],result2[11])
            api.speedJog = api.speedJog if (dec_to_float(result2[12],result2[13]) == None) else dec_to_float(result2[12],result2[13])
            api.offsetNY = api.offsetNY if (dec_to_float(result2[14],result2[15]) == None) else dec_to_float(result2[14],result2[15])
            api.offsetPP = api.offsetPP if (dec_to_float(result2[16],result2[17]) == None) else dec_to_float(result2[16],result2[17])

            api.fangjuanSpeedRatio = api.fangjuanSpeedRatio if (dec_to_float(result5[0],result5[1]) == None) else dec_to_float(result5[0],result5[1])
            api.alarmR = api.alarmR if (dec_to_float(result5[4],result5[5]) == None) else dec_to_float(result5[4],result5[5])
            api.tongkuanDown = api.tongkuanDown if (dec_to_float(result5[6],result5[7]) == None) else dec_to_float(result5[6],result5[7])
            api.tongkuanUp = api.tongkuanUp if (dec_to_float(result5[8],result5[9]) == None) else dec_to_float(result5[8],result5[9])

            api.shoujuanFSetUp = api.shoujuanFSetUp if (dec_to_float(result3[0],result3[1]) == None) else dec_to_float(result3[0],result3[1])
            api.shoujuanFSetDown = api.shoujuanFSetDown if (dec_to_float(result3[2],result3[3]) == None) else dec_to_float(result3[2],result3[3])
            api.zhuiduUp = api.zhuiduUp if (dec_to_float(result3[4],result1[5]) == None) else dec_to_float(result3[4],result3[5])
            api.zhuiduDown = api.zhuiduDown if (dec_to_float(result3[6],result3[7]) == None) else dec_to_float(result3[6],result3[7])

            api.targetUp = api.targetUp if (dec_to_float(result4[0],result4[1]) == None) else dec_to_float(result4[0],result4[1])
            api.targetDown = api.targetDown if (dec_to_float(result4[2],result4[3]) == None) else dec_to_float(result4[2],result4[3])
            api.circlesUp = api.circlesUp if (dec_to_float(result4[4],result1[5]) == None) else dec_to_float(result4[4],result4[5])
            api.circlesDown = api.circlesDown if (dec_to_float(result4[6],result4[7]) == None) else dec_to_float(result4[6],result4[7])

            api.flawPoint = api.flawPoint if (dec_to_float(result6[0],result6[1]) == None) else dec_to_float(result6[0],result6[1])
            api.flawPoint = int(api.flawPoint)
            api.Amount_LeftFlaw = api.Amount_LeftFlaw if (dec_to_float(result6[2],result6[3]) == None) else dec_to_float(result6[2],result6[3])
            api.Meters_NextFlaw = api.Meters_NextFlaw if (dec_to_float(result6[4],result6[5]) == None) else dec_to_float(result6[4],result6[5])
            api.jiedaijinchi = api.jiedaijinchi if (dec_to_float(result6[8],result6[9]) == None) else dec_to_float(result6[8],result6[9])

            api.fangjuanL = api.fangjuanL if (dec_to_float(result7[0],result7[1]) == None) else dec_to_float(result7[0],result7[1])
            
            if (api.fangjuanL == 0) & (self.lastFangjuan > 0):
                if len(api.shoujuanFlawStack) > 0:
                    for i in range(len(api.shoujuanFlawStack)):
                        api.shoujuanFlawStack[i][0] -= self.lastFangjuan
                        f6 = open(readPath + '\\shoujuanStack.csv','w',newline='')
                        csv.writer(f6).writerows(api.shoujuanFlawStack)
                        f6.close()

            if len(api.shoujuanFlawStack) > 0:
                # print(api.fangjuanL,api.shoujuanFlawStack)
                if (api.fangjuanL - api.shoujuanFlawStack[-1][0])>=0:
                    newFlaw = api.shoujuanFlawStack.pop()
                    # if (len(api.shoujuanFlawStack) > 0):
                    #     if newFlaw[2] == 1:
                    #         while (api.shoujuanFlawStack[-1][2] == 1) & (api.shoujuanFlawStack[-1][0] == newFlaw[0]):
                    #             if (len(api.shoujuanFlawStack) > 0):
                    #                 api.shoujuanFlawStack.pop()
                    #                 if (len(api.shoujuanFlawStack) == 0):
                    #                     break
                    #             else:
                    #                 break
                    if newFlaw[1] in api.shoujuanFlawInfo.keys():
                        api.shoujuanFlawInfo[newFlaw[1]][newFlaw[2]].append(api.lengthAct)
                    else:
                        if newFlaw[2] == 0:
                            api.shoujuanFlawInfo[newFlaw[1]] = [[api.lengthAct],[]]
                        elif newFlaw[2] == 1:
                            api.shoujuanFlawInfo[newFlaw[1]] = [[],[api.lengthAct]]
                    print('flaw info new',api.shoujuanFlawInfo)
                    df5 = pd.DataFrame(api.shoujuanFlawInfo)
                    df5.to_csv(readPath + '\\tempWindInfo.csv',encoding='utf-8',mode='w',index=False,header=True)
                    f6 = open(readPath + '\\shoujuanStack.csv','w',newline='')
                    csv.writer(f6).writerows(api.shoujuanFlawStack)
                    f6.close()

            if (api.lengthAct == 0) & (self.lastShoujuan > 0):
                WriteCsv()
                api.shoujuanFlawInfo = {}
                # api.shoujuanFlawStack = []
                df5 = pd.DataFrame(api.shoujuanFlawInfo)
                df5.to_csv(readPath + '\\tempWindInfo.csv',encoding='utf-8',mode='w',index=False,header=True)
                f6 = open(readPath + '\\shoujuanStack.csv','w',newline='')
                csv.writer(f6).writerows(api.shoujuanFlawStack)
                f6.close()
            self.lastShoujuan = api.lengthAct
            self.lastFangjuan = api.fangjuanL

            # if api.MXlist[5][0] == 1:       #自动停机选择打开，把这一米数入栈
            #     if api.lengthAct < api.lengthSet:
            #         yusheCount = 0
            #         for i in range(len(api.stopStack)):
            #             if api.stopStack[i][2] == 6:
            #                 yusheCount += 1
            #                 api.stopStack[i][1] = api.lengthSet
            #                 break
            #         if yusheCount == 0:
            #             api.stopStack.append([0,api.lengthSet,6,0])
            #         api.stopStack.sort(key = lambda x:x[1], reverse = True)
            #         f = open(readPath + '\\stopStack.csv', 'w', newline='')
            #         csv.writer(f).writerows(api.stopStack)
            #         f.close()

            # elif api.MXlist[5][0] == 0:      #自动停机选择关闭，米数出栈
            #     for i in range(len(api.stopStack)):
            #         if api.stopStack[i][2] == 6:
            #             del api.stopStack[i]
            #             f = open(readPath + '\\stopStack.csv', 'w', newline='')
            #             csv.writer(f).writerows(api.stopStack)
            #             f.close()
            #             break
            # print(api.stopStack)               
            if api.readPLCclose == 1:
                break
            time.sleep(0.02)


class dataThread (threading.Thread):       #数据保存类
    def __init__(self, threadID, name, stopflag):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stop = stopflag

    def close(self):
        self.stop = 1

    def run(self):
        print ("Starting " + self.name)
        threading.Lock().acquire()
        timeNow = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        # path = writePath + '\\OriginalData\\' + timeNow + 'OriDatasaved.csv' 
        path2 = readPath + '\\Datasaved\\' + timeNow + 'Datasaved.csv'
        # f = open(path,'a+',newline='')
        f2 = open(path2,'a+',newline='')
        # titles = ['Index', 'Time', 'SpeedHigh', 'SpeedLow', 'LenghHigh', 'LengthLow']
        titles2 = ['Index', 'Time', 'SpeedLmitHigh', 'SpeedLmitLow', 'fangjuanFSetUp', 'fangjuanFSetDown', \
                    'Speed', 'LengthAct', 'QianshoujuanR','houshoujuanR', 'fangjuanActFUp','fangjuanRUp','fangjuanActFDown','fangjuanRDown', \
                    'Omega_Axis1_REAL','Position_Axis1_Act_REAL','Torque_Axis1_Act_REAL','Omega_Axis2_REAL','Position_Axis2_Act_REAL','Torque_Axis2_Act_REAL', \
                    'Omega_Axis3_REAL','Position_Axis3_Act_REAL','Torque_Axis3_Act_REAL','Omega_Axis6_REAL','Position_Axis6_Act_REAL','Torque_Axis6_Act_REAL', \
                    'Omega_Axis8_REAL','Position_Axis8_Act_REAL','Torque_Axis8_Act_REAL','buttonCollect']
        # total = 0
        total2 = 0
        if os.path.getsize(path2) == 0:
            csv.writer(f2).writerow(titles2)
            total2 = 1
        else:
            total2 = len(open(path2).readlines())

        while True:
            # lines = []
            lines2 = []
            for i in range(50):
                t = time.time()
                t1 = datetime.datetime.now()
                t1 = t1.strftime('%Y/%m/%d/%H:%M:%S')
                t2 = str('%.3f'%(t-int(t)))
                t3 = t1 + t2[1:5]

                lines2.append([total2, t3, api.SpeedLmitHigh, api.SpeedLmitLow, api.fangjuanFSetUp, api.fangjuanFSetDown, \
                                api.speedNow, api.lengthAct, api.QianshoujuanR,api.houshoujuanR,api.fangjuanActFUp, api.fangjuanRUp, api.fangjuanActFDown,api.fangjuanRDown, \
                                api.Omega_Axis1_REAL, api.Position_Axis1_Act_REAL, api.Torque_Axis1_Act_REAL, api.Omega_Axis2_REAL, api.Position_Axis2_Act_REAL, api.Torque_Axis2_Act_REAL, \
                                api.Omega_Axis3_REAL, api.Position_Axis3_Act_REAL, api.Torque_Axis3_Act_REAL, api.Omega_Axis6_REAL, api.Position_Axis6_Act_REAL, api.Torque_Axis6_Act_REAL, \
                                api.Omega_Axis8_REAL, api.Position_Axis8_Act_REAL, api.Torque_Axis8_Act_REAL, api.buttonCollect])
                # total += 1
                total2 += 1
                if api.dataclose == 1:
                    break
                time.sleep(0.02)
            # csv.writer(f).writerows(lines)
            csv.writer(f2).writerows(lines2)

            if api.dataclose == 1:
                break        
        print ("Exiting " + self.name)
        # f.close()
        f2.close()


class mainStateMachine(object):              # 主状态机
    def on_enter_idle(self):
        print('Python is on')
        self.to_createAPI()
    
    def on_enter_createAPI(self):
        global api
        api = Api()
        self.to_connectPLC()
    
    def on_enter_connectPLC(self):
        global client
        client = ModbusTcpClient('10.30.76.26')
        print('正在与PLC建立连接...')
        connection = client.connect()        
        if connection:
            self.to_readPLC()
        else:
            print('连接失败！请检查网线连接与PLC状态')
            time.sleep(3)
            self.to_connectPLC()
    
    def on_enter_readPLC(self):
        thread2 = readPLCThread(2,'Thread2',0)
        thread2.setDaemon(True)
        thread2.start()
        print('正在读取PLC数据...')
        time.sleep(0.2)
        self.to_connectCamera()
    
    def on_enter_connectCamera(self):
        target_host = "10.30.76.27"
        target_port = 8500
        global client2
        #建立socket对象
        socket.setdefaulttimeout(10)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #连接客户端
        print('正在与相机建立连接...')
        try:
            client2.connect((target_host,target_port))
            self.to_readCamera()
        except Exception:
            print('连接失败！请检查网线连接与相机状态')
            time.sleep(3)
            self.to_connectCamera()

    def on_enter_readCamera(self):
        thread3 = photoThread(3,'Thread3',0)
        thread3.setDaemon(True)
        thread3.start()
        print('正在读取相机数据...')
        time.sleep(0.2)
        self.to_createWindows()
    
    def on_enter_createWindows(self):
        global lineWin, knifeWin, peiFangWin, mainWin
        # makeDecision(updateFlawFile(flawFileFolderPath) + '\\ErrorData.csv')
        makeDecision(api.flawFilePath + '/ErrorData.csv')
        app = QtWidgets.QApplication(sys.argv)
        lineWin = MyGraphWindow()
        mainWin = myMainWindow()
        knifeWin = myKnifeAndPeifang()
        peiFangWin = peiFang()
        print('欢迎！')
        
        # WriteCsv()
        # print('gongwei test',findGongWeiNum(300),findGongWeiNum(500))
        # renewTargetsInStack()
        mainWin.show()
        sys.exit(app.exec_())


if __name__=='__main__':
    mainSM = mainStateMachine()
    machine0 = LockedMachine(mainSM,
                            states=['idle','createAPI','connectPLC','readPLC','connectCamera','readCamera','createWindows'],
                            initial='idle')
    mainSM.to_idle()
