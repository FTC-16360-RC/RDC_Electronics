#include <Wire.h>
#include <VL53L0X.h>
#include <ESP32Servo.h>

#define xshut_1 19
#define xshut_2 15
#define LED 2

VL53L0X sensor1;
VL53L0X sensor2;
Servo servo1;
Servo servo2;
unsigned long t_last_blink = 0;
unsigned long blink_interval = 1000;

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  
  Wire.begin(); // SDA, SCL
  Serial.begin(9600);
  while (!Serial); // Wait for Serial Monitor to open

  servo1.attach(4);
  servo2.attach(5);

  pinMode(xshut_1, OUTPUT);
  digitalWrite(xshut_1, LOW);

  pinMode(xshut_2, OUTPUT);
  digitalWrite(xshut_2, HIGH);

  delay(1000);  // Wait for the sensor to boot up
  sensor1.setTimeout(1000);
  while (!sensor1.init()) {
    Serial.println("Failed to detect and initialize sensor 1!");
    delay(1000);
  }
  
  sensor1.setAddress(0x30);  // Change I2C address for sensor 1
  Serial.println("Sensor 1 initialized.");

  digitalWrite(xshut_1, HIGH);

  delay(1000);  // Wait for the sensor to boot up
  sensor2.setTimeout(1000);
  while (!sensor2.init()) {
    Serial.println("Failed to detect and initialize sensor 2!");
    delay(1000);
  }
  sensor2.setAddress(0x31);  // Change I2C address for sensor 2
  Serial.println("Sensor 2 initialized.");

  sensor1.startContinuous();
  sensor2.startContinuous();

  Serial.println("Succeded");
}

void loop() {

  Serial.print("Distance at sensor 30: ");
  Serial.print(String(sensor1.readRangeContinuousMillimeters()));
  if (sensor1.timeoutOccurred()) { Serial.print(" TIMEOUT"); }

  Serial.println("");

  Serial.print("Distance at sensor 31: ");
  Serial.print(String(sensor2.readRangeContinuousMillimeters()));
  if (sensor2.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  
  Serial.println("");

  
  if(millis() - t_last_blink >= blink_interval) {
    digitalWrite(LED, !digitalRead(LED)); //Toggle LED
    servo1.write(100*(!digitalRead(LED)));
    servo2.write(100*(!digitalRead(LED)));
    t_last_blink = millis();
  }
}
