import json, urllib, requests, re, logging, hashlib

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
    
    
hipchat_archive = {}
def scanHipChat(group, config, firstRun = False):
        hipchat_token = config['contact']['hipchat']['token']
        if not group in hipchat_archive:
            hipchat_archive[group] = {}
        room = config['contact']['hipchat']['room']
        ret = []
        try:
            js = json.loads(urllib.urlopen("https://api.hipchat.com/v1/rooms/history?auth_token=%s&room_id=%s&date=recent" % (hipchat_token, room)).read())
            if firstRun:
                for line in js['messages']:
                    hash256 = line['date'] + hashlib.sha256(line['message'].encode("ascii","ignore")).hexdigest()
                    hipchat_archive[group][hash256] = True
            for line in js['messages']:
                hash256 = line['date'] + hashlib.sha256(line['message'].encode("ascii","ignore")).hexdigest()
                if not hash256 in hipchat_archive[group]:
                    hipchat_archive[group][hash256] = True
                    match = re.match(r"#snmp (\S+) (\S+)(.*)", line['message'])
                    if match and line['from']['name'] != u'SNMP2HipChat':
                        community = None
                        host = match.group(1)
                        typ = match.group(2)
                        com = match.group(3)
                        if len(com) > 1:
                            community = com.strip()
                        ret.append(['check', host, typ, community])
                    if line['message'] == "#snmpstatus":
                        ret.append(['status'])
                    if line['message'] == "#snmpconf":
                        ret.append(['config'])
                    if line['message'] == "#snmphelp" or line['message'] == "#snmp help":
                        ret.append(['help'])
        except Exception as err:
            print("Could not get hipchat data for %s (using https://api.hipchat.com/v1/rooms/history?auth_token=%s&room_id=%s&date=recent): %s" % (group, hipchat_token, room, err))
        
        return ret
