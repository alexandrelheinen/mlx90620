#ifndef MLX90620_H_
#define MLX90620_H_

/**
 * @file MLX90620.h
 * @brief Arduino library for the Melexis MLX90620 16x4 IR temperature array.
 *
 * Based on community bring-up code (IlBaboomba / Arduino forum) and the Melexis
 * datasheet formulas for ambient (TA) and object (TO) temperature. Reworked as a
 * class for the CentraleSupélec Projet de Conception (2014/2015) and corrected
 * during the 2026 modernization.
 *
 * Authors: Alexandre Loeblein Heinen & Clyvian Ribeiro Borges
 */

#include <Arduino.h>
#include <stdint.h>

#include <i2cmaster.h>

class MLX90620 {
public:
  /** Number of IR pixels in one frame (16 rows x 4 columns). */
  static const uint8_t kPixelCount = 64;

  /** Size of the sensor configuration EEPROM dumped over I2C. */
  static const uint16_t kEepromSize = 256;

  /**
   * @param refreshRateHz Sensor refresh rate: 0 (0.5 Hz), 1, 2, 4, 8, 16, or 32.
   *        Unsupported values fall back to 1 Hz in configure().
   */
  explicit MLX90620(int refreshRateHz = 4);

  /**
   * Initialise I2C, enable Uno SDA/SCL pull-ups, dump EEPROM, derive
   * calibration coefficients, and program the refresh rate.
   * Call once from setup() before update().
   */
  void begin();

  /**
   * Acquire one IR frame, refresh ambient temperature every 16 frames, and
   * recompute object temperatures. Does not print on Serial.
   */
  void update();

  /** Convenience: update() then transmitTemperatures(). */
  void loop();

  float ambientTemperatureC() const {
    return ambientTemperatureC_;
  }

  /** Pointer to kPixelCount object temperatures in °C (valid until next update). */
  const float* objectTemperaturesC() const {
    return objectTemperaturesC_;
  }

  float objectTemperatureC(uint8_t index) const;

  uint8_t eepromByte(uint16_t index) const;
  int16_t irData(uint8_t index) const;

  /** Print kPixelCount temperatures, one °C value per Serial line. */
  void transmitTemperatures() const;

  /**
   * Scan-mode framing: print an integer marker (<= -300) then the temperatures.
   * Marker encoding used by the MATLAB mosaic reconstructor:
   *   -(300 + 10 * rowIndex + colIndex)
   */
  void transmitScanFrame(uint8_t rowIndex, uint8_t colIndex) const;

  static int scanFrameMarker(uint8_t rowIndex, uint8_t colIndex);

private:
  // I2C device addresses (8-bit form expected by i2cmaster).
  static const uint8_t kAddrSensorWrite = 0xC0;
  static const uint8_t kAddrSensorRead = 0xC1;
  static const uint8_t kAddrEepromWrite = 0xA0;
  static const uint8_t kAddrEepromRead = 0xA1;

  void calculateTA();
  void calculateTO();
  void checkConfigReg();
  void configure(int refreshRateHz);
  void writeTrimmingValue(uint8_t value);
  void initialiseCalibration();

  void readConfigReg();
  void readCPIX();
  void readEEPROM();
  void readIR();
  void readPTAT();

  static int16_t signExtend8(uint8_t value);

  uint8_t eepromData_[kEepromSize];
  int16_t irData_[kPixelCount];
  int16_t configReg_;
  int16_t compensationPixel_;
  uint16_t ptat_;

  float ambientTemperatureC_;
  float objectTemperaturesC_[kPixelCount];

  // Datasheet calibration coefficients (derived from EEPROM).
  int16_t aCp_;
  int16_t bCp_;
  int16_t aIj_[kPixelCount];
  int16_t bIj_[kPixelCount];
  int16_t bIScale_;
  float emissivity_;
  float kT1_;
  float kT2_;
  int16_t vTh_;
  int16_t tgc_;
  float alphaIj_[kPixelCount];

  int refreshRateHz_;
  uint8_t frameCounter_;
  bool begun_;
};

#endif // MLX90620_H_
