from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import re
from __main__ import snmp_pages, snmp_jobs
import templates

# Spawn our own HTTP server?
class dsnmpHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
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
            if group and group in snmp_pages:
                if not page or page == "":
                    page = "index"
                if page and page in snmp_pages[group]:
                    self.wfile.write(snmp_pages[group][page])
                    if group in snmp_jobs and snmp_jobs[group] < 100:
                        self.wfile.write("<p>Currently scanning hosts, %u%% done...</p>" % snmp_jobs[group])
                else:
                    self.wfile.write(templates.html_temp_template)
            else:
                self.wfile.write("<h2>dSNMP main page</h2><ul>")
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