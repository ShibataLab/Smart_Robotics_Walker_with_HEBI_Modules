from bluetooth import*
import hebi
import tkinter as tk #LIBRARY FOR GUI
from tkinter import *
from tkinter import messagebox, ttk
from time import sleep, time
import csv
import os
import numpy as np
import threading  #library for parallel processing 
import playsound
import speech_recognition as sr
#from threading import Thread
from PIL import ImageTk, Image
from gtts import gTTS #library for text to sound
from word2number import w2n #library for convering word to number




data2=""
fl=[]
rx=1
ble=1



root = Tk()  #instance for creating gui
var =0
newvar=0
pre=0
z=0
s1=0
xx=0
eff=0
eff1=0
aa=0
star=0
x=0
mm=0
text=""
oldvar=1
con=""

m=1
b=1
a=1

m=1
s=0
s1=0
s2=2
constant=0
constant1=0


qw=1
nn=1
options = [  
            "Velocity Control",
            "Torque Control",
            "Impedance Control"


]  #for options in gui 


lookup = hebi.Lookup()
group = lookup.get_group_from_names(['Wheel'], ['Right_light','Left_light'])

if group == None:
    pass
else:
    group_command=hebi.GroupCommand(group.size)
    group_feedback=hebi.GroupFeedback(group.size)




def bluetooth_esp32():     #esp32 connection configuration
	addr = "AC:67:B2:39:10:76" #address for esp32

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



def input_and_send(): #send data from raspberrypi/comp to ble esp32
	global ble
	global data2
	global fl
	while ble==1:
		data = "send"
		sock.send(data)
		sock.send("\n")
	sleep(2)
	lett=data2.split(",") #data sent with cooma so splitting
	lett.pop() #last element remove

	for item in lett:
		fl.append(float(item))


	write_file()


def write_file(): # writing received data to csv file
	global fl
	u=-3
	with open('new98.csv','a',newline='') as f:
		writer=csv.writer(f)
		writer.writerow(["time","toe","sole"])

	kk=len(fl)
	pk=int(kk/3)


	for p in range(pk):
		u=u+3
		with open('new98.csv','a',newline='') as f:
			writer=csv.writer(f)
			writer.writerow([fl[u]/1000,fl[u+1],fl[u+2]]) #converting milli seconds to seconds



def rx_echo():   #receiving data from esp32
    global data2
    global rx
    ##sock.send("\nsend anything\n")
    while rx==1:
        data = sock.recv(buf_size)
        data1= data.decode('UTF-8')
        data2=data2+data1






def check_audio():  #for configuring microphone 

    r = sr.Recognizer()
    r.energy_threshold = 6000  #threshold set according to background noise as actuators have some noise
    with sr.Microphone() as source:

        try:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            said = r.recognize_google(audio) #using google api
            print(r.energy_threshold)

        except:
            said ="not speaking"
            print(r.energy_threshold)
    return said.lower()


def speak(text): #function to generate sound that is from text to speech where computer as about enter desired speed etc
    global con
    tts = gTTS(text=text, lang="en")
    filename = "voice"+con+".mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)




def post_impedance(): #before stopping walker or applying brake we decrease effort in steps of 0.03 and 0.01 to avcid jerk
    global eff
    global eff1
    global another
    global another1
    global s1
    global xx
    global x
    xx=1
    if((group_feedback.velocity[1]-x)>=0.5):            #tw0 if statements belong to one wheel
        eff=eff-0.02
        group_command.effort =[-1*eff1,eff]
        group_command.position= [np.nan,np.nan]
        group.send_command(group_command)

    if(((-1*group_feedback.velocity[0])-x)>=0.5):
        eff1=eff1-0.02
        group_command.effort =[-1*eff1,eff]
        group_command.position= [np.nan,np.nan]
        group.send_command(group_command)

    if((group_feedback.velocity[1]>x) and (group_feedback.velocity[1] - x>0.09)):
        eff=eff-0.01
        group_command.effort =[-1*eff1,eff]
        group_command.position= [np.nan,np.nan]
        group.send_command(group_command)

    if(((-1*group_feedback.velocity[0])>x) and ((-1*group_feedback.velocity[0]) - x>0.09)):
        eff1=eff1-0.01
        group_command.effort =[-1*eff1,eff]
        group_command.position= [np.nan,np.nan]
        group.send_command(group_command)

    if(group_feedback.velocity[0]>=-0.1 and group_feedback.velocity[1]<0.1): #when this statements satisfy then store the value of position inorder to lock the wheels at that position
        another=group_feedback.position[0]
        another1=group_feedback.position[1]
        xx=0.2
        s1=2


def acceleration(): #function for acceleration in steps that is step of 0.03 and 2 if statements for one wheel
    global eff
    global eff1
    global x
    print(x)
    if((x - group_feedback.velocity[1])>=0.5):
        eff=eff+0.02
    if(((x-0.57) - (-1*group_feedback.velocity[0]))>=0.5):
        eff1=eff1+0.02
    if((x>group_feedback.velocity[1]) and (x - group_feedback.velocity[1]>0.09)):
        eff=eff+0.01
    if(((x-0.57)>(-1*group_feedback.velocity[0])) and ((x-0.57) - (-1* group_feedback.velocity[0]>0.09))):
        eff1=eff1+0.01


def vel_algo(): #this is with velocity algorithm which is generally not used we are using effort
    global z
    global pre
    global spring_constant
    global x

    if(x>pre or x==pre):
        y=(x-pre)/10
        z=z+y
        if(z<x and (z-group_feedback.velocity[1]<0.7)):
            spring_constant=z

        else:
            pre=x
            z=x
            spring_constant=z
                    
    elif(x<pre or x==pre):
        y=(pre-x)/10
        z=z-y
        if(z>x and (group_feedback.velocity[1]-z<0.7)):
            spring_constant=z

        else:
            pre=x
            z=x
            spring_constant=x



def vel_post_impedance(): #this is for stopping walker when velocity algo is used instead of effort
    global z
    global pre
    global spring_constant
    global another
    global another1
    global s1
    global xx
    global x


    if((x<pre or x==pre) and s1==1):
        y=(pre-x)/10
        z=z-y
        if(z>x and (group_feedback.velocity[1]-z<0.7)):
            spring_constant=z

        else:
            pre=x
            z=x
            spring_constant=x
        group_command.effort=[np.nan,np.nan]
        group_command.velocity=[-1*spring_constant,spring_constant]
        group_command.position=[np.nan,np.nan]    
        group.send_command(group_command)

        if(group_feedback.velocity[0]>=-0.1 and group_feedback.velocity[1]<0.1):
            #print("bello")
            another=group_feedback.position[0]
            another1=group_feedback.position[1]
            xx=0.2
            s1=2

def file_handle(): #in this function we are generating a csv file with some output feedback and command parameters from actuators
	global qw
	global nn
	global s1
	global mmm
	while qw==1:
		if group.get_next_feedback(reuse_fbk=group_feedback) is not None:
			if nn==1:
				start = time()
				nn=2
				with open('gcu1u.csv','a',newline='') as f:
					writer=csv.writer(f)
					writer.writerow(["time","fbkV_R","fbkV_L","comV_R","comV_L","fbkE_R","fbkE_L","comE_R","comE_L","fbkP_R","fbkP_L","comP_R","comP_L","tick_D","state"])
			if nn==2:
				d = time() - start
				with open('gcu1u.csv','a',newline='') as f:
					writer = csv.writer(f)
					outputdata = [
						d,   
						group_feedback.velocity[0],
						group_feedback.velocity[1],
						group_feedback.velocity_command[0],
						group_feedback.velocity_command[1],
						group_feedback.effort[0],
						group_feedback.effort[1],
						group_feedback.effort_command[0],
						group_feedback.effort_command[1],
						group_feedback.position[0],
						group_feedback.position[1],
						group_command.position[0],
						group_command.position[1],
						mmm, #distance multiplied by ticks
						s1
						]
					writer.writerow(outputdata)
def velocity_control():  #this is for acceleration in case of velocity command which generally we are not using
    global spring_constant
    group_command.velocity=[-1*spring_constant,spring_constant]
    group_command.position=[np.nan,np.nan]
    group_command.effort=[np.nan,np.nan]
    group.send_command(group_command)




def deacceleration(): #this is deacceleration part in case of effort algorithm 
    global eff
    global eff1
    global x
    if((group_feedback.velocity[1]-x)>=0.5):
        eff=eff-0.02

    if(((-1*group_feedback.velocity[0])-x)>=0.5):
        eff1=eff1-0.02

    if((group_feedback.velocity[1]>x) and (group_feedback.velocity[1] - x>0.09)):
        eff=eff-0.01

    if(((-1*group_feedback.velocity[0])>x) and ((-1*group_feedback.velocity[0])-x>0.09)):
        eff1=eff1-0.01


def position_control(): #this function helps in locking of wheels at last saved position of actuators
    global another
    global another1
    global xx
    xx=0.3
    group_command.position=[another,another1]
    group_command.effort= [np.nan,np.nan]
    group_command.velocity= [np.nan,np.nan]
    group.send_command(group_command)

def torque_control(): #this function is for passing effort parameters to the actuators as calculated in above functions by incrementing
    global eff
    global eff1
    global text
    group_command.effort =[-1*eff1,eff]
    group_command.position= [np.nan,np.nan]
    group_command.velocity= [np.nan,np.nan]
    group.send_command(group_command)




def Setting(): #this function is used for setting some initial actuator parameters
    #group_command.reference_effort = [0,0]

    new_velocity_kp_gains = [0.01, 0.01]
    new_effort_kp_gains = [0, 0]

    for new_gain in new_velocity_kp_gains:
        for i in range(group.size):
            group_command.velocity_kp = new_gain
        if not group.send_command_with_acknowledgement(group_command):
            print('Did not get acknowledgement from module when sending gains. Check connection.')
            exit(1)


    for new_gain in new_effort_kp_gains:
        for i in range(group.size):
            group_command.effort_kp = new_gain
        if not group.send_command_with_acknowledgement(group_command):
            print('Did not get acknowledgement from module when sending gains. Check connection.')
            exit(1)



def stop_walker(): #this helpos in stopping walker and teriminating some loops
    global s1
    global constant
    global xx
    global x
    global mm
    xx=1
    s1=1
    constant = 0
    #key = var
    x = 0
    mm = 0


def opertate_walker(): #a function that use above mentioned functions to operate the walker. used state 5 state positions with s2 and s1
	global s2 #in order to pass it from all states e-g (not moving, initial movement, acceleration, constant acceleration)
	global constant # (deacceleration, stop and lock wheels all  these are different state positions)
	global constant1
	global s1
	global m
	global mmm
	global x
	while m==1:
		if group.get_next_feedback(reuse_fbk=group_feedback) is not None:

			if s2==2:
				mmm = constant1*12.333    #distance multiplied by ticks
				x= constant*2
				aa = group_feedback.position[1]
				s2=3
				s1=0
				print(mm+aa)
				Setting()


			if s2==4:
				x=constant*2
				s2=5


			if(group_feedback.position[1]<(mmm+aa) and s1==0):
				if(group_feedback.velocity[1]>0.2):
					acceleration()
					deacceleration()
					torque_control()


			elif(s1==1):
				post_impedance()

			elif(s1==2):
				position_control()


			elif(group_feedback.position[1]>=(mmm+aa)):
				stop_walker()


def clicked(): #this function for voice speak with speech to text and text to speech functions
	global constant1
	global constant
	global m
	global qw
	global con
	global ble
	global rx
	b=0
	c=0
	a=1
	ab=7
	y=""
	con="1"
	while a==1:
		y=check_audio()
		res = [int(i) for i in y.split() if i.isdigit()] #this gives us number spoken in a sentence (eg i want  5 mangoes it will return 5)

		if(len(res)==0):
			try:
				res=w2n.word_to_num(y)
				res=str(res)
				print("tint")
			except:
				pass
		
		#y=input("enter")
		print(y)
		if "start" in y:
			speak("what is your desired distance")
			ab=0
			con="2"
			y=""
			c=1
			rx=1
			ble=1
			bluetooth_esp32()

		elif len(res)==0 and c==1 and "stop" not in y:
			speak("Please confirm desired distance again")
			con="6"


		elif len(res) >0 and ab==0:
			constant1=int(res[0])   #distance
			print(constant1)
			print(type(constant1))
			speak("what is your desired speed from 1 to 5. 5 being the fastest ")
			ab=2
			c=2
			con="3"
			y=""


		elif len(res) ==0 and c==2 and "stop" not in y:
			speak("Please confirm your desired speed again")
			con="7"


		elif len(res)>0 and ab==2:
			c=3
			constant=int(res[0])  #speed
			print(constant)
			print(type(constant))
			speak("You can start the rehabilitation with distance of"+str(constant1)+"and speed of"+str(constant))
			con="4"
			new_thread = threading.Thread(target=opertate_walker)
			new_thread.start()
			wow_thread = threading.Thread(target=file_handle)
			wow_thread.start()
			one_thread = threading.Thread(target=input_and_send)
			two_thread = threading.Thread(target=rx_echo)
			one_thread.start()
			two_thread.start()
			y=""
			ab=4


		elif "stop" in y:
			print("2 is entered and end")
			stop_walker()
			speak("walker has stopped")
			a=2
			m=3
			qw=3
			ble=3
			rx=3
			#s=2
			con="5"

		elif ("adjust" in y or "speed" in y) and len(res)==0 and c==3:
			speak("Please confirm your adjusted speed again")
			con="8"


		elif ("adjust" in y or "speed" in y) and len(res)>0 and c==3:
			s2=4
			constant=int(res[0])
			speak("Your speed is adjusted to" +str(constant)+ "meters per second")
			con="9"

		else:
			pass

class MyThread(threading.Thread):  #creating a thread to run multiple functions in a time
    
    def __init__(self):
        super(MyThread, self).__init__()
        self.com = np.zeros(2)    #with two zeros matrix
        self.stop_event = threading.Event()   #condition for stopping the thread event
        self.csv_name = ''
        self.new_dir_path = None
        
    def stop(self):
        self.stop_event.set()     # function for stopping event
        
    def run(self):
        global x
        global mm
        global aa
        global xx
        global s1
        global my_combo
        global music_thread
        global star
        global dd


        csvfile = self.new_dir_path            
        start = time()
        #x = self.com[0]
        #mm = self.com[1]*12.333
        #print("mm:outloop")
        #init_eff = group.get_next_feedback().effort
        while not self.stop_event.is_set():

            if group.get_next_feedback(reuse_fbk=group_feedback) is not None:
                #x = self.com[0]
                #mm = self.com[1]*12.333
                #print("inloop")
                #print(x)
                #print(mm)
                #print(aa)

                global pre
                global z
                global oldvar

            group.get_next_feedback(reuse_fbk=group_feedback)

            if(my_combo.get()=="Torque Control"): #this is effort/torque algorithm ehich we use most of the time
                #print("mm:torlop")



                if(group_feedback.position[1]<(mm+aa) and s1==0):
                    xx=0

                    if(group_feedback.velocity[1]>0.4):
                        acceleration()
                        deacceleration()
                        torque_control()

                        print("lgaya")
                        


                        #print("guzra")


                        xx=0
                elif(s1==1):
                    post_impedance()

                elif(s1==2):
                    position_control()

                elif(group_feedback.position[1]>=(mm+aa)):
                    dd=2
                    stop_walker()
                    oldvar=2


            elif(my_combo.get()=="Velocity Control"): #this we dont use mainly it use velocity control approach
                if(group_feedback.position[1]<(mm+aa) and s1==0):
                    xx=0
                    if(group_feedback.velocity[1]>0.4):
                        vel_algo()
                        velocity_control()

                        xx=0
                elif(s1==1):
                    vel_post_impedance()
                elif(s1==2):
                    position_control()

                elif(group_feedback.position[1]>=(mm+aa)):
                    dd=2
                    stop_walker()    




            d = time() - start
            with open(csvfile,'a', newline='') as f:   #for data collecting in file
                    writer = csv.writer(f)
                    outputdata = [
                         d,   
                         group_feedback.velocity[0],
                         group_feedback.velocity[1],
                         group_feedback.velocity_command[0],
                         group_feedback.velocity_command[1],
                         group_feedback.effort[0],
                         group_feedback.effort[1],
                         group_feedback.effort_command[0],
                         group_feedback.effort_command[1],
                         group_feedback.position[0],
                         group_feedback.position[1],
                         group_command.position[0],
                         group_command.position[1],
                         mm,
                         xx
                         ]   #correct indentation please
                    writer.writerow(outputdata)
                    
    def Move(self, key,key2):   #function for moving the entered speed
        com = self.com
        com[0] = float(key)/0.075   #converting it into float
        com[1] = float(key2)
        print(com[0])
        print(com[1])
        self._com = com
    
    def MakeSomething(self):   #functtion for creating folder and csv file
        new_dir_path = "./" + n_fold
        os.makedirs(new_dir_path, exist_ok=True)
        csv_name = n_fil
        self.csv_name = csv_name
        self.new_dir_path = os.path.join(new_dir_path, csv_name + '.csv')

def on_entry_click(event):
    """function that gets called whenever entry is clicked"""
    if e.get() == 'Speed in (m/s)':
       e.delete(0, "end") # delete all the text in the entry
       e.insert(0, '') #Insert blank for user input
       e.config(fg = 'black')


def on_focusout(event): #grey colored in gui text written for marking
    if e.get() == '':
        e.insert(0, 'Speed in (m/s)')
        e.config(fg = 'grey')

def on_entry_click1(event):
    """function that gets called whenever entry is clicked"""
    if ee.get() == 'Distance in (m)':
       ee.delete(0, "end") # delete all the text in the entry
       ee.insert(0, '') #Insert blank for user input
       ee.config(fg = 'black')

       
def on_focusout1(event):
    if ee.get() == '':
        ee.insert(0, 'Distance in (m)')
        ee.config(fg = 'grey')





def send_name():  #for sending names of csv file and folder
    global n_fold
    n_fold = e1.get()
    global n_fil
    n_fil = e2.get()
    global th
    Setting()
    th = MyThread()
    th.MakeSomething()   #for creating csv file and folder
    th.start()   #starting the thread as the name enters
    new2.destroy()


def open_new():   #opening of another window for folder setting
    

    global new2
    global newvar
    new2=Toplevel()
    new2.title("Folder Settings")
    new2.geometry("225x85")
    new2.resizable(width=False,height=False)

    open_frame = Frame(new2,width =400, height=600, bg="darkseagreen1")
    open_frame.pack(fill="both", expand=1)
    newvar=1

    e1_label = Label(open_frame, text="Folder Name", fg="black", bg="darkseagreen1", font=("Helvtica",10)).grid(row=0)
    global e1
    e1= Entry(open_frame,width=20)
    e1.grid(row=0,column=1)
    e2_label =Label(open_frame, text="CSV File Name", fg="black", bg="darkseagreen1", font=("Helvtica",10)).grid(row=1)
    global e2
    e2 = Entry(open_frame, width=20)
    e2.grid(row=1,column=1)

    set_button = Button(open_frame, text="Set", fg="white", bg="blue4", width=6, height=1, font=("Helvtica",10,"bold"), command=send_name)
    set_button.grid(row=4,column=1, pady=5)

def in_speed():  #input button for entering speed/force (infuture)
    global var
    global var2
    global s1
    global aa
    global star
    global th
    global start_thread
    global new_thread
    global mm
    global x
    if group.get_next_feedback(reuse_fbk=group_feedback) is not None:
        aa = group_feedback.position[1]
       #print(aa)
    s1=0
    if(newvar>0):
        star=0
        var=e.get()
        var2=ee.get()
        global key
        global key2

        #print("taken")
        if(var!='q'):
            #start_thread = threading.Thread(target=play_start_music)
            #start_thread.start()
            x = float(var)/0.075
            mm = float(var2)*12.333
            #th.Move(key,key2)


        if 'q' in var:  #for stopping enter q
            sleep(1)
            star=2
            th.stop()
        else:
           #print("masla")
            x = float(var)/0.075
            mm = float(var2)*12.333
    else:
        responsey = messagebox.showerror("Error","Folder not set. Set folder first then input speed")




def Hebi_Status():  #function for  looking up hebi module
    lookup = hebi.Lookup()
    global group
    group = lookup.get_group_from_names(['Wheel'], ['Right_light','Left_light'])
    module_type=[]
    module_name=[]
    module_macaddress=[]
    

    if group == None:
        response = messagebox.showerror("Hebi Module", "No module found. Check connection again!")  #messagebox if not connected
    
    else:
        response1 = messagebox.askyesno("Hebi Module", "Module successfully connected. Do you want to see details of connected module?") #messagebox if connected
        if(response1==1):
            for entry in lookup.entrylist: #looking up for entry/family list of hebi module
                module_type.append(entry.family)
                module_name.append(entry.name)
                module_macaddress.append(entry.mac_address)
            global new  
            new=Toplevel()  #creating new window
            new.title("Details")
            new.geometry("420x120")
            new.resizable(width=False,height=False)
            my_frame = Frame(new,width=262,height=200,bd=2,bg="turquoise",relief="sunken") #adding frame
            my_frame.pack(fill="both",expand=1) #for frmae covering all window
            type_label = Label(my_frame, text="Type of module: " + module_type[0], bg="turquoise", font=("Helvetica",15))
            type_label.grid(row=0,column=0) #for entering module type
            name_label = Label(my_frame, text="Name of module: " + module_name[0] + " & " + module_name[1],bg="turquoise", font=("Helvetica",15))
            name_label.grid(row=1,column=0) #for entering module name
            macaddress_label_1 = Label(my_frame, text="MAC Adress of module 1: " + str(module_macaddress[0]), bg="turquoise", font=("Helvetica",15))
            macaddress_label_1.grid(row=2,column=0) #for entering module address
            macaddress_label_2 = Label(my_frame, text="MAC Adress of module 2: " + str(module_macaddress[1]), bg="turquoise", font=("Helvetica",15))
            macaddress_label_2.grid(row=3,column=0) #for entering module address






def use_walker():  #main apllication window
    
    if group==None:
        respone=messagebox.showerror("Hebi Module", "No module found. Check connection again")
    else:
        new1=Toplevel() #subwindow in main window
        new1.title("Operating Walker")
        new1.geometry("270x250")
        new1.resizable(width=False,height=False)
        
        add_frame11 = Frame(new1,width =400, height=600, bg="darkseagreen1")
        add_frame11.pack(fill="both", expand=1)
        
        y_label=Label(add_frame11,text="Enter Speed and Distance", fg="black", bg="white", font=("Helvetica",16)).pack(pady=15)
        global e
        global ee
        global my_combo
        my_combo = ttk.Combobox(add_frame11, value =options, state='readonly',width=17)
        my_combo.current(0)
        my_combo.pack(pady =5)
        e= Entry(add_frame11,width=20,bd=1)   #for inputbox
        e.insert(0,'Speed in (m/s)')
        e.bind('<FocusIn>', on_entry_click)
        e.bind('<FocusOut>', on_focusout)
        e.config(fg = 'grey')
        ee = Entry(add_frame11,width=20)
        e.pack(pady=5)
        ee.insert(0,'Distance in (m)')
        ee.bind('<FocusIn>', on_entry_click1)
        ee.bind('<FocusOut>', on_focusout1)
        ee.config(fg = 'grey')
        ee.pack()
        
        
        input_button = Button(add_frame11, text="Enter", fg="white", bg="blue4",width=12, height=1, font=("Helvtica",10,"bold"), command=in_speed)
        input_button.pack(pady=5)
        folder_button = Button(add_frame11, text="Set Folder", fg="white", bg="blue4",width=12, height=1, font=("Helvtica",10,"bold"), command=open_new)
        folder_button.pack(pady=5)
        stop_button = Button(add_frame11, text="Stop", fg="white", bg="Red",width=12, height=1, font=("Helvtica",10,"bold"), command=stop_walker)
        stop_button.pack(pady=5)

    #new1.mainloop()

root.title("Walker Interface") #for title of window

root.geometry("210x670")  #size of window

root.resizable(width=False,height=True)


main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)


my_canvas = Canvas(main_frame,bg="DarkSlateGray1")
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

my_scrollbar = ttk.Scrollbar(my_canvas, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT,fill=Y)

my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))



add_frame = Frame(my_canvas,width =400, height=600, bg="DarkSlateGray1")
add_frame.pack(fill="both", expand=1)

my_canvas.create_window((0,0), window=add_frame, anchor="nw")

logo_image = ImageTk.PhotoImage(Image.open("logo1.png")) #adding logo
logo_label = Label(add_frame, image=logo_image, bg="DarkSlateGray1")
logo_label.pack()


my_label = Label(add_frame, text= "Smart Walker", fg="Dodgerblue2", bg="white", font=("Helvtica",20)).pack(pady=10) #fg to change text color here,bg for text background

my_image = ImageTk.PhotoImage(Image.open("circle1.png"))
image_label = Label(add_frame, image=my_image, bg="DarkSlateGray1")
image_label.pack(pady=5)

my_button  = Button(add_frame, text="Hebi Module Status", fg="white", bg="blue4", font=("Helvtica",10,"bold"), width=15, height =2, command=Hebi_Status, relief=RAISED)  #button for checking Hebi Module Status
my_button1 = Button(add_frame, text="Use Walker", fg="white", bg="blue4",  font=("Helvtica",10,"bold"), width=15, height =2,  command=use_walker, relief=RAISED)  # button for performing test
my_button2 = Button(add_frame, text="Data Logging", fg="white", bg="blue4", font=("Helvtica",10,"bold"), width=15, height =2, command=clicked, relief=RAISED)  # button for Data Logging
my_button3 = Button(add_frame, text="Help", fg="white", bg="blue4", width=15, font=("Helvtica",10,"bold"), height =2, command=clicked, relief=RAISED)  # button for Help
my_button.pack(pady=5) 
my_button1.pack(pady=5)  
my_button2.pack(pady=5)
my_button3.pack(pady=5)

root.mainloop()