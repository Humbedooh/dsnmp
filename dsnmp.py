#!/usr/bin/env python
# DSNMP: Dell SNMP monitoring system
# Licensed under the Apache License v/2.0
# Copyright 2014, Quokka IvS.
# Source: https://github.com/Humbedooh/dsnmp

#A few initial config options
http_url = "http://snmp.example.com" # Where does the HTML output live
http_dir = "/var/www" # Where on-disk to store the HTML output
json_data = "./settings.json" # Path to the global group settings
suffix = ".foo.org" # If set, append this to all hipchat host queries for fast access
ml_from = 'DSNMP Check <no-reply@example.com>' # Who to send emails from
ml_addr = 'no-reply@example.com' # Same as above, short format
vital_partitions = [ "/", "/x1.*" ] # Partitions that need to be below 75% space used, regex'ed
http_port = None # Set to hard-code a HTTP port to serve from instead of using an external HTTP server


# Basic imports
import os, sys, time, re, subprocess, urllib, json, hashlib, requests, time, random
from datetime import datetime

# SMTP Lib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Threading
from threading import Thread

# HTTP Lib + argsparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import argparse

# Parse args
parser = argparse.ArgumentParser(description='Command line options.')
parser.add_argument('--port', dest='port', type=int, nargs=1,
                   help='If defined, launch a HTTP server at this port to serve up static SNMP reports instead of compiling to files on disk')

args = parser.parse_args()
served_ourselves = False

# Sendmail function
def sendMail(to, subject, text, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = ml_from
    msg['To'] = to
    
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    s = smtplib.SMTP('localhost')
    s.sendmail(ml_addr, to, msg.as_string())
    s.quit()
    
# Add check_output if this is py 2.6 or below
if "check_output" not in dir( subprocess ): # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f


# SNMP OIDs
dell_perc_volumes = ".1.3.6.1.4.1.674.10893.1.20.140.1.1.2"
dell_perc_states = ".1.3.6.1.4.1.674.10893.1.20.140.1.1.4"
dell_perc_disk_status = ".1.3.6.1.4.1.674.10893.1.20.130.4.1.23" #Use combined status
dell_perc_disk_name = ".1.3.6.1.4.1.674.10893.1.20.130.4.1.25"
dell_disk_status = ".1.3.6.1.4.1.674.10893.1.20.130.4.1.4"

dell_psu_status = ".1.3.6.1.4.1.674.10892.1.200.10.1.9"
dell_product_name = "1.3.6.1.4.1.674.10892.1.300.10.1.9.1"
dell_service_tag = "1.3.6.1.4.1.674.10892.1.300.10.1.11.1"

dell_global_status = ".1.3.6.1.4.1.674.10893.1.20.110.13"
linux_load = ".1.3.6.1.4.1.2021.10.1.3"
linux_idle_pct = ".1.3.6.1.4.1.2021.11.11.0"
linux_cpu_cores = ".1.3.6.1.2.1.25.3.2.1.3"
linux_core_load = ".1.3.6.1.2.1.25.3.3.1.2"

dell_cpu_names = "1.3.6.1.4.1.674.10892.1.1100.30.1.23.1"
dell_cpu_cores = "1.3.6.1.4.1.674.10892.1.1100.30.1.17.1"

linux_free_mem = ".1.3.6.1.4.1.2021.4.11.0"
linux_buffered_mem = ".1.3.6.1.4.1.2021.4.14.0"
linux_total_mem = ".1.3.6.1.4.1.2021.4.5.0"
linux_used_mem = ".1.3.6.1.4.1.2021.4.6.0"

dell_memory_status = ".1.3.6.1.4.1.674.10892.1.200.10.1.27.1"
dell_memory_dimm_status = ".1.3.6.1.4.1.674.10892.1.200.10.1.28.1"

dell_overall_status = "1.3.6.1.4.1.674.10892.1.200.10.1.2.1"

linux_uptime = ".1.3.6.1.2.1.1.3.0"

linux_disk_mountpoint = ".1.3.6.1.4.1.2021.9.1.2"
linux_disk_pct = ".1.3.6.1.4.1.2021.9.1.9"

linux_os = ".1.3.6.1.2.1.1.1.0"

dell_disk_location = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.2"
dell_disk_vendor = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.3"
dell_disk_prodno = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.6"
dell_disk_serial = "iso.3.6.1.4.1.674.10893.1.20.130.4.1.7"

dell_extra_coolin = '1.3.6.1.4.1.674.10892.1.200.10.1.44.1'
dell_extra_battery = '1.3.6.1.4.1.674.10892.1.200.10.1.52.1'
dell_extra_temp = '1.3.6.1.4.1.674.10892.1.200.10.1.24.1'

dell_extra_temp_vals = "iso.3.6.1.4.1.674.10892.1.700.20.1.6.1"
dell_extra_temp_names = "iso.3.6.1.4.1.674.10892.1.700.20.1.8.1"


# Dell standard statuses
dell_status = {
     1: 'other',
     2: 'unknown',
     3: 'Okay',
     4: 'Non-critical',
     5: 'Critical'
}


# SMMP Walk + Get
def snmpwalk(server, community, oid):
    try:
        output = subprocess.check_output(["snmpwalk", "-Os", "-c", community, "-v", "2c", server, oid])
        print(output)
        assert(len(output) > 20)
    except:
        output = subprocess.check_output(["snmpwalk", "-Os", "-c", "secret", "-v", "2c", server, oid])
    arr = []
    for line in str(output).split("\n"):
        match = re.search(r"\w+\.(\d+) = (\w+): (.+)", line)
        if match:
            hid = int(match.group(1))
            typ = match.group(2)
            val = match.group(3)
            try:
                if typ == "INTEGER":
                    m = re.match(r"(\d+)", val)
                    val = m.group(1)
                val = val.replace('"', '')
                xval = val
                val = float(xval)
                val = int(xval)
            except:
                pass
            arr.append([hid, val])
    return arr
            
def snmpget(server, community, oid):
    try:
        output = ""
        try:
            output = subprocess.check_output(["snmpget", "-Os", "-c", community, "-v", "2c", server, oid])
        except:
            output = subprocess.check_output(["snmpget", "-Os", "-c", "secret", "-v", "2c", server, oid])
        match = re.search(r"\w+?\.(\d+) = [-\w]+: (.+)", output)
        out = ""
        if match:
            hid = int(match.group(1))
            val = match.group(2)
            try:
                val = val.replace('"', '')
                xval = val
                val = float(xval)
                val = int(xval)
            except:
                pass
            return xval
    except Exception as err:
        pass
    return ""
            

# Analytical functions
def linux_disk_space_used(arr, server, community):
    output = "%u partitions in place:<br/>" % (len(arr))
    overuse = False
    woveruse = False
    lv = None
    lu = 0
    for el in arr:
        used = snmpget(server, community, "%s.%u" % (linux_disk_pct, el[0]))
        if used > lu:
            lv = el[1]
            lu = used
        if int(used) >= 75:
            output += "%s: %s%% used (alert level = 75%%).<br/>" % (el[1], str(used))
            overuse = True
            for path in vital_partitions:
                if re.search(r"^%s$" % path, el[1]) or el[1] == path:
                    woveruse = True
    if not overuse:
        output += "No partitions using >= 75%% disk space (largest is %s with %s%%)" % (lv, lu)
    return output, woveruse
    
def get_dell_disk_info(hid, server, community):
    vendor = snmpget(server, community, "%s.%u" % (dell_disk_vendor, hid))
    location = snmpget(server, community, "%s.%u" % (dell_disk_location, hid))
    serial = snmpget(server, community, "%s.%u" % (dell_disk_serial, hid))
    prodno = snmpget(server, community, "%s.%u" % (dell_disk_prodno, hid))
    return "Disk %u: %s %s (serial=%s, location=%s)" % (hid, vendor, prodno, serial, location)
    
def get_perc_volume_info(hid, server, community):
    volume = snmpget(server, community, "%s.%u" % (dell_perc_volumes, hid))
    return volume

def get_perc_disk_info(hid, server, community):
    volume = "Unknown disk"
    try:
        volume = snmpget(server, community, "%s.%u" % (dell_perc_disk_name, hid))
    except:
        volume = snmpget(server, community, "%s.%u" % (dell_perc_volumes, hid))
    if volume == "" or not volume:
        volume = get_dell_disk_info(hid, server, community)
    return volume
    
def get_mem_free(arr, server, community):
    buffers = snmpget(server, community, linux_buffered_mem)
    m = re.search(r"(\d+)", buffers)
    buffers = m.group(1)
    kb = arr[0][1] + int(buffers)
    mb = kb/1024.0
    gb = mb/1024.0
    kbb = int(buffers)
    mbb = kbb/1024.0
    gbb = mbb/1024.0
    output = "%u KB free" % kb
    issue = False
    if mb < 100:
        issue = True
    if mb > 1:
        output = "%.2f MB free (%.2f MB buffered)" % (mb, mbb)
    if gb > 1:
        output = "%.2f GB free (%.2f GB buffered)" % (gb, gbb)
    return output, issue

def analyze_total_mem(arr, server, community):
    buffers = snmpget(server, community, linux_used_mem)
    
    m = re.search(r"(\d+)", buffers)
    buffers = m.group(1)
    kb = arr[0][1]
    mb = kb/1024.0
    gb = mb/1024.0
    egb = round((gb/8)+0.5)*8 # Estimate the no. of 8gb blocks
    kbb = int(buffers)
    mbb = kbb/1024.0
    gbb = mbb/1024.0
    output = "%u KB memory installed (%u KB used)" % (kb, kbb)
    issue = False
    what = ""
    try:
        mem_status = int(snmpget(server, community, dell_memory_status))
        print(mem_status)
        if mem_status != 3:
            issue = True
            dimm_status = snmpget(server, community, dell_memory_dimm_status)
            print(dimm_status)
            dimm = 0
            for d in re.finditer(r"(\d+)", dimm_status):
                dimm += 1
                ds = int(d.group(1))
                if ds != 3:
                    what += "DIMM #%u has status: %s. " % (dimm, dell_status[ds])
    except:
        pass
    if mb > 1:
        output = "%.2f MB memory installed (>%.2f MB used)" % (mb, mbb)
    if gb > 1:
        output = "%.2f GB memory installed (>%.2f GB used)" % (egb, gbb)
    if what != "":
        output += "<br/>\nStatus of memory blocks: %s" % what
    return output, issue

def analyze_dell_disks(arr, server, community):
    status = {
        0: 'Unknown',
        1: 'Ready (not assigned)',
        2: 'FAILED',
        3: 'Online and assigned',
        4: 'OFFLINE',
        6: 'DEGRADED',
        7: 'Resilvering',
        11: 'REMOVED',
        13: 'Online (Passthrough)',
        15: 'Resynching',
        24: 'Rebuilding',
        25: 'No media',
        26: 'Formatting',
        28: 'Diagnostics running',
        35: 'Initializing',
        38: 'Resynching Paused',
        52: 'Permanently Degraded',
        54: 'Degraded Redundancy'
    }
    ds = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    total = len(arr)
    for el in arr:
        ds[el[1]].append(el[0])
    output = "%u disks in total<br/>\n" % len(arr)
    issues = False
    for s in status:
        if len(ds[s]) > 0:
            if (s != 3 and s != 1 and s != 13):
                issues = True
            output += "<b>%s:</b> %s<br/>" % (status[s], ", ".join((get_dell_disk_info(x, server, community) if (s != 3 and s!= 1 and s != 13) else ("#" + str(x))) for x in ds[s]))
    return (output, issues)

def analyze_perc_volumes(arr, server, community):
    status = {
        0: 'Unknown',
        1: 'Ready',
        2: 'FAILED',
        3: 'Online and assigned',
        4: 'OFFLINE',
        6: 'DEGRADED',
        7: 'Resilvering',
        11: 'REMOVED',
        13: 'Online (Passthrough)',
        15: 'Resynching',
        24: 'Rebuilding',
        25: 'No media',
        26: 'Formatting',
        28: 'Diagnostics running',
        35: 'Initializing',
        38: 'Resynching Paused',
        52: 'Permanently Degraded',
        54: 'Degraded Redundancy'
    }
    ds = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    total = len(arr)
    for el in arr:
        ds[el[1]].append(el[0])
    output = "%u volumes in total<br/>\n" % len(arr)
    issues = False
    for s in status:
        if len(ds[s]) > 0:
            if (s != 3 and s != 1 and s != 13):
                issues = True
            output += "<b>%s:</b> %s<br/>" % (status[s], ", ".join(get_perc_volume_info(x, server, community) for x in ds[s]))
    return (output, issues)

def analyze_perc_disks(arr, server, community):
    status = {
        0: 'Unknown',
        1: 'Other(??)',
        2: 'Unknown (??)',
        3: 'Okay',
        4: 'Non-critical failure (degraded)',
        5: 'Critical failure',
        6: 'Non-recoverable'
    }
    ds = [[],[],[],[],[],[],[],[]]
    total = len(arr)
    for el in arr:
        ds[el[1]].append(el[0])
    output = "%u disks in total<br/>\n" % len(arr)
    issues = False
    for s in status:
        color = '000';
        if len(ds[s]) > 0:
            if (s != 3 and s != 1 and s != 13):
                issues = True
                color = '950';
            output += "<font color='#%s'><b>%s (%u):</b> %s</font><br/>" % (color, status[s], len(ds[s]), ", ".join(get_perc_disk_info(x, server, community) for x in ds[s]))
    return (output, issues)

def sendNotice(room, hipchat_tokenthing, msg, color = 'yellow'):
    headers = {'User-Agent': 'SNMP2HipChat/0.99'}
    payload = {
        'room_id': room,
        'auth_token': hipchat_tokenthing,
        'from': "SNMP2HipChat",
        'message_format': 'html',
        'notify': '0',
        'color': color,
        'message': msg
    }
    session = requests.Session()
    session.post('https://api.hipchat.com/v1/rooms/message',headers=headers,data=payload)

history = {}
    
def analyze_dell_status(arr, server, community):
    st = arr[0][1]
    if st != 3:
        return dell_status[st], True
    return dell_status[st], False

def analyze_dell_temp(arr, server, community):
    issue = False
    status = "Temperatures are within the acceptable range."
    st = arr[0][1]
    if st != 3:
        issue = True
        status = "Temperatures are outside the acceptable range!"
    vals = snmpwalk(server, community, dell_extra_temp_vals)
    names = snmpwalk(server, community, dell_extra_temp_names)
    y = 0
    for i in names:
        status += "<br>\n%s: %u &deg;C (%u &deg;F)" % (i[1], int(vals[y][1])/10, ((int(vals[y][1])/10.0) * (9.0/5.0)) + 32)
        y += 1
    return status, issue

def analyze_dell_overall_status(arr, server, community):
    st = arr[0][1]
    if st != 3:
        tries = {
            'power': '1.3.6.1.4.1.674.10892.1.200.10.1.42.1',
            'cooling': '1.3.6.1.4.1.674.10892.1.200.10.1.44.1',
            'memory': '1.3.6.1.4.1.674.10892.1.200.10.1.27.1',
            'cpu': '1.3.6.1.4.1.674.10892.1.200.10.1.50.1',
            'battery': '1.3.6.1.4.1.674.10892.1.200.10.1.52.1',
            'temperature': '1.3.6.1.4.1.674.10892.1.200.10.1.24.1'
        }
        bads = []
        for el in tries:
            try:
                val = int(snmpget(server, community, tries[el]))
                if val != 3:
                    bads.append("%s (%s)" % (el, dell_status[val]))
            except:
                pass
        if len(bads) == 0:
            bads.append("Non-standard error, please check your OpenManage service for details")
        return "Issues detected with: %s" % (", ".join(bads)), True
    return "All systems okay", False

def analyze_linux_load(arr, server, community):
    cores = get_max_cores(server, community)
    output = "<b>Load averages:</b> 5 min: %.2f, 10 min: %.2f, 15 min: %.2f" % (arr[0][1], arr[1][1], arr[2][1])
    if arr[2][1] > cores:
        output += "<br/>15 minute load is beyond what %u HT cores can handle!" % cores
        return output, True
    return output, False

def analyze_cpu_cores(arr, server, community):
    cpus = []
    output = ""
    oldarr = arr
    try:
        arr2 = snmpwalk(server, community, dell_cpu_names)
        if len(arr2) > len(arr):
            arr = arr2
    except:
        pass
    for el in arr:
        hw = el[1]
        if re.search(r"(CPU|Processor)", hw):
            cpus.append(hw)
            load = snmpget(server, community, "%s.%s" % (linux_core_load, el[0]))
            if not load:
                load = snmpget(server, community, "%s.%s" % (linux_core_load, oldarr[0][0]))
            output += "<b>Detected:</b> %s (%s%% load)<br/>\n" % (hw, load)
    cores = get_max_cores(server, community)
    output += "%u cores detected in total" % cores
    return output, False

def get_max_cores(server, community):
    cores = 0
    output = ""
    try:
        for el in snmpwalk(server, community, dell_cpu_cores):
            cores += int(el[1])
        if cores > 0:
            return cores
        else:
            raise Exception("Not a Dell machine!")
    except:
        for el in snmpwalk(server, community, linux_cpu_cores):
            hw = el[1]
            if re.search(r"CPU", hw, flags = re.IGNORECASE):
                cores += 2
        return cores
        
def analyze_prod(arr, server, community):
    prod = arr[0][1] if arr and len(arr) >= 1 else ""
    try:
        if prod and prod != "":
            serial = snmpget(server, community, dell_service_tag)
            return "%s (service tag: %s)" % (prod, serial), False
    except:
        pass
    os = "Ubuntu(?)"
    try:
        oss = snmpget(server, community, linux_os)
        m = re.search(r"(\w+)", oss)
        os = m.group(1)
    except:
        pass
    return (prod if (prod  and prod != "") else "Unknown (virtual?) machine, running %s") % os, False
    

# Define MIB actions
mibarray = {
    'load': [linux_load, analyze_linux_load],
    'cpuidle': linux_idle_pct,
    'memfree': [linux_free_mem, get_mem_free],
    'uptime': linux_uptime,
    'perc': [dell_perc_states, analyze_perc_volumes],
    'array': [dell_perc_disk_status, analyze_perc_disks],
    'disks': [dell_disk_status, analyze_dell_disks],
    'space': [linux_disk_mountpoint, linux_disk_space_used],
    'psu': [dell_psu_status, analyze_dell_status],
    'cores': [linux_cpu_cores, analyze_cpu_cores],
    'prod': [dell_product_name, analyze_prod],
    'memory': [linux_total_mem, analyze_total_mem],
    'status': [dell_overall_status, analyze_dell_overall_status],
    'temperature': [dell_extra_temp, analyze_dell_temp],
    'cooling': [dell_extra_coolin, analyze_dell_status],
    'battery': [dell_extra_battery, analyze_dell_status]
}


# Various states
alert_dials = {}
snmp_status = {}
snmp_daily_email = {}
snmp_hourly_hipchat = {}
snmp_hourly_pd = {}
snmp_reading = []
snmp_pages = {}


# Schedule
runall = {}
with open(json_data, "r") as f:
    js = f.read()
    f.close()
    runall = json.loads(js)

# populate states
for group in runall:
    if 'hipchat' in runall[group]['contact']:
        m = re.match(r"<(.+)", runall[group]['contact']['hipchat']['token'])
        if m:
            with open(m.group(1), "r") as f:
                runall[group]['contact']['hipchat']['token'] = f.read().strip()
                f.close()
    snmp_status[group] = []
    snmp_daily_email[group] = ""
    snmp_hourly_hipchat[group] = "",
    snmp_hourly_pd[group] = ""
    snmp_pages[group] = {}


# 15 minute check:
def run_all(what):
    gissues = 0
    goutput = ""
    gtoutput = ""
    snmp_reading.append(what)
    snmp_status[what] = []
    if 'hostsfile' in runall[what]:
        try:
            data = urllib.urlopen(runall[what]['hostsfile']).read()
            print(data)
            js = json.loads(data)
            if js:
                runall[what]['hosts'] = js
        except Exception as err:
            print(err)
            pass
    for server in sorted(runall[what]['hosts']):
        soutput = ""
        sissues = False
        whatissues = []
        scans = 0
        community = runall[what]['hosts'][server]['community']
        prod = None
        
        try:
            prod = snmpget(server, community, dell_product_name)
            if prod:
                soutput += "<h2>%s (%s):</h2>" % (server, prod)
            else:
                raise Exception("bah")
        except:
            soutput += "<h2>%s (virtual machine):</h2>" % server
        for el in runall[what]['hosts'][server]['checks']:
            dial = "%s-%s-%s" % (what, server, el)
            scans += 1
            try:
                output = "<h3>%s check:</h3>" % el
                if mibarray[el].__class__.__name__ == "list":
                    arr = snmpwalk(server, community, mibarray[el][0])
                    response, issues = mibarray[el][1](arr, server, community)
                    output += response
                    if issues:
                        sissues = True
                        gissues += 1
                        whatissues.append(el)
                        if (dial in alert_dials and alert_dials[dial] >= runall[what]['settings']['alertdial']) or runall[what]['settings']['alertdial'] <= 1:
                            if 'pd' in runall[what]['contact']:
                                sendMail(runall[what]['contact']['pd'], "SNMP detected issues with %s on %s" % (el, server), "SNMP detected issues with %s on %s" % (el, server), "SNMP detected issues with %s on %s" % (el, server))
                        alert_dials[dial] = 1 if not dial in alert_dials else alert_dials[dial] + 1
                    elif dial in alert_dials:
                        del alert_dials[dial]
                else:                            
                    arr = snmpwalk(server, community, mibarray[el])
                    out = []
                    for item in arr:
                        out.append("%s = %s" % (item[0], item[1]))
                    output += ", ".join(out)
                soutput += output
            except:
                if 'pd' in runall[what]['contact']:
                    whatissues.append('snmp communication')
                    sissues = True
                    gissues += 1
                    sendMail(runall[what]['contact']['pd'], "SNMP detected issues with %s on %s: Could not contact SNMPD" % (el, server), "SNMP detected issues with %s on %s: Could not contact SNMPD" % (el, server), "SNMP detected issues with %s on %s: Could not contact SNMPD" % (el, server))
        if not served_ourselves:
            with open("%s/%s/%s.html" % (http_dir, what, server), "w") as f:
                if sissues:
                    f.write("<h3><font color='#995500'>Issues detected!! (see details below)</font></h3>")
                    snmp_status[what].append(server)
                f.write(soutput)
                f.close()
        snmp_pages[what][server] = soutput
        
        goutput += "<a href='%s/%s/%s.html'>%s</a>: %s<br>" % (http_url, what, server, server, "<font color='#920'><b>&#10060; &nbsp;</b>Issues detected in: %s</font>" % ", ".join(whatissues) if sissues else "<font color='#008'><b>&#10003; &nbsp;</b></font>No issues detected (all %u scans passed at %s)") % (scans, time.strftime("%Y-%m-%d %H:%M"))
        gtoutput += "- %s: %s\n" % (server, "Issues detected in: %s" % ", ".join(whatissues) if sissues else "No issues detected")
        
    if not served_ourselves:
        with open("%s/%s/index.html" % (http_dir, what), "w") as f:
            f.write(goutput)
            f.close()
            
    snmp_pages[what]['index'] = goutput
    
    if runall[what]['contact']:
        if 'email' in runall[what]['contact']:
            dt = time.strftime("%y-%m-%d")
            print("Constructing email for %s" % dt)
            if dt != snmp_daily_email[what]:
                snmp_daily_email[what] = dt
                for email in runall[what]['contact']['email']:
                    subject = "Daily SNMP Check: %s" % ("ISSUES DETECTED (%u)" % gissues if gissues > 0 else "No issues detected")
                    text = "Hello, this is the daily SNMP check. Current SNMP status is:\n - No issues have been detected for today, hoorah!\n\nDetails:\n\n" + gtoutput
                    html = "Hello, this is the daily SNMP check. Current SNMP status is: <br/><b><i>No issues have been detected today, awesome!</i></b>.<br/><br/><b>Details:</b><br/>" + goutput
                    if gissues > 0:
                        text = "Hello, this is the daily SNMP check. Current SNMP status is:\n - ISSUES DETECTED\n\nDetails:\n\n" + gtoutput
                        html = "Hello, this is the daily SNMP check. Current SNMP status is: <br/><b><i>ISSUES DETECTED</i></b>.<br/><br/><b>Details:</b><br/>" + goutput
                    text += "\nFor more details, visit: %s/%s" % (http_url, what)
                    html += "<br/>\nFor more details, visit: <a href='%s/%s/'>%s/%s/</a>." % (http_url, what, http_url, what)
                    sendMail(email, subject, text, html)
        if 'hipchat' in runall[what]['contact']:
            h = datetime.now().hour / 4
            print("Constructing hipchat for %s" % h)
            if h != snmp_hourly_hipchat[what]:
                snmp_hourly_hipchat[what] = h
                headers = {'User-Agent': 'SNMP2HipChat/0.99'}
                payload = {
                    'room_id': runall[what]['contact']['hipchat']['room'],
                    'auth_token': runall[what]['contact']['hipchat']['token'],
                    'from': "SNMP2HipChat",
                    'message_format': 'html',
                    'notify': '0',
                    'color': 'red' if gissues > 0 else 'green',
                    'message': "SNMP Update: %s" % ("Issues detected with %s" % ", ".join(snmp_status[what])) if gissues > 0 else "Daily eight o'clock status: No issues detected!"
                }
                if datetime.now().hour == 20 or gissues > 0:
                    session = requests.Session()
                    session.post('https://api.hipchat.com/v1/rooms/message',headers=headers,data=payload)
    snmp_reading.remove(what)
    

# Spawn our own HTTP server?
class dsnmpHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type',"text/html")
        self.send_header('Connection',"close")
        self.end_headers()
        data = ""
        m = re.match(r"^/([^/]*)/?([^/]*?)(\.html)?$", self.path)
        group = None
        page = None
        if m:
            group = m.group(1)
            page = m.group(2)
        if group and group in runall:
            if not page or page == "":
                page = "index"
            if page and page in snmp_pages[group]:
                self.wfile.write(snmp_pages[group][page])
            else:
                self.wfile.write("404 Not found")
        else:
            self.wfile.write("404 Not found!")


def start_server(portno):
    global http_url
    server = HTTPServer(('', portno), dsnmpHTTPHandler)
    print ("Started HTTP server on port %u." % portno)
    if not re.search(r"[a-z]/", http_url):
        http_url += ":%u" % portno
    served_ourselves = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "Ctrl+C received, shutting down HTTP Server"
        server.socket.close()

# Start doing things

if len(args.port) == 1 or (http_port and http_port > 0):
    http_port = args.port[0] if len(args.port) > 0 else http_port
    thread = Thread(target = start_server, args = [http_port])
    thread.start()

# Our lil' timer for everything.
a = 0

while True:
    a += 1
    for group in runall:
        hipchat_token = runall[group]['contact']['hipchat']['token']
        room = runall[group]['contact']['hipchat']['room']
        try:
            js = json.loads(urllib.urlopen("https://api.hipchat.com/v1/rooms/history?auth_token=%s&room_id=%s&date=recent" % (hipchat_token, room)).read())
            if a == 1:
                for line in js['messages']:
                    hash256 = line['date'] + hashlib.sha256(line['message'].encode("ascii","ignore")).hexdigest()
                    history[hash256] = True
            for line in js['messages']:
                hash256 = line['date'] + hashlib.sha256(line['message'].encode("ascii","ignore")).hexdigest()
                if not hash256 in history:
                    history[hash256] = True
                    match = re.search(r"#snmp (\S+) (\S+)(.*)", line['message'])
                    if match:
                        if len(snmp_reading) > 0:
                            sendNotice(room, hipchat_token, "Sorry, I'm currently running the 15 minute check. Due to the non-thread-safe nature of the UDP checks, I cannot return any SNMP data currently. Please retry in a minute.", 'yellow')
                        else:
                            host = match.group(1)
                            typ = match.group(2)
                            com = match.group(3)
                            if len(com) > 1:
                                community = com.strip()
                            else:
                                community = "public"
                                if "%s%s" % (host, suffix) in runall[group]['hosts']:
                                    community = runall[group]['hosts']["%s%s" % (host, suffix)]['community']
                            if typ in mibarray:
                                arr = None
                                try:
                                    output = "<b>SNMP Response:</b><br/>\n"
                                    gi = False
                                    if mibarray[typ].__class__.__name__ == "list":
                                        arr = snmpwalk("%s%s" % (host, suffix), community, mibarray[typ][0])
                                        response, issues = mibarray[typ][1](arr, "%s%s" % (host, suffix), community)
                                        output += response
                                        if issues:
                                            gi = True
                                            output = "<i><font color='#994400'>Issues detected! (see details below):</font></i><br/>" + output
                                    else:                            
                                        arr = snmpwalk("%s%s" % (host, suffix), community, mibarray[typ])
                                        out = []
                                        for item in arr:
                                            out.append("%s = %s" % (item[0], item[1]))
                                        output += ", ".join(out)
                                        
                                    sendNotice(room, hipchat_token, output, 'red' if gi else 'green')
                                except Exception as err:
                                    print(err)
                                    sendNotice(room, hipchat_token, 'Got no response from SNMP server', 'red')
                            else:
                                sendNotice(room, hipchat_token, "Could not fetch SNMP data :(", 'red')
                    if line['message'] == "#snmpstatus":
                        if len(snmp_status[group]) > 0:
                            sendNotice(room, hipchat_token, "SNMP has detected issues with: %s. Click <a href='%s/%s'>Here</a> for details."  % (", ".join(snmp_status[group]), http_url, group), 'red')
                        else:
                            sendNotice(room, hipchat_token, "SNMP has not detected any recent issues.", 'green')
                    if line['message'] == "#snmpconf":
                        output = ""
                        for server in runall[group]['hosts']:
                            output += "<br/>\n%s: %s" % (server, ", ".join(runall[group]['hosts'][server]['checks']))
                        sendNotice(room, hipchat_token, "SNMP is currently running the following checks: %s" % output, 'green')
        except:
            print("Could not get hipchat data for %s (using https://api.hipchat.com/v1/rooms/history?auth_token=%s&room_id=%s&date=recent" % (group, hipchat_token, room))
    time.sleep(6)
    if (a % 150) == 5:
        for group in runall:
            thread = Thread(target = run_all, args = [group])
            thread.start()
    
