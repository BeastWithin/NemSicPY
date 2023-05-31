#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, time
import requests
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
#from adafruit_dht import DHT11
#from adafruit_dht import DHT22
from email.mime.text import MIMEText
import logging


from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

#SMTPserver = 'smtp.office365.com'
#port =587
#sender =     'nemsic@hotmail.com'
#destination = ['eczsinancengiz@gmail.com']
#USERNAME = "nemsic@hotmail.com"
#PASSWORD = ""
# email fonksiyonunun değişmezleri githubta kolaylık olması açısından başka dosyadan import olacak
from değişmezler import *

#lastAlarmSent=""
logging.basicConfig(filename='NemSıc.log', level=logging.DEBUG) #log tutmak için

ayGün=time.strftime("%d")
ölçümKlasörü="/nemsicolcum/"

sensorPins={
    4:("Ön Oda","DHT11",(0,32)), #birdençok sensor eklenebilir, sensoradı,sensor tipi, istenen sıcaklık aralığı
                5:("Buzdolabı Sensoru","DHT22",(2,8)),
                3:("Laboratuar","DHT11",(0,32))
}


mikrodenetleyici="arduino"  #"arduino" veya "raspi"
arduino_serial_path="/dev/ttyACM0"
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
def plotReport(veriDosyasıYolu,gün,kayıtDizini=ölçümKlasörü,raporÇıktısı="rapor.png"):
    from plotly.express import line as plotline
    from pandas import read_csv
    data=read_csv(veriDosyasıYolu,sep="\t")
    fig = plotline( data, x="Zaman", y="Sıcaklık", color="Sensor",title=gün+' Günü Sıcaklık Raporu')
    fig.write_image(os.path.join(kayıtDizini,raporÇıktısı))  

def sendEmail(content, subject, filePath=None,
 sender=sender,destination=destination,USERNAME=USERNAME,PASSWORD=PASSWORD,SMTPserver=SMTPserver,port=port, text_subtype = 'plain'):
    msg = MIMEMultipart()
    msg.attach(MIMEText(content, text_subtype))
    msg['Subject']=       subject
    msg['From']   = sender # some SMTP servers will do this automatically, not all
    if filePath:
        with open(filePath, 'rb') as f:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            
            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)
            
            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                "attachment; filename= {}".format(filePath),
            )
            
            # Add attachment to message and convert message to string
            msg.attach(part)              
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
    try:
        conn.sendmail(sender, destination, msg.as_string())
    except:
        logging.error("Email gönderimi başarısız")

    conn.quit()
    
def sendalarm(okunanDeğerler):
    content="\n{}\n{}".format(str(time.ctime()),ipNe())# şimdiki zamanı ekleme
    for sensor in okunanDeğerler:
        sıc,nem=okunanDeğerler[sensor][1]
        sensoradı=okunanDeğerler[sensor][0]
        content+="\nSensor:{}\tSıcaklık:{}°C\tNem:%{}".format(sensoradı,sıc,nem) #ne kadar sensor varsa okumaları listeleme
    sendEmail(content, "NemSıc Alarm")

def sendGünlükRapor(gün,ölçümKlasörü=ölçümKlasörü,raporÇıktısı="rapor.png"):
    """Gün sonu yollayacağı rapor için fonksiyon"""
    dosyaYolu=os.path.join(ölçümKlasörü,time.strftime("%Y"),time.strftime("%m"),gün+".csv")
    raporYolu=os.path.join(ölçümKlasörü,raporÇıktısı)
    plotReport(dosyaYolu,gün,)
    content="{} günü günlük ölçüm raporudur.".format(gün)
    sendEmail(content,"NemSıc Günlük Rapor",filePath=raporYolu)


def dosyayaKayıt(sensoradı,nem,sıc,dosyadizini=ölçümKlasörü):
    """Csv dosyasına verileri kaydetme"""
    
    yıl, ay, gün= time.strftime("%Y %m %d").split()
    dosyadizini=os.path.join(dosyadizini,yıl,ay)
    try:
        os.makedirs(dosyadizini)
    except:
        pass
    dosyaAdı='{}.csv'.format(gün)
    dosyayolu=os.path.join(dosyadizini,dosyaAdı)
    if not os.path.exists(dosyayolu):
        os.system("echo 'Zaman\tSensor\tSıcaklık\tNem' >> '{}'".format(dosyayolu))
    else:
        os.system("echo '{}\t{}\t{}\t{}' >> '{}'".format(time.strftime("%H:%M:%S"),sensoradı,sıc,nem,dosyayolu))    
    

def sıcKontrol(sıc,sıcaralık): #verilen aralık bilgisine göre sıcaklığı kontrol eder, boolean döner
    if sıc==None: return False
    elif sıcaralık[0]<=sıc<=sıcaralık[1]: return True
    else: return False

def bipbipbip(freq=5550,count=5,length=300):
    """PC speaker'dan bipleme sesi çıkarma fonksiyonu"""
    os.system("beep -f {} -l {} -r {}".format(freq,length,count))

def ipNe():
    ip=None
    try:
        ip=requests.get("http://ipecho.net/plain?").text
    finally:
        return ip


import serial
robinyo=serial.Serial(port=arduino_serial_path,)
def get_data_serial(açıkport=robinyo):

   # time.sleep(3)
    robi=""
    while len(robi)<38: 
        robi = açıkport.readline()  #3t NANt NANs4t NANt NANs5t26.60t23.10
    robi=robi.decode().strip().replace(" ","").split("s") #byte objecti stringe dönüştürme, /n gibi şeyleri ve boşlukları atma ve boşluklardan listelere dönüştürme
    #["3tNANtNAN","4tNANtNAN","5t26.60t23.10"]
    robiOkunanDeğerler={}
    for i in robi:    
        i=i.split("t") #["5","26.60","23.10"]
        pinNo=int(i[0])
        try:
            sıc=float(i[2])
        except ValueError:
            sıc="None"
        try:
            nem=float(i[1])
        except ValueError: 
            nem="None"
        
        robiOkunanDeğerler[pinNo]=(sensorPins[pinNo][0],(sıc,nem)) #{5:("Buzdolabı",(26.60,23.10)}
        #logging.info(robiOkunanDeğerler)
        
    return robiOkunanDeğerler #{'sensor0': ['None'], 'sensor1': ['None'], 'sensor2': ['39.60', '22.20']}


def mainloop(ölçümaralığı):
    global ayGün
    while True:
        #sıcaklıklar=[]
        alarm=False
        if mikrodenetleyici=="raspi":
            okunanDeğerler={i:(sensorPins[i][0],get_data(i,sensorPins[i][1])) for i in sensorPins}   # {23:("buzdolabı",(sıcaklık,nem))}
        if mikrodenetleyici=="arduino":
            okunanDeğerler=get_data_serial()
            
        #pyexcel_ods.write_data(str(time.strftime("%Y %m"))+" data.ods",{time.strftime("%d"):[["Saat",time.strftime("%H:%M:%S")],["Sıcaklık",2],["Nem",2]]})
        for sensor in okunanDeğerler:
            sıc=okunanDeğerler[sensor][1][0]
            nem=okunanDeğerler[sensor][1][1]
            sensoradı=sensorPins[sensor][0]
            dosyayaKayıt(sensoradı,nem,sıc)
            if not sıcKontrol(sıc,sensorPins[sensor][2]): #sensor sıcaklığı ve sensor aralığı
                alarm=True


        if alarm:
            try:
                bipbipbip()
            except:
                logging.error("Alarm sesi verilemedi.")
            sendalarm(okunanDeğerler)
        
        if not ayGün ==time.strftime("%d"):
            try:
                sendGünlükRapor(ayGün)
            except:
                logging.error("Günlük rapor yollanamadı.")
            ayGün=time.strftime("%d")
        time.sleep(ölçümaralığı)



if __name__ == "__main__":
    if len(sys.argv)==1:
        ölçümaralığı=600
        mainloop(ölçümaralığı)
    else:
        if "-a" in sys.argv:
            print(str(get_data_serial()))
