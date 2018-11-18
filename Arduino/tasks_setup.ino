#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050.h"
#include "Arduino_FreeRTOS.h"
#include "semphr.h"
#include "task.h"

#define STACK_SIZE 400

/* IMU Variables and Constants */
MPU6050 accelgyro; //address used is 0x68
float current;
float realV;
float power;
float energy = 0;
unsigned long prevMillis = 0;
int16_t leftaxoff, leftayoff, leftazoff, leftgxoff, leftgyoff, leftgzoff;
int16_t rightaxoff, rightayoff, rightazoff, rightgxoff, rightgyoff, rightgzoff;

/* RTOS Variables and Constants */
const byte startHandshake = 'H';
const byte ack = 'A';
const byte nak = 'N';

/****** STRUCT DECLARATIONS ******/
struct sensorReadings {
  int16_t acc_x;
  int16_t acc_y;
  int16_t acc_z;
  int16_t gyro_x;
  int16_t gyro_y;
  int16_t gyro_z;
};

struct sensorReadings arm_left;
struct sensorReadings arm_right;
/*********************************/

/****** DATA SERIALIZATION *******/
const int packetLength = 12;
const int bufferSize = 16;
int sendId = 0;  // data yet to be ack by rpi (head of ringbuffer)
int insertId = 0; // data to save to
int16_t ringBuffer[bufferSize][packetLength];

// Copies structure data into an array of char
unsigned int serialize(int16_t *buf, int16_t *p, size_t size) {
  int16_t checksum = 0;
  buf[0] = size + 2;  // need to +4 for voltage, current, power, cumpower
  memcpy(buf + 1, p, size * 2); // using int16_t, so need to copy 2x the num of bytes
  for (int i = 1; i <= size; i++) {
    checksum ^= buf[i];
  }
  buf[size + 1] = checksum;

  // insert buf into ring buffer
  ringBuffer[insertId][packetLength] = buf[1];
  insertId = (insertId + 1) % bufferSize;

  //  Serial.print("size is ");
  //  Serial.println(size+2);
  return size + 2;
}

void sendDataPacket() {
  int16_t cfg[packetLength];
  int16_t buffer[64];

  // Copy sensor data to data packet
  cfg[0] = arm_left.acc_x;
  cfg[1] = arm_left.acc_y;
  cfg[2] = arm_left.acc_z;
  cfg[3] = arm_left.gyro_x;
  cfg[4] = arm_left.gyro_y;
  cfg[5] = arm_left.gyro_z;

  cfg[6] = arm_right.acc_x;
  cfg[7] = arm_right.acc_y;
  cfg[8] = arm_right.acc_z;
  cfg[9] = arm_right.gyro_x;
  cfg[10] = arm_right.gyro_y;
  cfg[11] = arm_right.gyro_z;

  unsigned len = serialize(buffer, cfg, sizeof(cfg) / 2);
  sendSerialData(buffer, len);
}

void sendSerialData(int16_t *buffer, int len) {
  // Send calculated data first
  Serial2.println(realV);
  Serial2.println(current);
  Serial2.println(power);
  Serial2.println(energy);
  for (int i = 0; i < len; i++) {
    //    Serial.print("Test send: ");
    //    Serial.println(buffer[i]);
    Serial2.println(buffer[i]);
  }
}
/*********************************/

/********** TASKS ***************/
void uartComm(void) {
  Serial.println("uartComm");
  // organise data, serialize, send
  sendDataPacket();

  // wait for ack
  while (Serial2.available() <= 0) {
    //    Serial.println("waiting for data ack");
  }

  // respond accordingly
  char ackByte = Serial2.read();
  while (ackByte == 'N') {
    Serial.println("N received");
    sendSerialData(ringBuffer[sendId], packetLength);
    if (Serial2.available() > 0)
      ackByte = Serial2.read();
  }

  Serial.println("A received");
  // update ring buffer
  sendId = (sendId + 1) % bufferSize;
}

void getSensorData(void) {
  //  Serial.println("getData");
  /******** get power data **********/
  int voltage = analogRead(A0);
  realV = voltage / 1023.0 * 5 * 1.5;
  Serial.print("voltage: ");
  Serial.println(realV);

  int currentVal = analogRead(A1);
  float sensor = (currentVal * 5.0) / 1023;
  current = ((sensor) / (0.1 * 10000) * 1000); //* (3.5 - 0.35) + 0.35)*1000; //changing the range of current to 0.35A to 3.5A
  Serial.print("current: ");
  Serial.println(current); //mA

  power = current * realV; //mW

  unsigned long currentMillis = millis();
  energy += power / 1000 * ((currentMillis - prevMillis) / 1000.0); //J = W s 
  Serial.print("energy: ");
  Serial.print(energy);
  Serial.println("J");
  prevMillis = currentMillis;
  /************************************/

  /******** get sensor data ***********/
  int16_t ax1, ay1, az1, gx1, gy1, gz1;
  int16_t ax2, ay2, az2, gx2, gy2, gz2;

  // FIRST SENSOR
  digitalWrite(50, LOW);
  digitalWrite(51, HIGH);
  digitalWrite(52, HIGH);
  digitalWrite(53, HIGH);

  accelgyro.getAcceleration(&ax1, &ay1, &az1);
  accelgyro.getRotation(&gx1, &gy1, &gz1);

  //  Serial.print(",arm_left,");
  Serial.print(ax1 - leftaxoff);
  Serial.print(",");
  Serial.print(ay1 - leftayoff);
  Serial.print(",");
  Serial.print(az1 - leftazoff);
  Serial.print(",");
  Serial.print(gx1 - leftgxoff);
  Serial.print(",");
  Serial.print(gy1 - leftgyoff);
  Serial.print(",");
  Serial.print(gz1 - leftgzoff);
  Serial.print(",");

  arm_left.acc_x = ax1 - leftaxoff;
  arm_left.acc_y = ay1 - leftayoff;
  arm_left.acc_z = az1 - leftazoff;
  arm_left.gyro_x = gx1 - leftgxoff;
  arm_left.gyro_y = gy1 - leftgyoff;
  arm_left.gyro_z = gz1 - leftgzoff;

  // SECOND SENSOR
  digitalWrite(50, HIGH);
  digitalWrite(51, HIGH);
  digitalWrite(52, HIGH);
  digitalWrite(53, LOW);

  accelgyro.getAcceleration(&ax2, &ay2, &az2);
  accelgyro.getRotation(&gx2, &gy2, &gz2);

  //  Serial.print(",arm_right,");
  Serial.print(ax2 - rightaxoff);
  Serial.print(",");
  Serial.print(ay2 - rightayoff);
  Serial.print(",");
  Serial.print(az2 - rightazoff);
  Serial.print(",");
  Serial.print(gx2 - rightgxoff);
  Serial.print(",");
  Serial.print(gy2 - rightgyoff);
  Serial.print(",");
  Serial.println(gz2 - rightgzoff);

  arm_right.acc_x = ax2 - rightaxoff;
  arm_right.acc_y = ay2 - rightayoff;
  arm_right.acc_z = az2 - rightazoff;
  arm_right.gyro_x = gx2 - rightgxoff;
  arm_right.gyro_y = gy2 - rightgyoff;
  arm_right.gyro_z = gz2 - rightgzoff;
  /********************************/
}

void vTask(void *pvParameters) {
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();

  while (1) {
    getSensorData();
    uartComm();
    vTaskDelayUntil(&xLastWakeTime, 3);
  }
}

/********************************/

void setup() {
  // put your setup code here, to run once:
  /**************** Hardware Set Up ************************/
  /* Set up voltage, current sensors */
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  /* Set up serial comm */
  Serial.begin(115200); // for debugging purposes
  Serial2.begin(115200);

  /* Set up IMU1 */
  int16_t ax, ay, az, gx, gy, gz;

  pinMode(50, OUTPUT);
  digitalWrite(50, LOW);
  Wire.begin();
  accelgyro.initialize();
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 first connection successful" : "MPU6050 first connection failed");
  //set range
  accelgyro.setFullScaleAccelRange(1);
  accelgyro.setFullScaleGyroRange(1);
  // Offset calibration
  double sumax = 0; double sumay = 0; double sumaz = 0; double sumgx = 0; double sumgy = 0; double sumgz = 0;
  for (int i = 0; i < 1000; i++) {
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    sumax += ax * 1.0 / 32768; sumay += ay * 1.0 / 32768; sumaz += az * 1.0 / 32768;
    sumax += gx * 1.0 / 32768; sumax += gy * 1.0 / 32768; sumax += gz * 1.0 / 32768;
  }
  leftaxoff = sumax / 1000.0 * 32768;
  leftayoff = sumay / 1000.0 * 32768;
  leftazoff = sumaz / 1000.0 * 32768;
  leftgxoff = sumgx / 1000.0 * 32768;
  leftgyoff = sumgy / 1000.0 * 32768;
  leftgzoff = sumgz / 1000.0 * 32768;

  /* Set up IMU4 */
  pinMode(53, OUTPUT);
  digitalWrite(52, HIGH);
  digitalWrite(53, LOW);
  accelgyro.initialize();
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 second connection successful" : "MPU6050 second connection failed");
  //set range
  accelgyro.setFullScaleAccelRange(1);
  accelgyro.setFullScaleGyroRange(1);
  sumax = 0; sumay = 0; sumaz = 0; sumgx = 0; sumgy = 0; sumgz = 0;
  for (int i = 0; i < 1000; i++) {
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    sumax += ax * 1.0 / 32768; sumay += ay * 1.0 / 32768; sumaz += az * 1.0 / 32768;
    sumax += gx * 1.0 / 32768; sumax += gy * 1.0 / 32768; sumax += gz * 1.0 / 32768;
  }
  rightaxoff = sumax / 1000.0 * 32768;
  rightayoff = sumay / 1000.0 * 32768;
  rightazoff = sumaz / 1000.0 * 32768;
  rightgxoff = sumgx / 1000.0 * 32768;
  rightgyoff = sumgy / 1000.0 * 32768;
  rightgzoff = sumgz / 1000.0 * 32768;

  /****************************************************************/

  /********** Bootup handshake process (Arduino side) *************/
  // Keep sending to RPi "hello\n" and wait for ACK ("ACK")
  // when received ACK, send ACK to RPi

  // Wait for serial port to be available before sending handshake message
  while (!Serial2) {
    //  while (!Serial) {
    delay(100);
  }

  // Keep waiting for 'H' from RPi
  while (!Serial2.available() || Serial2.read() != int('H')) {     // no ACK
    //  while (!Serial.available() || Serial.read() != 'H') {
    delay(100);
  }

  // Respond with 'A' from RPi
  Serial2.write('A');
  //  Serial.write('A');
  // Wait for 'A' from RPi
  while (!Serial2.available() || Serial2.read() != int('A')) {
    //  while (!Serial.available() || Serial.read() != 'A') {
    delay(100);
  }
  Serial.println("Connection established");

  /********************************************************/

  /****************** Set up Tasks ************************/
  xTaskCreate(vTask, "vTask", STACK_SIZE, NULL, 1, NULL);
}

void loop() {
  // put your main code here, to run repeatedly:
}
