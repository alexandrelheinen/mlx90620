/**
 * Scan (balayage) MLX90620 example.
 *
 * Steps two servos across a small mosaic, acquires one IR frame per pose, and
 * emits a scan marker (<= -300) followed by 64 temperatures for MATLAB.
 */

#include <Servo.h>

#include <MLX90620.h>

// Sensor refresh rate (Hz).
MLX90620 sensor(4);

// Servo geometry (degrees) — matches the 2015 mechanical scan setup.
const int kPanStartDeg = 90 - 4 * 6;
const int kPanEndDeg = 90 + 4 * 6;
const int kTiltStartDeg = 90;
const int kTiltEndDeg = 70;
const int kPanSteps = 4;
const int kTiltSteps = 1;
const int kPanServoPin = 9;
const int kTiltServoPin = 11;

Servo panServo;
Servo tiltServo;

int panStepIndex = 0;
int tiltStepIndex = 0;
int panStepDegrees = 0;
int tiltStepDegrees = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  sensor.begin();

  panStepDegrees = (kPanEndDeg - kPanStartDeg) / kPanSteps;
  tiltStepDegrees = (kTiltEndDeg - kTiltStartDeg) / kTiltSteps;

  panServo.attach(kPanServoPin);
  tiltServo.attach(kTiltServoPin);
  panServo.write(kPanStartDeg);
  tiltServo.write(kTiltStartDeg);
}

void loop() {
  panServo.write(kPanStartDeg + panStepIndex * panStepDegrees);
  tiltServo.write(kTiltStartDeg + tiltStepIndex * tiltStepDegrees);
  delay(250);

  sensor.update();
  // MATLAB uses rowIndex = tiltStepIndex, colIndex = panStepIndex.
  sensor.transmitScanFrame(static_cast<uint8_t>(tiltStepIndex), static_cast<uint8_t>(panStepIndex));

  panStepIndex++;
  if (panStepIndex >= kPanSteps) {
    panStepIndex = 0;
    tiltStepIndex++;
    if (tiltStepIndex >= kTiltSteps) {
      tiltStepIndex = 0;
    }
  }
}
