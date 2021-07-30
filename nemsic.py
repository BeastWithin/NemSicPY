#!/usr/bin/env python3
# -*- coding: utf-8 -*-


SMTPserver = 'smtp.office365.com'
port =587
sender =     'nemsic@hotmail.com'
destination = ['cengizhasan@gmail.com']

USERNAME = "nemsic@hotmail.com"
PASSWORD = "Y3QLt66TLGRkxNt"

# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'


content="""\
Test message
"""

subject="Sent from Python"

import sys
import os
import re

#from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)

# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText

try:
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all

    conn = SMTP(SMTPserver,port)
    conn.set_debuglevel(1)
    conn.ehlo()
    conn.starttls()
    conn.login(USERNAME, PASSWORD)
    try:
        print("{} tarafından {} adresine {} konulu mesaj yollanıyor...",format(sender,destination,subject))
        conn.sendmail(sender, destination, msg.as_string())
    finally:
        conn.quit()

except:
    sys.exit( "mail failed; %s" % "CUSTOM_ERROR" ) # give an error message