# SMTP Lib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sendmail function
def sendMail(to, subject, text, html, settings):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings['global_settings']['email_from']
    msg['To'] = to
    
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html', 'UTF-8')
    msg.attach(part1)
    msg.attach(part2)
    s = smtplib.SMTP('localhost')
    s.sendmail(settings['global_settings']['email_addr'], to, msg.as_string())
    s.quit()
    