#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import time
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
import adafruit_dht
from email.mime.text import MIMEText


SMTPserver = 'smtp.office365.com'
port =587
sender =     'nemsic@hotmail.com'
destination = ['eczsinancengiz@gmail.com']
#destination = ['eczpinar.ekmek@gmail.com']
USERNAME = "nemsic@hotmail.com"
PASSWORD = "Y3QLt66TLGRkxNt"
# typical values for text_subtype are plain, html, xml
text_subtype = 'plain'
subject="NemSıc Alarm"
lastAlarmSent=""

#DHT işlemleri
def get_data(sensorpin):
    dhtDevice = adafruit_dht.DHT11(sensorpin)
    sıc=dhtDevice.temperature
    nem=dhtDevice.humidity
    return (sıc,nem)


def sendalarm(sıc,nem):
    content="\n{}\nSıcaklık:{}°C\nNem:%{}".format(str(time.ctime()),sıc,nem)
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all
    
    conn = SMTP(SMTPserver,port)
    conn.set_debuglevel(1)
    conn.ehlo()
    conn.starttls()
    conn.login(USERNAME, PASSWORD)
    #try:
        #print("{} tarafından {} adresine {} konulu mesaj yollanıyor...",format(sender,destination,subject))
    conn.sendmail(sender, destination, msg.as_string())
    #except:
        #print("Başaramadık abi")
    #finally:
    conn.quit()

while True:
    sıc,nem=get_data(23)
    os.system("echo {},{},{} >> '{}.txt'".format(time.strftime("%H:%M:%S"),sıc,nem,time.strftime("%Y %m")))
    #pyexcel_ods.write_data(str(time.strftime("%Y %m"))+" data.ods",{time.strftime("%d"):[["Saat",time.strftime("%H:%M:%S")],["Sıcaklık",2],["Nem",2]]})
    if sıc > 25:
        sendalarm(sıc,nem)
    time.sleep(600)


