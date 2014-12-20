# Sendmail function
def sendMail(to, subject, text, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = ml_from
    msg['To'] = to
    
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html', 'UTF-8')
    msg.attach(part1)
    msg.attach(part2)
    s = smtplib.SMTP('localhost')
    s.sendmail(ml_addr, to, msg.as_string())
    s.quit()
    