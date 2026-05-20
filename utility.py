import struct
import time

def microTimer(t):      #毫秒定时器，t单位为毫秒
    start,end = 0,0
    start = time.time()
    t = t/1000
    while end-start<t:
        end = time.time()

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
    return(ret)


