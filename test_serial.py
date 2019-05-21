import serial.tools.list_ports as port_list
import serial

ports = list(port_list.comports())
for p in ports:
    print (p)

s = serial.Serial('COM7')
s.baudrate = 115200

while True:
    res = s.read(3)
    id = int(res[0])
    turn = int(res[1])
    roll = int(res[2])
    print(res)
    print('Id:', id)
    print('Turn:', turn)
    print('Roll:', roll)