#Date: July 21, 2021
#Author: Jimmy Majumder 
#Affiliation: Graduate student-M1, LSSE, Kyutech, Japan.  
# ©All rights to Shibatalaboratory, Kyutech, Japan.

import hebi
from time import sleep, time

lookup = hebi.Lookup() #initialization
# Wait 2 seconds for the module list to populate
sleep(10)

group = lookup.get_group_from_names(['X-series'], ['Left_wheel','Right_wheel'])
#group.command_lifetime = 20.0
if group is None:
    
    
    print('Group not found: Did you forget to set the module family and name above?')
    exit(1)
    
group_command = hebi.GroupCommand(group.size)
group_feedback = hebi.GroupFeedback(group.size)

#t = 0.0
#dt = 0.01 # 10 ms
while True:
    
    if group.get_next_feedback(reuse_fbk=group_feedback) is not None:  
        group_command.velocity=[+3,-3]
        group.send_command(group_command) 

    print((group_feedback.accelerometer[0]))
    sleep (2)
    #group_command.stop(.1000)

         
