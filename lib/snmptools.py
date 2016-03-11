import oids
import subprocess
import re

# SMMP Walk + Get
def walk(server, community, oid):
    try:
        try:
            output = subprocess.check_output(["snmpwalk", "-t", "10", "-Os", "-c", community, "-v", "2c", server, oid])
            print(output)
            assert(len(output) > 20)
        except:
            output = subprocess.check_output(["snmpwalk", "-t", "10", "-Os", "-c", "secret", "-v", "2c", server, oid])
    except subprocess.CalledProcessError as err:
        output = ""
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
            
def get(server, community, oid):
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

def is_snmp(server, community, oid):
    try:
        isit = False
        try:
            output = subprocess.check_output(["snmpget", "-Os", "-c", community, "-v", "2c", server, oids.unix_os])
        except:
            output = subprocess.check_output(["snmpget", "-Os", "-c", community, "-v", "2c", server, oids.unix_os])
        if output and len(output):
            return True
    except Exception as err:
        pass
    return False
