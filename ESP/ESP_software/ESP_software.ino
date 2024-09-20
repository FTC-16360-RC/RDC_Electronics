/* This example shows how to use continuous mode to take
range measurements with the VL53L0X. It is based on
vl53l0x_ContinuousRanging_Example.c from the VL53L0X API.

The range readings are in units of mm. */

#include <ESP32Servo.h>

#define LED 2
#define SDA_PIN 32
#define SCL_PIN 33

#define PIN_BLU_TOP 17
#define PIN_BLU_MID 31
#define PIN_BLU_LOW 12

#define PIN_RED_TOP 11
#define PIN_RED_MID 7
#define PIN_RED_LOW 23


//sensor Vars
const int trigPin = 19;
const int echoPin = 18;

#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701

long duration;
float distanceMM;
float distanceInch;



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
const int open_angle_rl = 18;

const int closed_angle_bt = 90;
const int closed_angle_bm = 90;
const int closed_angle_bl = 90;

const int closed_angle_rt = 90;
const int closed_angle_rm = 90;
const int closed_angle_rl = 77;

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
  //Init sensor
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);  // Sets the echoPin as an Input

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

  digitalWrite(LED, 0);
}

void loop()
{
  //Handle Blink
  if(millis() - t_last_blink >= blink_interval) {
    digitalWrite(LED, !digitalRead(LED)); //Toggle LED
    
    t_last_blink = millis();
  }


  if(Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    
    //Red
    if(msg == "RED_TOP_OPEN") {
      //target_angle_rt = open_angle_rt;
      ServoRedTop.write(open_angle_rt);
    }
    else if(msg == "RED_TOP_CLOSE") {
      //target_angle_rt = closed_angle_rt;$
      ServoRedTop.write(closed_angle_rt);
    }

    else if(msg == "RED_MID_OPEN") {
      //target_angle_rm = open_angle_rm;
      ServoRedMid.write(open_angle_rm);
    }
    else if(msg == "RED_MID_CLOSE") {
      //target_angle_rm = closed_angle_rm;
      ServoRedMid.write(closed_angle_rm);
    }

    else if(msg == "RED_LOW_OPEN") {
      //target_angle_rl = open_angle_rl;
      ServoRedLow.write(open_angle_rl);
    }
    else if(msg == "RED_LOW_CLOSE") {
      //target_angle_rl = closed_angle_rl;
      ServoRedLow.write(closed_angle_rl);
    }

    //Blue
    else if(msg == "BLU_TOP_OPEN") {
      //target_angle_bt = open_angle_bt;
      ServoBluTop.write(open_angle_bt);
    }
    else if(msg == "BLU_TOP_CLOSE") {
      //target_angle_bt = closed_angle_bt;
      ServoBluTop.write(closed_angle_bt);
    }

    else if(msg == "BLU_MID_OPEN") {
      //target_angle_bm = open_angle_bm;
      ServoBluMid.write(open_angle_bm);
    }
    else if(msg == "BLU_MID_CLOSE") {
      //target_angle_bm = closed_angle_bm;
      ServoBluMid.write(closed_angle_bm);
    }

    else if(msg == "BLU_LOW_OPEN") {
      //target_angle_bl = open_angle_bl;
      ServoBluLow.write(open_angle_bl);
    }
    else if(msg == "BLU_LOW_CLOSE") {
      //target_angle_bl = closed_angle_bl;
      ServoBluLow.write(closed_angle_bl);
    }
  }

  //Handle Sensor Input

    // Clears the trigPin
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    // Sets the trigPin on HIGH state for 10 micro seconds
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    // Reads the echoPin, returns the sound wave travel time in microseconds
    duration = pulseIn(echoPin, HIGH);
    
    // Calculate the distance
    distanceMM = duration * SOUND_SPEED/2 * 10;

  Serial.print("Distance at sensor 29: ");
  Serial.println(String(int(trunc(distanceMM))));

  delay(10);

}
