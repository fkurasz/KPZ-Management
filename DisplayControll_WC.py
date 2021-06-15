#=================================================
# Program controlling user display settings
# program have options to detect all displays,
# check and save actual parameters of specific display
# set userSettings from xml file if monitor model
# is same or set default displays for new models
# 
# Developed by KG,FK,PaN,PiN
#=================================================
import os
import re
import subprocess
import xml.etree.ElementTree as ET
import argparse

#=================GLOBAL===============
# main container for curent displays
Interface = {}
# user loaded settings
UserInterface = {}
# default settings for optimal power consumption
defaultSettings = {}
#=================COMMANDS=============
command_detect = "/bin/ddcutil detect"
command_getvcp = "/bin/ddcutil getvcp known --bus "
command_setvcp = "/bin/ddcutil setvcp "
#=================XML PATH=============
default_settings_xml = "defaultSettings.xml"
user_settings_xml = "userSettings.xml"
user_profiles_xml = "userProfile.xml"
user_whitecard_xml = "userWhiteCard.xml"
#======================================

#======================================
#=============FUNCTIONS================
#======================================


#=============Detect displays=========
#-------------------------------------
# fuction detect and save current displays
# parameters like i2c bus, model, mfg
#-------------------------------------
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
                #make adisctionary inside dictionary
                current_display=linesplit[1] 
                Interface[current_display]={}            
                break
            if word == "Invalid":
                current_display=0   
                break
            #only for correct displays
            if current_display!=0:
                if word == "I2C":
                    Interface[current_display]["I2C"]=linesplit[2].split("-")[1]
                if word == "Mfg":
                    Interface[current_display]["Mfg"]=linesplit[2]
                if word == "Model:":
                    Interface[current_display]["Model"]=linesplit[1]  


#=============Detect settings=========
#-------------------------------------
# fucntion detect settings of current
#  displays
# store them as a pair of VCP code and
# current value C
# it only collect info about editable 
# parameters
#-------------------------------------
def ddcutil_getvcp():
    for a in Interface:
        command = command_getvcp + Interface[current_display]["I2C"]+ " --terse --rw"
        process = subprocess.Popen(command.split(),stdout = subprocess.PIPE)
        output, error = process.communicate()
        lines=output.decode().split("\n")
        # for test only
        #lines = open("hetvcp2.txt","r").read().split("\n")
        Interface[current_display]["Parameters"]={}
        for line in lines:
            if(line==""): break                 
            linesplit=line.split()
            Interface[current_display]["Parameters"][linesplit[1]]=linesplit[3]

#=============Save Profile=========
#-------------------------------------
# save to xml file user profiles
# info about display numbers, I2C bus,
# Mfg and model
#-------------------------------------
def save_userProfiles():    
    data = ET.Element('Display')
    for display in Interface:
        item = ET.SubElement(data, "display")
        item.text=display
        for parameter in Interface[display]:
            if(parameter=="Parameters"): 
                continue
            subitem = ET.SubElement(item, parameter)
            subitem.text = Interface[display][parameter]

    newdata=ET.tostring(data)
    file = open(user_profiles_xml,"w")
    file.write(str(newdata.decode()))

#=============Save user settings=========
#-------------------------------------
# save info about user model and 
# editable code and they values
#-------------------------------------
def save_userSettings():
    data = ET.Element("Settings")
    for display in Interface:
        item = ET.SubElement(data, "Model")
        item.text = Interface[display]["Model"]
        for param in Interface[display]["Parameters"]:
            subitem = ET.SubElement(item,"Code")
            subitem.text = param
            subsubitem = ET.SubElement(subitem,"Value")
            subsubitem.text=Interface[display]["Parameters"][param]
 
    newdata=ET.tostring(data)
    file = open(user_settings_xml,"w")
    file.write(str(newdata.decode()))

#=========Load user profiles=========
#-------------------------------------
#-------------------------------------
#Not need for now
def load_userProfile():
    tree = ET.parse(user_profiles_xml)
    root = tree.getroot()
    for elem in root:
        print(elem.text)
        for subelem in elem:
            print(subelem.tag)
            print(subelem.text)

#==========Load user settings=========
#-------------------------------------
#-------------------------------------
def load_userSettings():
    tree = ET.parse(user_settings_xml)
    root = tree.getroot()
    for elem in root:
        UserInterface[elem.text]={}
        for subelem in elem:          
            for subsubelem in subelem:
                UserInterface[elem.text][subelem.text]=subsubelem.text
#=========Load default settings=========
#-------------------------------------
#-------------------------------------
def load_defaultSettings():
    tree = ET.parse(default_settings_xml)
    root = tree.getroot()
    for subelem in root:          
        for subsubelem in subelem:
            defaultSettings[subelem.text]=subsubelem.text

#===========Set Settings=============
#-------------------------------------
# For every current detected display
# check if there is any saved model
# that fits to current model
# if yes load saved settings
# if not set default settings
#-------------------------------------
def Set_Settings():
    for display in Interface:
        for model in UserInterface:
            if Interface[display]["Model"]==model:
                for code in UserInterface[model]:                    
                    os.system(str(command_setvcp+"--bus "+Interface[display]["I2C"]+code+""+UserInterface[model][code]))
            else:
                for code in defaultSettings:
                    os.system(str(command_setvcp+"--bus "+Interface[display]["I2C"]+code+""+defaultSettings[code]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='DISPLAY CONTROL PROGRAM')
    parser.add_argument("-start",action="store",help='load and set user settings')
    parser.add_argument("-save",action="store",help='save user settings')
#    parser.add_argument("-set", action="store",help='set settings')
    parser.add_argument("-default", action="store",help='set all settings to default')
    parser.add_argument("-wc", action="store",help='load and set user settings from whitecard if not in save xml')
    parser.add_argument("-wcall", action="store",help='load and set all user settings from whitecard')
    args = parser.parse_args()
    if args.start:
        ddcutil_detect()
        ddcutil_getvcp()
        load_defaultSettings()
        load_userSettings()
        Set_Settings()
    if args.save:
        ddcutil_detect()
        ddcutil_getvcp()
        save_userSettings()
    if args.default:
        ddcutil_detect()
        ddcutil_getvcp()
        load_defaultSettings()
        Set_Settings()
    if args.wc:
        ddcutil_detect()
        ddcutil_getvcp()
        user_settings_xml=user_whitecard_xml
        load_defaultSettings()
        load_userSettings()
        Set_Settings()
    if args.wcall:
        ddcutil_detect()
        ddcutil_getvcp()
        user_settings_xml=user_whitecard_xml
        load_defaultSettings()
        Set_Settings()


