from bluetooth import*
import threading
import csv
from time import sleep
data2=""
fl=[]
def input_and_send():
    global data2
    global fl
    for x in range(5):
        data = "send"
        sock.send(data)
        sock.send("\n")
    sleep(2)    
    lett=data2.split(",")
    lett.pop()
    
    for item in lett:
        fl.append(float(item))
        

    print(fl)
    write_file()
        
def write_file():
    u=-3
    with open('abcd.csv','a',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(["time","toe","sole"])
    
    kk=len(fl)
    pk=int(kk/3)
    
    for p in range(pk):
        u=u+3
        with open('abcd.csv','a',newline='') as f:
            writer=csv.writer(f)
            writer.writerow([fl[u]/1000,fl[u+1],fl[u+2]])
            
        
def mx():
    global data2
    print(data2)
def rx_echo():
    global data2
    ##sock.send("\nsend anything\n")
    while True:
        data = sock.recv(buf_size)
        data1= data.decode('UTF-8')
        data2=data2+data1
        #if data:
            #print(data2)
            #sock.send(data)
            
addr = "AC:67:B2:39:10:76"

service_matches = find_service(address=addr)

buf_size = 1024;

if len(service_matches)==0:
    print("could not find sample server")
    sys.exit(0)
    
for s in range(len(service_matches)):
    print("\nservice_matches: [" + str(s) + "]:")
    print(service_matches[s])
    
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

port=1
print("connecting to \"%s\" on %s,port %s" %(name,host,port))

sock=BluetoothSocket(RFCOMM)
sock.connect((host,port))

print("connected")

new_thread=threading.Thread(target=input_and_send)
new_thread.start()
new_thread1=threading.Thread(target=rx_echo)
new_thread1.start()
#input_and_send()
#rx_echo()
#sock.close()
#print("bye")