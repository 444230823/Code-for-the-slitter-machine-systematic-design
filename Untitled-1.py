from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys
import time
import struct
from pymodbus.client.sync import ModbusTcpClient


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

client = ModbusTcpClient('10.30.76.26')
connection = client.connect()
try:
    client.read_holding_registers(9,1)
except Exception as e:
    print(e)
if connection:
    request1 = client.read_holding_registers(9,1).registers
    buttonList = dec_to_binlist(request1[0],16)        
    print(buttonList)
    result1 = client.read_holding_registers(562,2).registers
    dealtype = dec_to_float(result1[0],result1[1])
    print('dealtype:',dealtype)
    buttonList[4] = 0   # DealDone
    buttonList[5] = 0   # PopStart
    buttonList[7] = 0   # CloseSubWin
    command = binlist_to_int(buttonList)
    client.write_register (value=command, unit=2, address=9)    # 主屏幕弹窗启动
    request1 = client.read_holding_registers(9,1).registers
    buttonList = dec_to_binlist(request1[0],16)        
    print(buttonList)
    client.write_registers (values=inverse(0), unit=2, address=560, data_format='!f')  # StopType
#     client.write_registers (values=inverse(0), unit=2, address=562, data_format='!f')  # DealType

class Ui_lineWindow(object):               
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.closeW = QtWidgets.QPushButton(self.centralwidget)
        self.closeW.setGeometry(QtCore.QRect(0, 0, 100, 80))
        self.closeW.setObjectName("closeW")
        self.retranslateUi(MainWindow) 
        QtCore.QMetaObject.connectSlotsByName(MainWindow)        

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.closeW.setText(_translate("MainWindow", "关闭"))

class MyGraphWindow(QtWidgets.QMainWindow,Ui_lineWindow):   
    def __init__(self):
        super(MyGraphWindow,self).__init__()
        self.setupUi(self)
        self.closeW.clicked.connect(self.pop)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.mainTimer)
        self.timer.start(200)
    
    def pop(self):
        client.write_registers (values=inverse(3), unit=2, address=560, data_format='!f')
        self.popwin = MyGraphWindow2()
        self.popwin.show()
    
    def mainTimer(self):
        request1 = client.read_holding_registers(9,1).registers
        buttonList = dec_to_binlist(request1[0],16)        
        if buttonList[4]:
            result1 = client.read_holding_registers(562,2).registers
            dealtype = dec_to_float(result1[0],result1[1])
            print('dealtype:',dealtype)
            buttonList[4] = 0   # DealDone
            # buttonList[5] = 1   # PopStart
            # buttonList[7] = 1   # CloseSubWin
            command = binlist_to_int(buttonList)
            client.write_register (value=command, unit=2, address=9)
            self.popwin.close()
        else:
            pass



class Ui_lineWindow2(object):               
    def setupUi(self, Window2):
        Window2.setObjectName("Window2")
        Window2.resize(200, 200)
        self.centralwidget = QtWidgets.QWidget(Window2)
        self.centralwidget.setObjectName("centralwidget")
        self.closeW = QtWidgets.QPushButton(self.centralwidget)
        self.closeW.setGeometry(QtCore.QRect(20, 20, 100, 80))
        self.closeW.setObjectName("closeW")
        self.retranslateUi(Window2) 
        QtCore.QMetaObject.connectSlotsByName(Window2)        

    def retranslateUi(self, Window2):
        _translate = QtCore.QCoreApplication.translate
        Window2.setWindowTitle(_translate("Window2", "Window2"))
        self.closeW.setText(_translate("Window2", "关闭"))

class MyGraphWindow2(QtWidgets.QMainWindow,Ui_lineWindow2):   
    def __init__(self):
        super(MyGraphWindow2,self).__init__()
        self.setupUi(self)
        self.closeW.clicked.connect(self.send)
    
    def send(self):
        request1 = client.read_holding_registers(9,1).registers
        buttonList = dec_to_binlist(request1[0],16)        
        print(buttonList)
        result1 = client.read_holding_registers(562,2).registers
        dealtype = dec_to_float(result1[0],result1[1])
        print('dealtype:',dealtype)
        # buttonList[4] = 0   # DealDone
        buttonList[5] = 1   # PopStart
        # buttonList[7] = 1   # CloseSubWin
        command = binlist_to_int(buttonList)
        client.write_register (value=command, unit=2, address=9)    # 主屏幕弹窗启动


# if __name__=='__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     win = MyGraphWindow()
#     win.show()
#     sys.exit(app.exec_())