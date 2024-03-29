import hebi
from time import sleep, time
import numpy as np
import threading
import csv
import time
lookup = hebi.Lookup() #initialization
a=""
m=0
# Wait 2 seconds for the module list to populate
sleep(2.0)



group = lookup.get_group_from_names(['Test'], ['wheel1', 'wheel2'])

if group is None:
    print('Group not found: Did you forget to set the module family and name above?')
    exit(1)

group_command  = hebi.GroupCommand(group.size)  #setting group commmand
group_feedback = hebi.GroupFeedback(group.size) #setting group feedback



def ou():
    global a
    while a=="1":
        if group.get_next_feedback(reuse_fbk=group_feedback) is not None:
            first_wheel=group_feedback.position[0]  #position of wheel 1
            second_wheel=group_feedback.position[1] #position of wheel 2
            if(group_feedback.accelerometer[0][0]>2):  
                #print("upper"+str(group_feedback.accelerometer[0][0]>1.0))
                group_command.position=[np.nan,np.nan]
                group_command.velocity=[-1,+1]
            
                group.send_command(group_command)
        
            elif(group_feedback.accelerometer[0][0]<0):
                group_command.velocity=[1,-1]
                group_command.position=[np.nan,np.nan]
                print("lower"+str(group_feedback.accelerometer[0][0]<-1.0))
                group.send_command(group_command)
            else:
                group_command.velocity=[np.nan,np.nan]
                group_command.position=[first_wheel,second_wheel]
                group.send_command(group_command)
                print("nothing")

            
def fil():
    global a
    start = time.time()
    with open('abc.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["time","velocity_1", "velocity_2", "effort_1","effort_2","position_1","position_2","acc_x","acc_y","acc_z","time_diff"])
        
        while a=="1":
            if group.get_next_feedback(reuse_fbk=group_feedback) is not None:
                t=time.time()-start
                with open('abc.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([t,group_feedback.velocity[0], group_feedback.velocity[1], 
                                     group_feedback.effort[0],group_feedback.effort[1],group_feedback.position[0],
                                     group_feedback.position[1],group_feedback.accelerometer[0][0],
                                     group_feedback.accelerometer[0][1],group_feedback.accelerometer[0][2],
                                     (group_feedback.receive_time[0]-group_feedback.transmit_time[0])])




while m==0:
    a=input("Enter 1 to start")
    if a=="1":
        thread_1 = threading.Thread(target=ou)
        thread_2 = threading.Thread(target=inn)
        thread_1.start()
        thread_2.start()
    if a=="0":
        m=1
