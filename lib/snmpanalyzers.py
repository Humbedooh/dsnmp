import snmptools, oids, re, os, time
from datetime import datetime
from __main__ import queue


# Analytical functions
def linux_disk_space_used(arr, server, community, config):
    output = "%u partitions in place:<br/>" % (len(arr))
    overuse = False
    woveruse = False
    lv = None
    lu = 0
    vital_partitions = ['/']
    if 'vital_partitions' in config:
        vital_partitions = config['vital_partitions']
    for el in arr:
        used = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.unix_disk_pct, el[0]))
        if int(used) > lu:
            lv = el[1]
            lu = int(used)
        if int(used) >= 75:
            output += "%s: %s%% used (alert level = 75%%).<br/>" % (el[1], str(used))
            overuse = True
            for path in vital_partitions:
                if re.search(r"^%s$" % path, el[1]) or el[1] == path:
                    woveruse = True
        else:
            output += "%s: %s%% used.<br/>" % (el[1], str(used))
    if not overuse:
        output += "No partitions using >= 75%% disk space (largest is %s with %s%%)" % (lv, lu)
    return output, woveruse
    
def get_dell_disk_info(hid, server, community, config):
    vendor = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_disk_vendor, hid))
    location = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_disk_location, hid))
    serial = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_disk_serial, hid))
    prodno = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_disk_prodno, hid))
    return "Disk %u: %s %s (serial=%s, location=%s)" % (hid, vendor, prodno, serial, location)
    
def get_perc_volume_info(hid, server, community, config):
    volume = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_raid_volumes, hid))
    return volume

def get_perc_disk_info(hid, server, community, config):
    volume = "Unknown disk"
    try:
        volume = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_raid_disk_name, hid))
    except:
        volume = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_raid_volumes, hid))
    if volume == "" or not volume:
        volume = get_dell_disk_info(hid, server, community, config)
    return volume
    
def get_mem_free(arr, server, community, config):
    buffers = queue.queue(snmptools.get, server, community, oids.unix_memory_buffered)
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

def analyze_total_mem(arr, server, community, config):
    buffers = queue.queue(snmptools.get, server, community, oids.unix_memory_used)
    
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
        mem_status = int(queue.queue(snmptools.get,server, community, oids.dell_memory_status))
        print(mem_status)
        if mem_status != 3:
            issue = True
            dimm_status = queue.queue(snmptools.get,server, community, oids.dell_memory_dimm_status)
            print(dimm_status)
            dimm = 0
            for d in re.finditer(r"(\d+)", dimm_status):
                dimm += 1
                ds = int(d.group(1))
                if ds != 3:
                    what += "DIMM #%u has status: %s. " % (dimm, oids.dell_status_standard[ds])
    except:
        pass
    if mb > 1:
        output = "%.2f MB memory installed (>%.2f MB used)" % (mb, mbb)
    if gb > 1:
        output = "%.2f GB memory installed (>%.2f GB used)" % (egb, gbb)
    if what != "":
        output += "<br/>\nStatus of memory blocks: %s" % what
    return output, issue

def analyze_dell_disks(arr, server, community, config):
    ds = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    total = len(arr)
    for el in arr:
        ds[el[1]].append(el[0])
    output = "%u disks in total<br/>\n" % len(arr)
    issues = False
    for s in oids.dell_status_disk:
        if len(ds[s]) > 0:
            if (s != 3 and s != 1 and s != 13):
                issues = True
            output += "<b>%s:</b> %s<br/>" % (oids.dell_status_disk[s], ", ".join((get_dell_disk_info(x, server, community, config) if (s != 3 and s!= 1 and s != 13) else ("#" + str(x))) for x in ds[s]))
    return (output, issues)

def analyze_disk_info(arr, server, community, config):
    output = "%u disks in total<br/>\n" % len(arr)
    for el in arr:
        output += "<b>%s:</b> %s<br/>" % (oids.dell_status_disk[int(el[1])], get_dell_disk_info(el[0], server, community, config))
    return (output, False)

def analyze_perc_volumes(arr, server, community, config):

    ds = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    total = len(arr)
    for el in arr:
        ds[el[1]].append(el[0])
    output = "%u volumes in total<br/>\n" % len(arr)
    issues = False
    for s in oids.dell_status_disk:
        if len(ds[s]) > 0:
            if (s != 3 and s != 1 and s != 13):
                issues = True
            output += "<b>%s:</b> %s<br/>" % (oids.dell_status_disk[s], ", ".join(get_perc_volume_info(x, server, community, config) for x in ds[s]))
    return (output, issues)

def analyze_perc_disks(arr, server, community, config):
    ds = [[],[],[],[],[],[],[],[]]
    total = len(arr)
    for el in arr:
        ds[el[1]].append(el[0])
    output = "%u disks in total<br/>\n" % len(arr)
    issues = False
    for s in oids.dell_status_standard:
        color = '000';
        if len(ds[s]) > 0:
            if (s != 3 and s != 1 and s != 13):
                issues = True
                color = '950';
            output += "<font color='#%s'><b>%s (%u):</b> %s</font><br/>" % (color, oids.dell_status_standard[s], len(ds[s]), ", ".join(get_perc_disk_info(x, server, community, config) for x in ds[s]))
    return (output, issues)


history = {}
    
def analyze_dell_status(arr, server, community, config):
    st = arr[0][1]
    if st != 3:
        return oids.dell_status_standard[st], True
    return oids.dell_status_standard[st], False

def analyze_dell_temp(arr, server, community, config):
    issue = False
    status = "Temperatures are within the acceptable range."
    st = arr[0][1]
    if st != 3:
        issue = True
        status = "Temperatures are outside the acceptable range!"
    vals = queue.queue(snmptools.walk,server, community, oids.dell_machine_temperature_values)
    names = queue.queue(snmptools.walk,server, community, oids.dell_machine_temperature_sensornames)
    y = 0
    for i in names:
        status += "<br>\n%s: %u &deg;C (%u &deg;F)" % (i[1], int(vals[y][1])/10, ((int(vals[y][1])/10.0) * (9.0/5.0)) + 32)
        y += 1
    return status, issue

def analyze_dell_overall_status(arr, server, community, config):
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
                val = int(queue.queue(snmptools.get, server, community, tries[el]))
                if val != 3:
                    bads.append("%s (%s)" % (el, oids.dell_status_standard[val]))
            except:
                pass
        if len(bads) == 0:
            return "Unknown global status error: Possible firmware version issue. Please check your OpenManage service for details", False
        return "Issues detected with: %s" % (", ".join(bads)), True
    return "All systems okay", False

def analyze_linux_load(arr, server, community, config):
    cores = get_max_cores(server, community, config)
    output = "<b>Load averages:</b> 5 min: %.2f, 10 min: %.2f, 15 min: %.2f" % (arr[0][1], arr[1][1], arr[2][1])
    if arr[2][1] > cores:
        output += "<br/>15 minute load is beyond what %u HT cores can handle!" % cores
        return output, True
    return output, False

def analyze_cpu_cores(arr, server, community, config):
    cpus = []
    output = ""
    oldarr = arr
    try:
        arr2 = queue.queue(snmptools.walk, server, community, oids.dell_cpu_names)
        if len(arr2) > len(arr):
            arr = arr2
    except:
        pass
    for el in arr:
        hw = el[1]
        if re.search(r"(CPU|Processor)", hw):
            cpus.append(hw)
            load = queue.queue(snmptools.get, server, community, "%s.%s" % (oids.unix_cpu_core_load, el[0]))
            if not load:
                load = queue.queue(snmptools.get, server, community, "%s.%s" % (oids.unix_cpu_core_load, oldarr[0][0]))
            output += "<b>Detected:</b> %s (%s%% load)<br/>\n" % (hw, load)
    cores = get_max_cores(server, community, config)
    output += "%u cores detected in total" % cores
    return output, False

def get_max_cores(server, community, config):
    cores = 2
    output = ""
    try:
        for el in queue.queue(snmptools.walk, server, community, oids.dell_cpu_cores):
            cores += int(el[1])
        if cores > 0:
            return cores
        else:
            try:
                arr = queue.queue(snmptools.walk, server, community, oids.dell_cpu_names)
                for el in arr:
                    hw = el[1]
                    if re.search(r"(CPU|Processor|GenuineIntel)", hw):
                        cores += 1
                if cores > 0:
                    return cores
            except:
                pass
        if cores == 0:
            raise Exception("Not a Dell machine!")
            
    except:
        for el in queue.queue(snmptools.walk, server, community, oids.unix_cpu_number_of_cores):
            hw = el[1]
            if re.search(r"(CPU|Processor)", hw, flags = re.IGNORECASE):
                cores += 2
        return cores
        
def analyze_prod(arr, server, community, config):
    prod = arr[0][1] if arr and len(arr) >= 1 else ""
    try:
        if prod and prod != "":
            serial = queue.queue(snmptools.get, server, community, oids.dell_machine_service_tag)
            return "%s (service tag: %s)" % (prod, serial), False
    except:
        pass
    os = "Ubuntu(?)"
    try:
        oss = queue.queue(snmptools.get, server, community, oids.unix_os)
        m = re.search(r"(\w+)", oss)
        os = m.group(1)
    except:
        pass
    return (("%s, running %s" % (prod, os) if (prod  and prod != "") else ("Unknown (virtual?) machine, running %s") % os)), False
    
def analyze_dell_logs(arr, server, community, config):
    lines = []
    for i in range(1, 12):
        try:
            line = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_log_entries, i))
            date = queue.queue(snmptools.get, server, community, "%s.%u" % (oids.dell_log_dates, i))
            if line and date and line != "" and date != "":
                rdate = datetime.strptime(date, "%Y%m%d%H%M%S.000000-000")
                lines.append("%s :: %s" % (rdate.strftime("%a, %d %b, %Y %H:%M:%S"), line))
        except Exception as err:
            print(err)
    return "<b>Latest log entries:</b><br/>\n%s" % ("<br>\n".join(lines)), False

def analyze_systimes(arr, server, community, config):
    what = {
        'User': 50,
        'Nice': 51,
        'System': 52,
        'Idle': 53,
        'IO Wait': 54,
        'Kernel': 55
    }
    cores = get_max_cores(server, community, config)
    orig = {}
    new = {}
    diff = 1
    ts = 20
    for el in what:
        val = int(queue.queue(snmptools.get,server, community, "%s.%u.0" % (oids.unix_cpu_systimes, what[el])))
        orig[el] = val
    time.sleep(ts)
    output = ""
    for el in what:
        val = int(queue.queue(snmptools.get,server, community, "%s.%u.0" % (oids.unix_cpu_systimes, what[el])))
        new[el] = val
        diff += val - orig[el]
    for el in what:
        cpu = (new[el] - orig[el]) / (diff/100)
        output += "%s: %u%%<br/>\n" % (el, cpu)
    return output, False
        

# Define MIB actions
mibarray = {
    'load': [oids.unix_cpu_load, analyze_linux_load],
    'cpuidle': oids.unix_cpu_idle,
    'memfree': [oids.unix_memory_free, get_mem_free],
    'uptime': oids.unix_uptime,
    'perc': [oids.dell_raid_disk_states, analyze_perc_volumes],
    'array': [oids.dell_raid_disk_status, analyze_perc_disks],
    'disks': [oids.dell_disk_status, analyze_dell_disks],
    'space': [oids.unix_disk_mountpoint, linux_disk_space_used],
    'psu': [oids.dell_psu_status, analyze_dell_status],
    'cores': [oids.unix_cpu_number_of_cores, analyze_cpu_cores],
    'prod': [oids.dell_machine_product_name, analyze_prod],
    'memory': [oids.unix_memory_total, analyze_total_mem],
    'status': [oids.dell_machine_global_status, analyze_dell_overall_status],
    'temperature': [oids.dell_machine_temperatures, analyze_dell_temp],
    'cooling': [oids.dell_machine_cooling, analyze_dell_status],
    'battery': [oids.dell_machine_batteries, analyze_dell_status],
    'log': [oids.unix_os, analyze_dell_logs],
    'diskinfo': [oids.dell_disk_status, analyze_disk_info],
    'systimes': [oids.unix_os, analyze_systimes, True]
}

