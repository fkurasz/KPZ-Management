#=================================================
# Display brightness range controll program
# program check every 10 minutes if all displays are
# not above 90% lvl, if yes slowly change brightness
# to 90.
# Developed by KG,FK,PaN,PiN
#=================================================
import time
import os
import subprocess
import argparse
#=================COMMANDS============================
command_detect = "/bin/ddcutil detect"
command_detect_brightness = "/bin/ddcutil getvcp --bus "
command_set = "/bin/ddcutil setvcp --bus "
#=================Container============================
#collect bus number of current displays
Interface = {}
#this is default upper bound limit for brightness
LIMIT=80
#-------------------------------------------------------
#detect current displays and store they I2C number
#-------------------------------------------------------
def ddcutil_detect():
    process = subprocess.Popen(command_detect.split(),stdout = subprocess.PIPE)
    output, error = process.communicate()
    lines=output.decode().split("\n")
    current_display=0
    for line in lines:
        if(line==""): break                 
        linesplit=line.split()
        for word in linesplit:            
            if word == "Display":
                current_display=linesplit[1] 
                Interface[current_display]={}            
                break
            #------------------------------------------------------
            #check if this isI2C display
            #------------------------------------------------------
            if word == "Invalid":
                current_display=0   
                break
            #------------------------------------------------------
            #only for correct displays
            # collect bus number
            #------------------------------------------------------
            if current_display!=0:
                if word == "I2C":
                    Interface[current_display]["I2C"]=linesplit[2].split("-")[1]
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='DISPLAY CONTROL PROGRAM')
    parser.add_argument("-limit",action="store", type=int,help='set an upper limit for brightness in percents example: -limit 80')
    args = parser.parse_args()
    if args.limit:
        LIMIT = args.limit
    while True:
        
        #search for displays   
        ddcutil_detect()
        #------------------------------------------------------
        # for every display check brightness lvl (code 10)
        # if above 90 every 10sec lower lvl t othe point of 90%
        #repeate every 10 minuts
        #------------------------------------------------------
        for current_display in Interface:
            command = command_detect_brightness + Interface[current_display]["I2C"]+ " 10 --terse"
            process = subprocess.Popen(command.split(),stdout = subprocess.PIPE)
            output, error = process.communicate()
            words=output.decode().split(" ")
            while int(words[3])>LIMIT:
                command = command_set + Interface[current_display]["I2C"] + " 10 + 1"
                os.system(command)
                time.sleep(10)
        time.sleep(600)
  