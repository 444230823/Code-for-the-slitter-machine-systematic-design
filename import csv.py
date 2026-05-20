from modulefinder import IMPORT_NAME
import pandas as pd
import os
from pymodbus.client.sync import ModbusTcpClient
import struct
import csv
def inverse(a):                       #调换高低位(向PLC发数据)
    a0 = struct.pack('>f', float(a)).hex()
    a1 = a0[0:4]
    a2 = a0[4:8]
    return [int(a2,16),int(a1,16)]

k=[i for i in range(5)]
k=[i for i in range(5)]
print(k)
# badMetersFilepath = os.getcwd() + '\\realData.csv'
# badMetersdata = pd.read_csv(badMetersFilepath,encoding='GBK',header=None)
# print(badMetersdata[0].values.tolist())
# print(badMetersdata.index)
# client = ModbusTcpClient('10.30.76.26')
# print('正在与PLC建立连接...')
# connection = client.connect()  
# client.write_registers (values=inverse(2), unit=2, address=300, data_format='!f')
# f3 = open('knifeUsing.csv','r',newline='')
# reader = csv.reader(f3)
# # print('length',len(reader))
# for a in reader:
#     for i in range(12):
#         a[i] = int(a[i])
#     # for i in range(23):
#     #     if (i == 0) | ((i >= 5)&(i <= 15)) | ((i >= 17)&(i <= 20)):
#     #         a[i] = float(a[i])
#     print(a)
# f3.close()
# f3 = open('KnifeFile.csv','r',newline='')
# reader = csv.reader(f3)
# tt = 0
# aa = {}
# for a in reader:
#     if tt == 0:
#         tt += 1
#     elif tt == 1:
#         aa[int(a[0])] = float(a[1])
# f3.close()
# print(len(aa))
# for i in aa.keys():
#     print(aa[i])
# column = [1,2,3,4,5,6,7,8,9,10,11,12]
# data = [1,1,1,0,0,0,0,0,0,0,0,0]
# dfdf = pd.DataFrame(columns=column,index=None)
# dfdf.loc[1] = data
# dfdf.to_csv('knifeUsing.csv',index=False)