/**
 * @file MLX90620.cpp
 * @brief Implementation of the MLX90620 Arduino sensor library.
 *
 * Temperature formulas follow the Melexis MLX90620 datasheet (ambient TA from
 * PTAT / Vth / Kt coefficients; per-pixel TO with offset, TGC, emissivity, and
 * alpha compensation). I2C traffic uses the vendored hardware TWI master.
 */

#include "MLX90620.h"

#include <math.h>

MLX90620::MLX90620(int refreshRateHz)
    : configReg_(0),
      compensationPixel_(0),
      ptat_(0),
      ambientTemperatureC_(0.0f),
      aCp_(0),
      bCp_(0),
      bIScale_(0),
      emissivity_(1.0f),
      kT1_(0.0f),
      kT2_(0.0f),
      vTh_(0),
      tgc_(0),
      refreshRateHz_(refreshRateHz),
      frameCounter_(0),
      begun_(false) {
  for (uint16_t i = 0; i < kEepromSize; ++i) {
    eepromData_[i] = 0;
  }
  for (uint8_t i = 0; i < kPixelCount; ++i) {
    irData_[i] = 0;
    objectTemperaturesC_[i] = 0.0f;
    aIj_[i] = 0;
    bIj_[i] = 0;
    alphaIj_[i] = 0.0f;
  }
}

void MLX90620::begin() {
  i2c_init();
  // Enable internal pull-ups on Uno A4 (SDA) and A5 (SCL).
  PORTC = (1 << PORTC4) | (1 << PORTC5);
  delay(5);

  readEEPROM();
  initialiseCalibration();
  configure(refreshRateHz_);
  frameCounter_ = 0;
  begun_ = true;
}

void MLX90620::update() {
  if (!begun_) {
    return;
  }

  // Match the sensor's slower ambient refresh: recompute TA every 16 frames.
  if (frameCounter_ == 0) {
    readPTAT();
    calculateTA();
    checkConfigReg();
  }

  frameCounter_++;
  if (frameCounter_ >= 16) {
    frameCounter_ = 0;
  }

  readIR();
  readCPIX();
  calculateTO();
}

void MLX90620::loop() {
  // Pace acquisitions roughly to the configured refresh rate.
  delay(static_cast<unsigned long>(1000.0f / static_cast<float>(refreshRateHz_ > 0 ? refreshRateHz_ : 1)));
  update();
  transmitTemperatures();
}

float MLX90620::objectTemperatureC(uint8_t index) const {
  if (index >= kPixelCount) {
    return NAN;
  }
  return objectTemperaturesC_[index];
}

uint8_t MLX90620::eepromByte(uint16_t index) const {
  if (index >= kEepromSize) {
    return 0;
  }
  return eepromData_[index];
}

int16_t MLX90620::irData(uint8_t index) const {
  if (index >= kPixelCount) {
    return 0;
  }
  return irData_[index];
}

int MLX90620::scanFrameMarker(uint8_t rowIndex, uint8_t colIndex) {
  return -(300 + 10 * static_cast<int>(rowIndex) + static_cast<int>(colIndex));
}

void MLX90620::transmitTemperatures() const {
  for (uint8_t i = 0; i < kPixelCount; ++i) {
    Serial.println(objectTemperaturesC_[i]);
  }
}

void MLX90620::transmitScanFrame(uint8_t rowIndex, uint8_t colIndex) const {
  Serial.println(scanFrameMarker(rowIndex, colIndex));
  transmitTemperatures();
}

void MLX90620::calculateTA() {
  // Datasheet: solve quadratic in PTAT for ambient temperature (°C).
  const float discriminant =
      kT1_ * kT1_ - 4.0f * kT2_ * (static_cast<float>(vTh_) - static_cast<float>(ptat_));
  ambientTemperatureC_ = (-kT1_ + sqrt(discriminant)) / (2.0f * kT2_) + 25.0f;
}

void MLX90620::calculateTO() {
  const float ta = ambientTemperatureC_;
  const float scale = pow(2.0f, static_cast<float>(bIScale_));
  // Compensation pixel removes the temperature-gradient contribution (TGC path).
  const float vComp =
      static_cast<float>(compensationPixel_) -
      (static_cast<float>(aCp_) + static_cast<float>(bCp_) / scale * (ta - 25.0f));

  for (uint8_t i = 0; i < kPixelCount; ++i) {
    float sample =
        static_cast<float>(irData_[i]) -
        (static_cast<float>(aIj_[i]) + static_cast<float>(bIj_[i]) / scale * (ta - 25.0f));
    sample = sample - static_cast<float>(tgc_) / 32.0f * vComp;
    sample = sample / emissivity_;
    // Planck-style inversion using per-pixel alpha_ij (datasheet object formula).
    objectTemperaturesC_[i] =
        sqrt(sqrt(sample / alphaIj_[i] + pow(ta + 273.15f, 4.0f))) - 273.15f;
  }
}

void MLX90620::checkConfigReg() {
  readConfigReg();
  const uint8_t configMsb = static_cast<uint8_t>(static_cast<uint16_t>(configReg_) >> 8);
  // Bit 2 of the config MSB is the brown-out / POR flag; reconfigure when clear.
  if ((configMsb & 0x04) == 0) {
    configure(refreshRateHz_);
  }
}

void MLX90620::configure(int refreshRateHz) {
  uint8_t hzLsb;
  switch (refreshRateHz) {
    case 0:
      hzLsb = 0x0F;  // 0.5 Hz
      break;
    case 1:
      hzLsb = 0x0E;
      break;
    case 2:
      hzLsb = 0x0D;
      break;
    case 4:
      hzLsb = 0x0C;
      break;
    case 8:
      hzLsb = 0x0B;
      break;
    case 16:
      hzLsb = 0x0A;
      break;
    case 32:
      hzLsb = 0x09;
      break;
    default:
      hzLsb = 0x0E;
      break;
  }

  i2c_start_wait(kAddrSensorWrite);
  i2c_write(0x03);
  i2c_write(static_cast<uint8_t>(hzLsb - 0x55));
  i2c_write(hzLsb);
  i2c_write(0x1F);
  i2c_write(0x74);
  i2c_stop();
}

void MLX90620::readConfigReg() {
  i2c_start_wait(kAddrSensorWrite);
  i2c_write(0x02);
  i2c_write(0x92);
  i2c_write(0x00);
  i2c_write(0x01);
  i2c_rep_start(kAddrSensorRead);
  const uint8_t lsb = i2c_readAck();
  const uint8_t msb = i2c_readAck();
  i2c_stop();
  configReg_ = static_cast<int16_t>((static_cast<uint16_t>(msb) << 8) | lsb);
}

void MLX90620::readCPIX() {
  i2c_start_wait(kAddrSensorWrite);
  i2c_write(0x02);
  i2c_write(0x91);
  i2c_write(0x00);
  i2c_write(0x01);
  i2c_rep_start(kAddrSensorRead);
  const uint8_t lsb = i2c_readAck();
  const uint8_t msb = i2c_readAck();
  i2c_stop();
  compensationPixel_ = static_cast<int16_t>((static_cast<uint16_t>(msb) << 8) | lsb);
}

void MLX90620::readEEPROM() {
  i2c_start_wait(kAddrEepromWrite);
  i2c_write(0x00);
  i2c_rep_start(kAddrEepromRead);
  for (uint16_t i = 0; i < kEepromSize; ++i) {
    // ACK all bytes including the last; the historical bring-up used readAck throughout.
    eepromData_[i] = i2c_readAck();
  }
  i2c_stop();
  writeTrimmingValue(eepromData_[0xF7]);
}

void MLX90620::readIR() {
  i2c_start_wait(kAddrSensorWrite);
  i2c_write(0x02);
  i2c_write(0x00);
  i2c_write(0x01);
  i2c_write(0x40);
  i2c_rep_start(kAddrSensorRead);
  for (uint8_t i = 0; i < kPixelCount; ++i) {
    const uint8_t lsb = i2c_readAck();
    const uint8_t msb = i2c_readAck();
    irData_[i] = static_cast<int16_t>((static_cast<uint16_t>(msb) << 8) | lsb);
  }
  i2c_stop();
}

void MLX90620::readPTAT() {
  i2c_start_wait(kAddrSensorWrite);
  i2c_write(0x02);
  i2c_write(0x90);
  i2c_write(0x00);
  i2c_write(0x01);
  i2c_rep_start(kAddrSensorRead);
  const uint8_t lsb = i2c_readAck();
  const uint8_t msb = i2c_readAck();
  i2c_stop();
  ptat_ = (static_cast<uint16_t>(msb) << 8) | lsb;
}

void MLX90620::writeTrimmingValue(uint8_t value) {
  i2c_start_wait(kAddrSensorWrite);
  i2c_write(0x04);
  i2c_write(static_cast<uint8_t>(value - 0xAA));
  i2c_write(value);
  i2c_write(0x56);
  i2c_write(0x00);
  i2c_stop();
}

int16_t MLX90620::signExtend8(uint8_t value) {
  return (value > 127) ? static_cast<int16_t>(value) - 256 : static_cast<int16_t>(value);
}

void MLX90620::initialiseCalibration() {
  // Datasheet ~p.14 — absolute temperature coefficients.
  vTh_ = static_cast<int16_t>((static_cast<uint16_t>(eepromData_[0xDB]) << 8) | eepromData_[0xDA]);
  kT1_ = static_cast<float>((static_cast<uint16_t>(eepromData_[0xDD]) << 8) | eepromData_[0xDC]) /
         1024.0f;
  kT2_ = static_cast<float>((static_cast<uint16_t>(eepromData_[0xDF]) << 8) | eepromData_[0xDE]) /
         1048576.0f;

  // Datasheet ~p.17 — compensation pixel and scale.
  aCp_ = signExtend8(eepromData_[0xD4]);
  bCp_ = signExtend8(eepromData_[0xD5]);
  tgc_ = signExtend8(eepromData_[0xD8]);
  bIScale_ = static_cast<int16_t>(eepromData_[0xD9]);
  emissivity_ =
      static_cast<float>((static_cast<uint16_t>(eepromData_[0xE5]) << 8) | eepromData_[0xE4]) /
      32768.0f;

  for (uint8_t i = 0; i < kPixelCount; ++i) {
    aIj_[i] = signExtend8(eepromData_[i]);            // offsets at 0x00
    bIj_[i] = signExtend8(eepromData_[0x40 + i]);     // slopes at 0x40
  }

  const uint16_t alpha0L = eepromData_[0xE0];
  const uint16_t alpha0H = eepromData_[0xE1];
  const uint16_t alpha0S = eepromData_[0xE2];
  const uint16_t deltaAlphaS = eepromData_[0xE3];
  for (uint8_t c = 0; c < kPixelCount; ++c) {
    const uint16_t deltaAlphaIj = eepromData_[0x80 + c];
    alphaIj_[c] = (256.0f * alpha0H + alpha0L) / pow(2.0f, static_cast<float>(alpha0S)) +
                  deltaAlphaIj / pow(2.0f, static_cast<float>(deltaAlphaS));
  }
}
