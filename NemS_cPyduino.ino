

#include "DHT.h"


DHT lab(LAB, DHT11);
DHT oda(ODA, DHT11);
DHT bd(BDO, DHT22);



void setup() {
  Serial.begin(9600);
//  Serial.println(F("DHTxx test!"));

  lab.begin();// Laboratuar Sensörü
  oda.begin();// Oda Sensörü
  bd.begin();// Buzdolabı Sensörü Digital pin connected to the DHT sensor

}



String measure(DHT dht){
  float h=dht.readHumidity();
  float t=dht.readTemperature();
  if (isnan(t)|| isnan(h)){return "None";};
  return String(h)+"t"+String(t);
}
void loop() {
  // Wait a few seconds between measurements.
  delay(2000);

  

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  Serial.println(" "+measure(lab)+" "+measure(oda)+" "+measure(bd));

//  Serial.print(F("°C "));

}
