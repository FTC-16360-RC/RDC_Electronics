/* This example shows how to use continuous mode to take
range measurements with the VL53L0X. It is based on
vl53l0x_ContinuousRanging_Example.c from the VL53L0X API.

The range readings are in units of mm. */

#include <ESP32Servo.h>

#define LED 2

#define PIN_BLU_TOP 4  
#define PIN_BLU_MID 16 //RX2
#define PIN_BLU_LOW 17 //TX2

#define PIN_RED_TOP 18
#define PIN_RED_MID 19
#define PIN_RED_LOW 21

#define XX_SERVOS //NO_SERVOS
#define DEBUG
#define SERIAL_PLOT


//sensor pins
const int red_top_trig = 22; //22, 23
const int red_mid_trig = 14;
const int red_low_trig = 26;

const int red_top_echo = 23; //22, 23
const int red_mid_echo = 27;
const int red_low_echo = 36;

const int blu_top_trig = 25;
const int blu_mid_trig = 33;
const int blu_low_trig = 32;

const int blu_top_echo = 39;
const int blu_mid_echo = 34;
const int blu_low_echo = 35;


#define SOUND_SPEED 0.034

//sensor measurement vars
long duration_red_top;
long duration_red_mid;
long duration_red_low;

long duration_blu_top;
long duration_blu_mid;
long duration_blu_low;

double distMM_red_top;
double distMM_red_mid;
double distMM_red_low;

double distMM_blu_top;
double distMM_blu_mid;
double distMM_blu_low;


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


void sendPulse(int trigPin) {
    // Clears the trigPin
    digitalWrite(trigPin, LOW);
    delayMicroseconds(15);
    // Sets the trigPin on HIGH state for 10 micro seconds
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
}

void setup()
{
  //Init sensor pins
  pinMode(red_top_trig, OUTPUT); // Sets the trigPins as Output
  pinMode(red_mid_trig, OUTPUT); 
  pinMode(red_low_trig, OUTPUT); 

  pinMode(blu_top_trig, OUTPUT); 
  pinMode(blu_mid_trig, OUTPUT); 
  pinMode(blu_low_trig, OUTPUT); 

  pinMode(red_top_echo, INPUT); // Sets the echoPins as Input
  pinMode(red_mid_echo, INPUT); 
  pinMode(red_low_echo, INPUT); 

  pinMode(blu_top_echo, INPUT); 
  pinMode(blu_mid_echo, INPUT); 
  pinMode(blu_low_echo, INPUT); 


  //Init blinker
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

  //Init Serial
  Serial.begin(9600);
  Serial.println("GOT MY SETUP");

    #ifndef NO_SERVOS
  //Init Servos
  ServoBluTop.attach(PIN_BLU_TOP);
  ServoBluMid.attach(PIN_BLU_MID);
  ServoBluLow.attach(PIN_BLU_LOW);

  ServoRedTop.attach(PIN_RED_TOP);
  ServoRedMid.attach(PIN_RED_MID);
  ServoRedLow.attach(PIN_RED_LOW);
    #endif

  digitalWrite(LED, 0);
}

void loop()
{
  //Handle Blink
  if(millis() - t_last_blink >= blink_interval) {
    digitalWrite(LED, !digitalRead(LED)); //Toggle LED
    
    t_last_blink = millis();
  }

    #ifndef NO_SERVOS
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
    #endif

  //Handle Sensor Input
  sendPulse(red_top_trig);
  duration_red_top = pulseIn(red_top_echo, HIGH, 10000);

  sendPulse(red_mid_trig);
  duration_red_mid = pulseIn(red_mid_echo, HIGH, 10000);

  sendPulse(red_low_trig);
  duration_red_low = pulseIn(red_low_echo, HIGH, 10000);


  sendPulse(blu_top_trig);
  duration_blu_top = pulseIn(blu_top_echo, HIGH, 10000);

  sendPulse(blu_mid_trig);
  duration_blu_mid = pulseIn(blu_mid_echo, HIGH, 10000);

  sendPulse(blu_low_trig);
  duration_blu_low = pulseIn(blu_low_echo, HIGH, 10000);


  distMM_red_top = 10 * duration_red_top * SOUND_SPEED/2;
  distMM_red_mid = 10 * duration_red_mid * SOUND_SPEED/2;
  distMM_red_low = 10 * duration_red_low * SOUND_SPEED/2;

  distMM_blu_top = 10 * duration_blu_top * SOUND_SPEED/2;
  distMM_blu_mid = 10 * duration_blu_mid * SOUND_SPEED/2;
  distMM_blu_low = 10 * duration_blu_low * SOUND_SPEED/2;


#ifndef SERIAL_PLOT

  if(distMM_red_top > 5 && distMM_red_top < 800) {
    Serial.print("Distance at sensor "); Serial.print(red_top_trig); Serial.print(" ");
    Serial.println(distMM_red_top);
  }

  if(distMM_red_mid > 5 && distMM_red_mid < 800) {
    Serial.print("Distance at sensor "); Serial.print(red_mid_trig); Serial.print(" ");
    Serial.println(distMM_red_mid);
  }

  if(distMM_red_low > 5 && distMM_red_low < 800) {
    Serial.print("Distance at sensor "); Serial.print(red_low_trig); Serial.print(" ");
    Serial.println(distMM_red_low);
  }


  if(distMM_blu_top > 5 && distMM_blu_top < 800) {
    Serial.print("Distance at sensor "); Serial.print(blu_top_trig); Serial.print(" ");
    Serial.println(distMM_blu_top);
  }

  if(distMM_blu_mid > 5 && distMM_blu_mid < 800) {
    Serial.print("Distance at sensor "); Serial.print(blu_mid_trig); Serial.print(" ");
    Serial.println(distMM_blu_mid);
  }

  if(distMM_blu_low > 5 && distMM_blu_low < 800) {
    Serial.print("Distance at sensor "); Serial.print(blu_low_trig); Serial.print(" ");
    Serial.println(distMM_blu_low);
  }
#endif

#ifdef SERIAL_PLOT
    Serial.print(red_top_trig); Serial.print(":");
    Serial.print(distMM_red_top);
    Serial.print(",");

    Serial.print(red_mid_trig); Serial.print(":");
    Serial.print(distMM_red_mid);
    Serial.print(",");

    Serial.print(red_low_trig); Serial.print(":");
    Serial.print(distMM_red_low);
    Serial.print(",");

    Serial.print(blu_top_trig); Serial.print(":");
    Serial.print(distMM_blu_top);
    Serial.print(",");

    Serial.print(blu_mid_trig); Serial.print(":");
    Serial.print(distMM_blu_mid);
    Serial.print(",");
    
    Serial.print(blu_low_trig); Serial.print(":");
    Serial.print(distMM_blu_low);
    Serial.println("");
  

#endif


  delay(10);

}
