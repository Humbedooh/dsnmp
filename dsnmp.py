#!/usr/bin/env python
# DSNMP: Dell SNMP monitoring system
# Licensed under the Apache License v/2.0
# Joint copyright 2014, Quokka IvS.
# Joint copyright 2014, The Apache Software Foundation
# Source: https://github.com/Humbedooh/dsnmp

# Basic imports
import os, sys, time, re, subprocess, urllib, json, hashlib, requests, time, random
from datetime import datetime

# Daemon
from lib import daemon
# Queue
queue = daemon.Queue()


## Globals
snmp_pages = {}
snmp_jobs = {}
alert_dials = {}
snmp_status = {}
snmp_daily_email = {}
snmp_hourly_hipchat = {}
snmp_hourly_pd = {}

# Local imports
from lib import templates, oids, sendmail, hipchat, snmptools, snmpanalyzers, globalanalyzer, http


# Set up path and logging
import logging
sys.path.append(os.path.basename(sys.argv[0]))
reload(sys);
sys.setdefaultencoding("utf8")

logging.basicConfig(filename='dsnmp.log', format='[%(asctime)s]: %(message)s', level=logging.INFO)
path = os.path.dirname(os.path.abspath(sys.argv[0]))
if len(path) == 0:
    path = "."
    

# Threading
from threading import Thread

# argsparse
import argparse




# Global settings
just_started = True
dry_run = False
settings = {}

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


            


def updateSettings():
    for group in settings['groups']:
        if 'hostsfile' in settings['groups'][group]:
            try:
                data = urllib.urlopen(settings['groups'][group]['hostsfile']).read()
                print(data)
                js = json.loads(data)
                if js:
                    settings['groups'][group]['hosts'] = js
            except Exception as err:
                logging.warn("Could not load hosts file for %s: %s" % (group, err))
                pass
        
        
with open("%s/settings.json" % path, "r") as f:
    js = f.read()
    f.close()
    settings = json.loads(js)

# populate states
for group in settings['groups']:
    if 'hipchat' in settings['groups'][group]['contact']:
        m = re.match(r"<(.+)", settings['groups'][group]['contact']['hipchat']['token'])
        if m:
            with open(m.group(1), "r") as f:
                settings['groups'][group]['contact']['hipchat']['token'] = f.read().strip()
                f.close()
    snmp_status[group] = []
    snmp_daily_email[group] = ""
    snmp_hourly_hipchat[group] = "",
    snmp_hourly_pd[group] = ""
    snmp_pages[group] = {}



    
# Start doing things
def main(args):
    print("Starting dSNMP")
    if (args.port and len(args.port)) == 1 or (settings['global_settings']['http_port'] and settings['global_settings']['http_port'] > 0):
        http_port = args.port[0] if (args.port and len(args.port)) > 0 else settings['global_settings']['http_port']
        thread = Thread(target = http.start_server, args = [http_port])
        thread.start()
        print ("Started HTTP server on port %u." % http_port)
        if not re.search(r"[a-z]/", settings['global_settings']['http_domain']):
            settings['global_settings']['http_domain'] += ":%u" % http_port
        served_ourselves = True
        
    if args.dry:
        dry_run = True
        print("Dry run enabled, won't alert of issues")

    # Our lil' timer for everything.
    a = 0
    
    # Run an initial hipchat scan to not trigger on these messages.
    for group in settings['groups']:
        hipchat.scanHipChat(group, settings['groups'][group], True)
    
    just_started = True
    # Continuously run hipchat scans every 6 seconds
    while True:
        a += 1
        for group in settings['groups']:
            ret = hipchat.scanHipChat(group, settings['groups'][group], False)
            if ret and len(ret) > 0:
                print("Got HipChat directive, handling..")
                hipchat_token = settings['groups'][group]['contact']['hipchat']['token']
                room = settings['groups'][group]['contact']['hipchat']['room']
                for el in ret:
                    if el[0] == "status":
                        if len(snmp_status[group]) > 0:
                            hipchat.sendNotice(room, hipchat_token, "SNMP issues were detected with: %s " % ", ".join(snmp_status[group]), 'red')
                        else:
                            hipchat.sendNotice(room, hipchat_token, "No issues were detected on the last run.", 'green')
                    elif el[0] == "config":
                        hipchat.sendNotice(room, hipchat_token, "bla bla bla")
                    elif el[0] == "help":
                        checks = []
                        for check in snmpanalyzers.mibarray:
                            checks.append(check)                        
                        hipchat.sendNotice(room, hipchat_token, "Usage: #snmp $host $check [$community]<br/>\nAvailable checks: %s" % ", ".join(checks))
                    elif el[0] == "check" and len(el) > 2:
                        server = el[1]
                        if not re.match(r"([^.]+\.[^.]+\.[^.]+)", el[1]):
                            server = "%s%s" % (el[1], settings['global_settings']['helper_suffix'])
                        checktype = el[2]
                        community = "public"
                        if len(el) > 3 and el[3]:
                            community = el[3]
                        elif server in settings['groups'][group]['hosts'] and 'community' in settings['groups'][group]['hosts'][server]:
                            community = settings['groups'][group]['hosts'][server]['community']
                        
                        if checktype in snmpanalyzers.mibarray and snmpanalyzers.mibarray[checktype].__class__.__name__ == "list":
                            arr = queue.queue(snmptools.walk, server, community, snmpanalyzers.mibarray[checktype][0])
                            if len(snmpanalyzers.mibarray[checktype]) > 2:
                                hipchat.sendNotice(room, hipchat_token, "Doing long-lived query, please wait...", 'gray')
                            print(arr)
                            try:
                                response, issues = snmpanalyzers.mibarray[checktype][1](arr, server, community, settings['groups'][group])
                                hipchat.sendNotice(room, hipchat_token, response, 'red' if issues else 'green')
                            except:
                                hipchat.sendNotice(room, hipchat_token, "No SNMP output returned from server. Please make sure that the address is correct, SNMPd is running and that no firewall or security setups are blocking data transmission.", 'red')
                        elif checktype in snmpanalyzers.mibarray:
                            pass
                        else:
                            hipchat.sendNotice(room, hipchat_token, "Sorry, I don't know that check type.", 'yellow')
        if (a % 200) == 1:
            updateSettings()
            for group in settings['groups']:
                logging.info("Starting thread to analyze '%s' group" % group)
                thread = Thread(target = globalanalyzer.start_analysis, args = [group, settings['groups'][group], just_started, settings])
                thread.start()
        if a > 100:
            just_started = False
        time.sleep(5)
        
        
## Daemon class
class MyDaemon(daemon.Daemonize):
    def run(self, args):
        main(args)

# Parse args
parser = argparse.ArgumentParser(description='Command line options.')
parser.add_argument('--port', dest='port', type=int, nargs=1,
                   help='If defined, launch a HTTP server at this port to serve up static SNMP reports instead of compiling to files on disk')
parser.add_argument('--dry-run', dest='dry', action='store_true',
                   help='If set, dSNMP will not warn via email, hipchat or pd. used for testing checks.')
parser.add_argument('--daemonize', dest='daemon', action='store_true',
                   help='Run dSNMP as a daemon')

args = parser.parse_args()

# Get started!
if args.daemon:
    print("Daemonizing...")
    snmpdaemon = MyDaemon('/tmp/dsnmp.pid')
    snmpdaemon.start(args)
else:
    main(args)
    