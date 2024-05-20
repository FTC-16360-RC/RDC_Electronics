/* This example shows how to use continuous mode to take
range measurements with the VL53L0X. It is based on
vl53l0x_ContinuousRanging_Example.c from the VL53L0X API.

The range readings are in units of mm. */

#include <Wire.h>
#include <VL53L0X.h>
#include <ESP32Servo.h>

#define LED 2
#define SDA_PIN 32
#define SCL_PIN 33

#define PIN_BLU_TOP 14
#define PIN_BLU_MID 31
#define PIN_BLU_LOW 12

#define PIN_RED_TOP 11
#define PIN_RED_MID 7
#define PIN_RED_LOW 4


//Servo Vars
VL53L0X sensor;
unsigned long t_last_scan = 0;
unsigned long scan_interval = 10;


//Blink Vars
unsigned long t_last_blink = 0;
unsigned long blink_interval = 1000;


//Servo Vars
Servo ServoBluTop;
Servo ServoBluMid;
Servo ServoBluLow;

Servo ServoRedTop;
Servo ServoRedMid;
Servo ServoRedLow;

const int open_angle_bt = 0;
const int open_angle_bm = 0;
const int open_angle_bl = 0;

const int open_angle_rt = 0;
const int open_angle_rm = 0;
const int open_angle_rl = 0;

const int closed_angle_bt = 90;
const int closed_angle_bm = 90;
const int closed_angle_bl = 90;

const int closed_angle_rt = 90;
const int closed_angle_rm = 90;
const int closed_angle_rl = 90;

const int step = 5;

int current_angle_bt = 0;
int current_angle_bm = 0;
int current_angle_bl = 0;

int current_angle_rt = 0;
int current_angle_rm = 0;
int current_angle_rl = 0;

int target_angle_bt = 0;
int target_angle_bm = 0;
int target_angle_bl = 0;

int target_angle_rt = 0;
int target_angle_rm = 0;
int target_angle_rl = 0;

long servo_update_interval = 3;
long t_pervious_servo_update = 0;


void setup()
{
  //Init i2c
  Wire.setPins(SDA_PIN, SCL_PIN);
  Wire.begin();

  //Init blinker
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

  //Init Serial
  Serial.begin(9600);
  Serial.println("GOT MY SETUP");

  //Init Servos
  ServoBluTop.attach(PIN_BLU_TOP);
  ServoBluMid.attach(PIN_BLU_MID);
  ServoBluLow.attach(PIN_BLU_LOW);

  ServoRedTop.attach(PIN_RED_TOP);
  ServoRedMid.attach(PIN_RED_MID);
  ServoRedLow.attach(PIN_RED_LOW);

  //Init Sernsors
  sensor.setTimeout(500);
  if (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    while (1) {}
  }
  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
  sensor.startContinuous();

  digitalWrite(LED, 0);
}

void loop()
{
  //Handle Blink
  if(millis() - t_last_blink >= blink_interval) {
    digitalWrite(LED, !digitalRead(LED)); //Toggle LED
    
    t_last_blink = millis();
  }

  //Handle Servo Input
  Serial.print("Distance at sensor 29: ");
  Serial.print(String(sensor.readRangeContinuousMillimeters()));
  if (sensor.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  Serial.println("");

  //Handle Servo nonBlocking
  if(millis() - t_pervious_servo_update >= servo_update_interval) {
    t_pervious_servo_update = millis();

    //Blu Top Servo
    if (current_angle_bt < target_angle_bt) {
      current_angle_bt += step;
      ServoBluTop.write(current_angle_bt);
    }
    else if (current_angle_bt > target_angle_bt) {
      current_angle_bt -= step;
      ServoBluTop.write(current_angle_bt);
    }

    //Blu Mid Servo
    if (current_angle_bm < target_angle_bm) {
      current_angle_bm += step;
      ServoBluMid.write(current_angle_bm);
    }
    else if (current_angle_bm > target_angle_bm) {
      current_angle_bm -= step;
      ServoBluMid.write(current_angle_bm);
    }

    //Blo Low Servo
    if (current_angle_bl < target_angle_bl) {
      current_angle_bl += step;
      ServoBluLow.write(current_angle_bl);
    }
    else if (current_angle_bl > target_angle_bl) {
      current_angle_bl -= step;
      ServoBluLow.write(current_angle_bl);
    }

    //Red Top Servo
    if (current_angle_rt < target_angle_rt) {
      current_angle_rt += step;
      ServoRedTop.write(current_angle_rt);
    }
    else if (current_angle_rt > target_angle_rt) {
      current_angle_rt -= step;
      ServoRedTop.write(current_angle_rt);
    }

    //Red Mid Servo
    if (current_angle_rm < target_angle_rm) {
      current_angle_rm += step;
      ServoRedMid.write(current_angle_rm);
    }
    else if (current_angle_rm > target_angle_rm) {
      current_angle_rm -= step;
      ServoRedMid.write(current_angle_rm);
    }

    //Red Low Servo
    if (current_angle_rl < target_angle_rl) {
      current_angle_rl += step;
      ServoRedLow.write(current_angle_rl);
    }
    else if (current_angle_rl > target_angle_rl) {
      current_angle_rl -= step;
      ServoRedLow.write(current_angle_rl);
    }
  }

  if(Serial.available() > 0) {
    String msg = Serial.readString();
    
    //Red
    if(msg == "RED_TOP_OPEN") {
      target_angle_rt = open_angle_rt;
    }
    else if(msg == "RED_TOP_CLOSE") {
      target_angle_rt = closed_angle_rt;
    }

    else if(msg == "RED_MID_OPEN") {
      target_angle_rm = open_angle_rm;
    }
    else if(msg == "RED_MID_CLOSE") {
      target_angle_rm = closed_angle_rm;
    }

    else if(msg == "RED_LOW_OPEN") {
      target_angle_rl = open_angle_rl;
    }
    else if(msg == "RED_LOW_CLOSE") {
      target_angle_rl = closed_angle_rl;
    }

    //Blue
    else if(msg == "BLU_TOP_OPEN") {
      target_angle_bt = open_angle_bt;
    }
    else if(msg == "BLU_TOP_CLOSE") {
      target_angle_bt = closed_angle_bt;
    }

    else if(msg == "BLU_MID_OPEN") {
      target_angle_bm = open_angle_bm;
    }
    else if(msg == "BLU_MID_CLOSE") {
      target_angle_bm = closed_angle_bm;
    }

    else if(msg == "BLU_LOW_OPEN") {
      target_angle_bl = open_angle_bl;
    }
    else if(msg == "BLU_LOW_CLOSE") {
      target_angle_bl = closed_angle_bl;
    }
  }
}
