from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import re
from __main__ import snmp_pages, snmp_jobs, snmp_json
import templates
import base64
import json

# Spawn our own HTTP server?
class dsnmpHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            extension = None
            m = re.search(r"\.([a-z]+)$", self.path)
            if m:
                extension = m.group(1)
                
            self.send_header('Connection',"close")
            if extension == "ico":
                self.send_header('Content-type',"image/x-icon")
            elif extension == "json":
                self.send_header('Content-type',"appliation/json")
            elif extension == "png":
                self.send_header('Content-type',"image/png")
            elif extension == "gif":
                self.send_header('Content-type',"image/gif")
            else:
                self.send_header('Content-type',"text/html")
            self.end_headers()
            data = ""
            m = re.match(r"^/([^/]*)/?([^/]*?)(\.[a-z]+)?$", self.path)
            group = None
            page = None
            if m:
                group = m.group(1)
                page = m.group(2)
                ext = m.group(3)
            if group and group in snmp_pages:
                if not page or page == "":
                    page = "index"
                if page and page in snmp_pages[group]:
                    self.wfile.write(snmp_pages[group][page])
                    if group in snmp_jobs and snmp_jobs[group] < 100:
                        self.wfile.write("<p>Currently scanning hosts, %u%% done...</p>" % snmp_jobs[group])
                elif page == "status" and ext and ext == ".json" and group in snmp_json:
                    self.wfile.write(json.dumps(snmp_json[group]))
                else:
                    self.wfile.write(templates.html_temp_template)
            elif self.path == "/favicon.ico":
                self.wfile.write(base64.decodestring(templates.favicon))
            elif self.path == "/logo.png":
                self.wfile.write(base64.decodestring(templates.logo))
            elif self.path == "/loader.gif":
                self.wfile.write(base64.decodestring(templates.loader))
            else:
                self.wfile.write("<img src='/logo.png'><br/><ul>")
                for group in snmp_pages:
                    self.wfile.write("<li><a href='/%s/'>%s</a></li>" % (group, group))
                self.wfile.write("</ul>")
        except Exception as err:
            pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Moomins live here"""

def start_server(portno):
    server = ThreadedHTTPServer(('', portno), dsnmpHTTPHandler)
    server.serve_forever()