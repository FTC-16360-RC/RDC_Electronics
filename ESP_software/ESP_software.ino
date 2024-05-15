/* This example shows how to use continuous mode to take
range measurements with the VL53L0X. It is based on
vl53l0x_ContinuousRanging_Example.c from the VL53L0X API.

The range readings are in units of mm. */

#include <Wire.h>
#include <VL53L0X.h>

#define LED 2

VL53L0X sensor1;
VL53L0X sensor2;
unsigned long t_last_blink = 0;
unsigned long blink_interval = 1000;
unsigned long t_last_scan = 0;
unsigned long scan_interval = 10;

void setup()
{
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

  Serial.begin(9600);
  Wire.begin();

  sensor1.setTimeout(500);
  sensor2.setTimeout(500);

  sensor1.setAddress(0x29); // Set the I2C address of sensor 1
  sensor2.setAddress(0x30); // Set the I2C address of sensor 2

  while (!sensor1.init() || !sensor2.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
  }

  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
  sensor1.startContinuous();
  sensor2.startContinuous();
}

void loop()
{
  /*if(millis() - t_last_scan >= scan_interval) {*/
    Serial.print("Distance at sensor 1: ");
    Serial.print(String(sensor1.readRangeContinuousMillimeters()));
    Serial.print(", sensor 2: ");
    Serial.print(String(sensor2.readRangeContinuousMillimeters()));
    if (sensor1.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
    if (sensor2.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
    Serial.println("");

    /*t_last_scan = millis();
  }*/
  if(millis() - t_last_blink >= blink_interval) {
    digitalWrite(LED, !digitalRead(LED)); //Toggle LED
    
    t_last_blink = millis();
  }
  
}
