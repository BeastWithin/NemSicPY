#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time
import requests
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from adafruit_dht import DHT11
from adafruit_dht import DHT22
from email.mime.text import MIMEText
import logging

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
logging.basicConfig(filename='NemSıc.log', level=logging.DEBUG) #log tutmak için

sensorPins={
    23:("Ön Oda",DHT11,(0,32)), #birdençok sensor eklenebilir, sensoradı,sensor tipi, istenen sıcaklık aralığı
                24:("Buzdolabı Sensoru",DHT22,(2,8)),
                25:("Laboratuar",DHT11,(0,32))
}

#DHT işlemleri
def get_data(sensorpin,sensortype):
    den=0
    sıc=None
    nem=None
    while den<25: #25 defa sensor okumayı denesin diye, olmazsa None dönsün
        try:
            dhtDevice = sensortype(sensorpin)
            sıc=dhtDevice.temperature
            nem=dhtDevice.humidity
            dhtDevice.exit() #sensorün yine okunabilmesi için şart. yoksa ligpio işlemi yüzünden hata veriyor.
            break
        except:
            dhtDevice.exit()
            den+=1
            logging.error("Sensor okunamadı: Deneme {}".format(den))
            time.sleep(0.77)
            continue
    return (sıc,nem)

###


    

###


def sendalarm(okunanDeğerler):
    content="\n{}\n{}".format(str(time.ctime()),ipNe())# şimdiki zamanı ekleme
    for sensor in okunanDeğerler:
        sıc,nem=okunanDeğerler[sensor][1]
        sensoradı=okunanDeğerler[sensor][0]
        content+="\nSensor:{}\tSıcaklık:{}°C\tNem:%{}".format(sensoradı,sıc,nem) #ne kadar sensor varsa okumaları listeleme
    msg = MIMEText(content, text_subtype)
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all
    try:
        conn = SMTP(SMTPserver,port)
    except:
        logging.error("Email sunucusuna bağlanılamadı.")
        return
    #conn.set_debuglevel(1)
    conn.ehlo()
    conn.starttls()
    try:
        conn.login(USERNAME, PASSWORD)
    except:
        logging.error("Login Hatası")
        return
    #try:
        #print("{} tarafından {} adresine {} konulu mesaj yollanıyor...",format(sender,destination,subject))
    try:
        conn.sendmail(sender, destination, msg.as_string())
    except:
        logging.error("Email gönderimi başarısız")
    #except:
        #print("Başaramadık abi")
    #finally:
    conn.quit()

def dosyayaKayıt(sensoradı,nem,sıc): #csv dosyasına verileri kaydetme
    os.system("echo '{}\t{}\t{}\t{}\t{}' >> 'nemsicolcum/{}.csv'".format(time.strftime("%d"),time.strftime("%H:%M:%S"),sensoradı,sıc,nem,time.strftime("%Y %m")))

def sıcKontrol(sıc,sıcaralık): #verilen aralık bilgisine göre sıcaklığı kontrol eder, boolean döner
    if sıc==None: return False
    elif sıcaralık[0]<=sıc<=sıcaralık[1]: return True
    else: return False

def ipNe():
    ip=None
    try:
        ip=requests.get("http://ipecho.net/plain?").text
    finally:
        return ip


import serial
def get_data_serial(port):
    robinyo=serial.Serial(port="/dev/ttyACM0",)
    robi = robinyo.readline()  #25.00t30.00 25.00t30.00 25.00t30.00
    robiOkunanDeğerler={}
    robi=robi.split(" ")
    for i,sensor in range(len(robi)),robi:    #"0","25.00t30.00"
        robiOkunanDeğerler["sensor"+string(i)]=sensor #{"sensor0":"25.00t30.00"}
    for sensor in robiOkunanDeğerler:
        if robiOkunanDeğerler[sensor]=="None":
            pass
        robiOkunanDeğerler[sensor]=robiOkunanDeğerler[sensor].split("t") #{"sensor0":["25.00","30.00"]}
    return robiOkunanDeğerler

        


while True:
    #sıcaklıklar=[]
    alarm=False
    okunanDeğerler={i:(sensorPins[i][0],get_data(i,sensorPins[i][1])) for i in sensorPins}   # {pin23:("buzdolabı",(sıcaklık,nem))}

    #pyexcel_ods.write_data(str(time.strftime("%Y %m"))+" data.ods",{time.strftime("%d"):[["Saat",time.strftime("%H:%M:%S")],["Sıcaklık",2],["Nem",2]]})
    for sensor in okunanDeğerler:
        sıc=okunanDeğerler[sensor][1][0]
        nem=okunanDeğerler[sensor][1][1]
        sensoradı=sensorPins[sensor][0]
        #sıcaklıklar.append(sıc)
        dosyayaKayıt(sensoradı,nem,sıc)
        if not sıcKontrol(sıc,sensorPins[sensor][2]): #sensor sıcaklığı ve sensor aralığı
            alarm=True
    #if not all([s for s in sıcaklıklar]):
        #sendalarm(okunanDeğerler)
    #elif not all([s<25 for s in sıcaklıklar]):
        #sendalarm(okunanDeğerler)

    if alarm: sendalarm(okunanDeğerler)
    time.sleep(3600)



