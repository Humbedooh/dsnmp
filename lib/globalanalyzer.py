import snmptools, snmpanalyzers, hipchat, templates, oids, daemon, sendmail
from __main__ import queue, snmp_pages, snmp_jobs, snmp_daily_email, snmp_hourly_hipchat, snmp_status, alert_dials
import logging, time, re
from datetime import datetime



# Big ol' SNMP routine check
def start_analysis(group, config, dry_run, settings):
    logging.info("Running checks for %s" % group)
    now = time.time()
    gissues = 0
    goutput = ""
    gtoutput = ""
    
    served_ourselves = True if settings['global_settings']['http_server'] == "internal" else False
    http_dir = settings['global_settings']['html_dir'] if 'html_dir' in settings['global_settings'] else "/var/www"
    http_url = "http://%s" % settings['global_settings']['http_domain']
    
    snmp_status[group] = []
    
    if not 'index' in snmp_pages[group]:
        snmp_pages[group]['index'] = templates.html_temp_template
    
    # Count jobs to be done
    no_jobs = 0
    jobs_done = 0
    for server in sorted(config['hosts']):
        no_jobs += len(config['hosts'][server]['checks'])
        
    # Run through all jobs
    for server in sorted(config['hosts']):
        soutput = ""
        sissues = False
        whatissues = []
        scans = 0
        
        prod = None
        s_header = ""
        
        # SNMP Checks??
        if not 'type' in config['hosts'][server] or config['hosts'][server]['type'] == "snmp":
                
            community = config['hosts'][server]['community']
            try:
                prod = snmpget(server, community, dell_product_name)
                if prod:
                    s_header = "<h2>%s (%s):</h2>" % (server, prod)
                else:
                    raise Exception("bah")
            except:
                s_header = "<h2>%s (virtual machine):</h2>" % server
                
            s_header += "<p><i>Check run at %s.</i></p>" % time.strftime("%Y-%m-%d %H:%M")
            
            #Run through all checks on the host
            for el in config['hosts'][server]['checks']:
                jobs_done += 1
                snmp_jobs[group] = (jobs_done / (no_jobs * 1.0)) * 100
                dial = "%s-%s-%s" % (group, server, el)
                scans += 1
                try:
                    output = "<tr><td><b>%s check:</b></td>" % el
                    if snmpanalyzers.mibarray[el].__class__.__name__ == "list":
                        arr = queue.queue(snmptools.walk, server, community, snmpanalyzers.mibarray[el][0])
                        response, issues = snmpanalyzers.mibarray[el][1](arr, server, community, config)
                        output += "<td %s><pre>%s</pre></td></tr>" % (("style='background:#FDD; color: #000;'" if issues else ""),response)
                        if issues:
                            sissues = True
                            gissues += 1
                            whatissues.append(el)
                            if (dial in alert_dials and alert_dials[dial] >= config['settings']['alertdial']) or config['settings']['alertdial'] <= 1:
                                if 'pd' in config['contact'] and not dry_run:
                                    sendmail.sendMail(config['contact']['pd'], "SNMP detected issues with %s on %s" % (el, server), "SNMP detected issues with %s on %s" % (el, server), "SNMP detected issues with %s on %s" % (el, server))
                            alert_dials[dial] = 1 if not dial in alert_dials else alert_dials[dial] + 1
                        elif dial in alert_dials:
                            del alert_dials[dial]
                    else:                            
                        arr = queue.queue(snmptools.walk, server, community, snmpanalyzers.mibarray[el])
                        out = []
                        for item in arr:
                            out.append("%s = %s" % (item[0], item[1]))
                        output += "<td><pre>%s</pre></td></tr>" % ", ".join(out)
                    soutput += output
                except Exception as err:
                    soutput += "<td style='background:#FDD; color: #000;'><pre>Could not contact SNMP Server: %s</pre></td></tr>" % err
                    if 'pd' in config['contact'] and not dry_run:
                        if 'snmp communication' in whatissues:
                            whatissues.remove('snmp communication')
                        whatissues.append('snmp communication')
                        sissues = True
                        gissues += 1
                        sendmail.sendMail(config['contact']['pd'], "SNMP detected issues with %s: Could not contact SNMPD" % (server), "SNMP detected issues with %s: Could not contact SNMPD" % (server), "SNMP detected issues with %s: Could not contact SNMPD" % (server))
                        break # Skip the other checks if we can't contact snmpd
                    
        if not served_ourselves:
            with open("%s/%s/%s.html" % (http_dir, group, server), "w") as f:
                if sissues:
                    f.write("<h3><font color='#995500'>Issues detected!! (see details below)</font></h3>")
                    snmp_status[group].append(server)
                f.write(templates.html_report_template % (server, s_header, soutput))
                f.close()
        snmp_pages[group][server] = templates.html_report_template % (server, s_header, soutput)
        
        goutput += "<tr><td><a href='%s/%s/%s.html'>%s</a></td><td>%s</td><td>%s</td></tr>" % (
            http_url,
            group,
            server,
            server,
            (
                    ("<font color='#F62'><b>&#10060; &nbsp;</b>Issues detected in: %s</font>" % ", ".join(whatissues)) if sissues else
                    ("<font color='#4E4'><b>&#10003; &nbsp;</b></font>No issues detected (all %u scans passed)" % scans)
            ),
            time.strftime("%Y-%m-%d %H:%M")
        )
        gtoutput += "- %s: %s\n" % (server, "Issues detected in: %s" % ", ".join(whatissues) if sissues else "No issues detected")
        
        
    # Compile the front page
    if not served_ourselves:
        with open("%s/%s/index.html" % (http_dir, group), "w") as f:
            f.write(templates.html_output_template % ("<h2>Overall status for %s:</h2>" % group, goutput))
            f.close()
            
    snmp_pages[group]['index'] = templates.html_output_template % ("<h2>Overall status for %s:</h2>" % group, goutput)
    
    
    # Sum up and deploy status messages
    dt = time.strftime("%y-%m-%d")
    if 'contact' in config:
        if 'email' in config['contact'] and not dry_run:
            print("Constructing email for %s" % dt)
            if dt != snmp_daily_email[group]:
                snmp_daily_email[group] = dt
                for email in config['contact']['email']:
                    subject = "Daily SNMP Check: %s" % ("ISSUES DETECTED (%u)" % gissues if gissues > 0 else "No issues detected")
                    text = "Hello, this is the daily SNMP check. Current SNMP status is:\n - No issues have been detected for today, hoorah!\n\nDetails:\n\n" + gtoutput
                    html = templates.html_output_template % ("Hello, this is the daily SNMP check. Current SNMP status is: <br/><b><i>No issues have been detected today, awesome!</i></b>.<br/><br/><b>Details:</b><br/>", goutput)
                    if gissues > 0:
                        text = "Hello, this is the daily SNMP check. Current SNMP status is:\n - ISSUES DETECTED\n\nDetails:\n\n" + gtoutput
                        html = templates.html_output_template % ("Hello, this is the daily SNMP check. Current SNMP status is: <br/><b><i>ISSUES DETECTED!</i></b>.<br/><br/><b>Details:</b><br/>", goutput)
                    text += "\nFor more details, visit: %s/%s.\nPowered by dSNMP - https://github.com/Humbedooh/dsnmp" % (http_url, group)
                    sendmail.sendMail(email, subject, text, html)
    
        if 'hipchat' in config['contact']:
            h = datetime.now().hour / 4
            print("Constructing hipchat for %s" % h)
            if h != snmp_hourly_hipchat[group]:
                snmp_hourly_hipchat[group] = h
                message = "SNMP Update: %s. See the <a href='%s/%s/'>status page</a> for more details." % ("Issues detected with %s" % ", ".join(snmp_status[group]), http_url, group) if gissues > 0 else "Daily eight o'clock status: No issues detected"
                color = 'red' if gissues else 'green'
                if datetime.now().hour == 20 or gissues > 0:
                    hipchat.sendNotice(config['contact']['hipchat']['room'], config['contact']['hipchat']['token'], message, color)
    
    snmp_daily_email[group] = dt

    # All done!
    print("Done deploying.")
    logging.info("Done with %s in %u seconds" % (group, time.time() - now))
    