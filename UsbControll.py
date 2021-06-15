#============================================
# Program controlling usb devices power supply
# developed by KG, FK, PaN, PiN
#============================================
import os
import re
import subprocess
import xml.etree.ElementTree as ET
import argparse
# ============ Definitions ===================
#here are saved found devices
foundDevices_file = "devices_t.txt"
#path to xml containing vendor_id
xml_patch_vendor = "vendor_id.xml"
#path to xml containing product_id
xml_patch_product = "product_id.xml"
#path to xml containing device class
xml_patch_class = "device_class.xml"
#path to xml containing off devices
xml_patch_offdevices = "offdevices.xml"
#path to usb devices config
devices_localization = "/sys/bus/usb/devices/"
#---------------------------------------------
#containers
#---------------------------------------------
# curreent devices
DEVICES = {}
# devices with matching vendor id
DEVICES_VID= {}
# devices with matching product id
DEVICES_PID= {}
# list of product id to be shut down
PRODUCT_ID = []
# list of vendor id to be shut down
VENDOR_ID = []
# list of devices classes that are not to be shut down
CLASSES = []
#suppor table for xml loading
XMLS = [xml_patch_vendor,xml_patch_product,xml_patch_class]
# turned off devices
TURNED_OFF_DEVICES = []
#---------------  MACRO  ---------------------
S = " >> "
# --------------------------------------------
# ------------- COMMANDS ---------------------
# --------------------------------------------
bash_command_lsusb = "lsusb"
bash_command_tree = "lsusb -t"
bash_command_verbose = "lsusb -v"
turn_off = "echo \"0\" > \""
turn_on = "echo \"auto\" > \""
turn_on_delay = "echo \"2000\" > \""
turn_off_end = "/power/autosuspend_delay_ms\""
turn_on_end = "/power/control\""

#============== FUNCTIONS ======================
#-------------READ XML--------------------------
#read from XML file specified device_id 
# or class_id
#create xml parser and read files
#-----------------------------------------------
def read_xml():
    i=0
    for xml in XMLS:
        i+=1
        tree = ET.parse(xml)
        root = tree.getroot()
        for elem in root:
            #print(elem.text)
            if i==1:
                VENDOR_ID.append(elem.text)
            if i==2:
                PRODUCT_ID.append(elem.text)
            if i==3:    
                CLASSES.append(elem.text)

   # print(VENDOR_ID)            
   # print(PRODUCT_ID)
   # print(CLASSES)

#---------------------------------------------
#-------------READ DEVICE CLASS---------------
#read devices from lsusb -t command
#and read device class
#-----------------------------------------------
def read_devices_class():
    process = subprocess.Popen(bash_command_tree.split(),
     stdout = subprocess.PIPE)
    output, error = process.communicate()
    str_lines=output.decode().split("\n")
    #getting device number
    if str_lines.__sizeof__ != 0:
        for line in str_lines:
            if(line==""): break
            print(line)
            line_split = line.split()
            if re.search(r'/:', line_split[0]):
                BUS=line_split[2].split('.')[0].split('0')[1]
            if re.search(r'__', line_split[0]):
                PORT=line_split[2].split(':')[0]
                DEV=line_split[4].split(',')[0]
                key=str(BUS+"-"+PORT)
                class_value=line_split[7].split('=')[1]
                #print(DEVICES, class_value, key)
                #DEVICES[key]={'device_class':class_value}
                if key in DEVICES.keys(): 
                     if not(DEVICES[key]['device_class'] in CLASSES):
                         
                         DEVICES[key]={'device_class':class_value}                 
                     
                else:
                     
                     DEVICES[key]={'device_class':class_value}
                
                   
                DEVICES[key]['device_number']=DEV
                
        #print(DEVICES)
    else: print("There are no devices found")

#---------------------------------------------
#-------------READ DEVICE IDs---------------
#read devices from lsusb command
#and read device vendor and product ID
#-----------------------------------------------
def read_devices_id():
    process = subprocess.Popen(bash_command_lsusb.split(),
     stdout = subprocess.PIPE)
    output, error = process.communicate()
    str_lines=output.decode().split("\n")

    if str_lines.__sizeof__ != 0:
        for line in str_lines:
            if(line==""): break
           # print(line)
            line_split = line.split()
            BUS=line_split[1].split('00')[1]
            DEV=str(int(line_split[3].split(':')[0]))
            vendorID=line_split[5].split(':')[0]
            productID=line_split[5].split(':')[1]
            DEVICES_VID[DEV]=vendorID
            DEVICES_PID[DEV]=productID
            
       # print(DEVICES_VID)
       # print(DEVICES_PID)
    else: print("There are no devices found")

#--------------------------------------------------
#--------------TURN OFF by class-------------------
#Turn off all devices with class not defined in xml
#--------------------------------------------------
def turn_off_byclass():        
    for device in DEVICES:
        if not(DEVICES[device]['device_class'] in CLASSES):
        #if not(re.search(r'Human', DEVICES[device])):
            os.system(str(turn_off + devices_localization
                +device + turn_off_end)) 
                # show file
            os.system(str("cat \""+devices_localization+
            device+turn_off_end))
            # save turned off device
            TURNED_OFF_DEVICES.append(device)

#--------------------------------------------------
#--------------TURN OFF by vendor id---------------
#Turn off all devices with vendor_id
#  not defined in xml
#--------------------------------------------------
def turn_off_byvendor():        
    for device in DEVICES_VID:
        if not(DEVICES_VID[device] in VENDOR_ID):
            for dev in DEVICES:
                if DEVICE[dev]['device_number']==device:
                    correct_path=dev
                    print(correct_path)
                    os.system(str(turn_off + devices_localization
                        +correct_path + turn_off_end)) 
                        # show file
                    os.system(str("cat \""+devices_localization+
                    correct_path+turn_off_end))
                    # save turned off device
                    TURNED_OFF_DEVICES.append(correct_path)

#--------------------------------------------------
#--------------TURN OFF by vendor id---------------
#Turn off all devices with vendor_id
#  not defined in xml
#--------------------------------------------------
def turn_off_byproduct():        
    for device in DEVICES_PID:
        if not(DEVICES_PID[device] in PRODUCT_ID):
            for dev in DEVICES:
                
                if DEVICES[dev]['device_number']==device:
                    correct_path=dev
                    #print(correct_path)
                    os.system(str(turn_off + devices_localization
                        +correct_path + turn_off_end)) 
                        # show file
                    os.system(str("cat \""+devices_localization+
                    correct_path+turn_off_end))
                    # save turned off device
                    TURNED_OFF_DEVICES.append(correct_path)

#--------------------------------------------------
#--------------SAVE TURNED OFF DEVICES-------------
#save all devices turned off to xml file
#--------------------------------------------------
def save_off_devices():
    if TURNED_OFF_DEVICES.__sizeof__==0: return
    data = ET.Element('Device')
    for device in TURNED_OFF_DEVICES:
        item = ET.SubElement(data, 'path')
        item.text=str(device)
    newdata=ET.tostring(data)
    file = open(xml_patch_offdevices,"w")
    file.write(str(newdata.decode()))
            
#--------------------------------------------------
#--------------READ TURNED OFF DEVICES-------------
#read all devices turned off from xml file
#--------------------------------------------------
def read_off_devices():
        tree = ET.parse(xml_patch_offdevices)
        root = tree.getroot()
        for elem in root:
            #print(elem.text)
            TURNED_OFF_DEVICES.append(elem.text)

#--------------------------------------------------
#--------------TURN ON DEFIVES---------------------
#turn on all devices saved in TURNED_OFF_DEVICES
#--------------------------------------------------
def turn_on_devices():
    for device in TURNED_OFF_DEVICES:
        os.system(str(turn_on + devices_localization 
        +device + turn_on_end))
        os.system(str(turn_on_delay + devices_localization
        +device + turn_off_end)) 
        os.system(str("cat \"" + devices_localization 
        +device + turn_on_end))
        os.system(str("cat \"" + devices_localization
        +device + turn_off_end)) 


def arg_vendor():
    try:
        read_xml()
    except:
        print("there is some problem with xml file")
    read_devices_class()
    read_devices_id()
    turn_off_byvendor()
    print("Turned off all devices depending on vendor id")
    save_off_devices()


def arg_product():
    try:
        read_xml()
    except:
        print("there is some problem with xml file")
    read_devices_class()
    read_devices_id()
    turn_off_byproduct()
    print("Turned off all devices depending on product class")
    save_off_devices()

def arg_class():
    try:
        read_xml()
    except:
        print("there is some problem with xml file")
    read_devices_class()
    turn_off_byclass()
    print("Turned off all devices depending on class")
    save_off_devices()

def arg_on():
    try:
        read_off_devices()
                
    except:
        print("There are some problems with xml file, yet if other commands were passed, there can still be devices turned on")    
    turn_on_devices()
    print("turned on")
    print(TURNED_OFF_DEVICES) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='USB DEVICE POWER MENAGER')
    parser.add_argument("-vendor",action="store",help='turn off all devices except those with vendor-id defined in xml file, requires some any argument')
    parser.add_argument("-product",action="store",help='turn off all devices except those with product-id defined in xml file, requires some any argument')
    parser.add_argument("-clas", action="store",help='turn off all devices except those with class defined in xml file, requires some any argument')
    parser.add_argument("-on", help='turn on all devices that have beed off and saved in xml file, requires some any argument')
    parser.print_help()
    args = parser.parse_args()
    if args.vendor:
        arg_vendor()
    if args.product:
        arg_product()
    if args.clas:
        arg_class()
    if args.on:
        arg_on()
