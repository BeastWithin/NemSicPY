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
sys.stdout=open("NemSıc.log","a")

#DHT işlemleri
def get_data(sensorpin):
    den=0
    sıc=None
    nem=None
    while den<25:
        try: #25 defa sensor okumayı denesin diye
            dhtDevice = adafruit_dht.DHT11(sensorpin)
            sıc=dhtDevice.temperature
            nem=dhtDevice.humidity
            dhtDevice.exit() #sensorün yine okunabilmesi için şart. yoksa ligpio işlemi yüzünden hata veriyor. 
            break
        except:
            dhtDevice.exit()
            den+=1
            print("Sensor okunamadı: Deneme {}".format(den))
            time.sleep(0.77)
            continue
    return (sıc,nem)


def sendalarm(sıc,nem):
    content="\n{}\nSıcaklık:{}°C\nNem:%{}".format(str(time.ctime()),sıc,nem)
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all
    try:
        conn = SMTP(SMTPserver,port)
    except:
        print("Email sunucusuna bağlanılamadı.")
        return
    #conn.set_debuglevel(1)
    conn.ehlo()
    conn.starttls()
    try:
        conn.login(USERNAME, PASSWORD)
    except:
        print("Login Hatası")
        return
    #try:
        #print("{} tarafından {} adresine {} konulu mesaj yollanıyor...",format(sender,destination,subject))
    try:
        conn.sendmail(sender, destination, msg.as_string())
    except:
        print("Email gönderimi başarısız")
    #except:
        #print("Başaramadık abi")
    #finally:
    conn.quit()

while True:
    sıc,nem=get_data(23)
    os.system("echo {},{},{} >> '{}.txt'".format(time.strftime("%H:%M:%S"),sıc,nem,time.strftime("%Y %m"))) #txt dosyasına verileri kaydetme
    #pyexcel_ods.write_data(str(time.strftime("%Y %m"))+" data.ods",{time.strftime("%d"):[["Saat",time.strftime("%H:%M:%S")],["Sıcaklık",2],["Nem",2]]})
    if sıc > 25 or sıc==None:
        sendalarm(sıc,nem)
    time.sleep(600)


sys.stdout.close()


