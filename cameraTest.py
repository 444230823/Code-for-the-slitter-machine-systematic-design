import socket

target_host = "10.30.76.27"
target_port = 8500
global client2
#建立socket对象
socket.setdefaulttimeout(10)
client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client2.connect((target_host,target_port))

tt = 16
msg = 'MR'
msagint = []
for i in range(tt):
    msg += ',#L0000[' + str(i) + ']'
for i in range(tt+7):
    msagint.append(0)
# qq = (time.time())
msg = bytes(msg+'\r',encoding="utf-8")
client2.send(msg)
msag = client2.recv(4096).decode('utf-8')
print(msag)