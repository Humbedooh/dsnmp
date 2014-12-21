import snmptools, oids, re, os, time, json, sys
from datetime import datetime
#from __main__ import queue
import pywbem
import logging
import pprint

NS = 'root/cimv2'

CIMStatus = {
            0  : False,    # Unknown
            5  : False,    # OK
            10 : True,  # Degraded
            15 : True,  # Minor
            20 : True,  # Major
            25 : True,  # Critical
            30 : True,  # Non-recoverable Error
}

def init(server, mib, config):
    try:
        wbemclient = connect(server, config['wbem']['user'], config['wbem']['password'])
        if wbemclient:
            output = wbemclient.EnumerateInstances(mib)  
            return output
    except:
        pass
    return None

def connect(server, user, password):
    server = "https://%s" % server
    try:
        wbemclient = pywbem.WBEMConnection(server, (user,password), NS)
        return wbemclient
    except Exception as err:
        logging.warn("Could not connect to WBEM: %s" % err)
        return None
    

def analyze_fans(arr):
    issue = False
    output = "Temperature status:<br/>\n"
    for instance in arr:
        if u'Caption' in instance and re.search(r"Temp(erature)?$", instance[u'Caption']):
            output += "%s: %u degrees Celcius (%s)<br/>\n" % (instance[u'Caption'], int(instance[u'CurrentReading'])/100, instance[u'CurrentState'])
            if instance[u'CurrentState'] != "Normal":
                issue = True
    return output, issue

def analyze_prod(arr):
    issue = False
    output = "Product information:<br/>\n"
    prod = arr[0]
    output += "Machine type: %s<br/>Service Tag: %s<br>Manifacturer: %s" % (prod[u'Model'], prod[u'SerialNumber'], prod[u'Manufacturer'])
    return output, issue

def analyze_cores(arr):
    issue = False
    output = "Processor stats:<br/>\n"
    cores = 0
    for instance in arr:
        output += "- %s (%s cores)<br/>" % (instance[u'ModelName'], instance[u'NumberOfEnabledCores'])
    return output, issue

def analyze_psu(arr):
    issue = False
    output = "Power stats:<br/>\n"
    cores = 0
    for instance in arr:
        if CIMStatus[instance[u'HealthState']]:
            issue = True
        output += "- %s: %s<br/>" % (instance[u'Description'], "Operational" if not CIMStatus[instance[u'HealthState']] else "Not operational!")
    return output, issue


def analyze_raid(arr):
    issue = False
    output = "RAID contoller stats:<br/>\n"
    cores = 0
    for instance in arr:
        if CIMStatus[instance[u'HealthState']]:
            issue = True
        output += "- %s: %s<br/>" % (instance[u'Caption'], "Operational" if not CIMStatus[instance[u'HealthState']] else "Not operational!")
    return output, issue


def analyze_memory(arr):
    issue = False
    mem = 0
    output = "Memory status:<br/>\n"
    
    for instance in arr:
        if not u'Level' in instance and u'NumberOfBlocks' in instance:
            mem += int(instance[u'NumberOfBlocks']) * int(instance[u'BlockSize'])
            if u'ErrorInfo' in instance and instance[u'ErrorInfo']:
                issue = True
                output += "Error(s) detected: %s<br/>\n" % instance[u'ErrorInfo']
    mem = mem / (1024*1024*1024)
    output += "%u GB memory installed, no memory errors detected" % mem
    return output, issue



def analyze_array(arr):
    issue = False
    output = "Disk array status:<br/>\n"
    
    for instance in arr:
        space = int(instance[u'NumberOfBlocks']) * int(instance[u'BlockSize']) / (1024*1024*1024)
        output += "- %s (%s GB allocated)<br/>\n" % (instance[u'Caption'], space)
        if u'ErrorDescription' in instance and instance[u'ErrorDescription']:
            issue = True
            output += "Error(s) detected: %s<br/>\n" % instance[u'ErrorDescription']
    return output, issue

mibarray = {
    'temperature': ["CIM_NumericSensor", analyze_fans],
    'cores': ["CIM_Processor", analyze_cores],
    'memory': ["CIM_Memory", analyze_memory],
    'prod': ["CIM_Chassis", analyze_prod],
    'psu': ["OMC_PowerSupply", analyze_psu],
    'array': ["VMware_StorageVolume", analyze_array],
    'raid': ["VMware_Controller", analyze_raid]
}

if __name__ == "__main__":
    wbem = init(sys.argv[1], sys.argv[2], { "wbem": {
                "user": sys.argv[3],
                "password": sys.argv[4]
            }})
    
    o = 0
    for el in wbem:
        print(o)
        o += 1
        for key, val in el.items():
            print("%s = %s" % (key, val))
            