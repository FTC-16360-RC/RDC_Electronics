#include <Vector>
#include <Map>
#include <Wire.h>
#include "Adafruit_VL53L0X.h"

#define LED 2

std::vector<byte> addresses;

std::map<byte, Adafruit_VL53L0X> sensors;

int x = 0;
bool booted;

std::vector<byte> findAddresses() {
  byte error, address;
  int nDevices;
  std::vector<byte> addresses = {};
 
  Serial.println("Scanning for addresses...");
 
  nDevices = 0;

  for(address = 1; address < 127; address++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
 
    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.print(address,HEX);
      Serial.println("  !");
      addresses.push_back(address);
 
      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Unknown error at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.println(address,HEX);
    }    
  }
  if (nDevices == 0) Serial.println("No I2C devices found");
  else {
    Serial.println("done");
  }

  return addresses;
}


void setup() {

  Serial.begin(9600);
  while(!Serial);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  delay(1000);
  digitalWrite(LED, HIGH);

  Wire.begin();

  addresses = findAddresses();
  delay(1000);
  Serial.println("--------");

  for(int i = 0; i < addresses.size(); i++) {
    byte address = addresses.at(i);                 //get address for new sensor
    sensors[address] = Adafruit_VL53L0X();          //put new sensor in array
    
    Serial.println(address,HEX);
    booted = (sensors[address]).begin();

    while(false) {     //initialize sensor
      //Serial.print(F("Failed to boot VL53L0X at address: "));
      //Serial.print(address, HEX);
      //Serial.println("");
      delay(1000);
    }
  }
}

void loop() {
  Serial.print("dings: ");
  Serial.println(booted);
  delay(1000);
  /*for(int i = 0; i < addresses.size(); i++) {
    Serial.println(addresses.at(i), HEX);
    delay(500);
  }*/
}
