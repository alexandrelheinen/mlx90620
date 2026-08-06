# Third-party notices

This repository includes or depends on the following third-party material.

## I2C Master Library (hardware TWI)

- **Path:** `firmware/external/I2Cmaster/` (historically `arduino/libraries/I2Cmaster/`)
- **Authors:** Peter Fleury; distributed via the [DSSCircuits I2C-Master-Library](https://github.com/DSSCircuits/I2C-Master-Library) packaging used in the 2015 project
- **License:** GNU General Public License v3 (see `firmware/external/I2Cmaster/License.txt` and the root `LICENSE`)
- **Use:** Low-level AVR TWI access for the MLX90620 sensor from Arduino Uno sketches

Because this dependency is GPL-3, the combined firmware distributed from this repository is released under GPL-3 as well.

## Melexis MLX90620

- **Role:** Infrared thermometer array sensor (16×4)
- **Datasheet:** [Melexis MLX90620 product page / datasheet](https://www.melexis.com/en/product/MLX90620/)
- Calibration formulas implemented in `firmware/lib/MLX90620` follow the device datasheet (primarily sections describing ambient and object temperature calculation from EEPROM coefficients).

## Historical reference code

Portions of the original sensor bring-up were informed by community Arduino forum discussions around the MLX90620 (notably IlBaboomba’s examples). The library in this repository was rewritten as an object-oriented API for the 2015 Supélec project and corrected during the 2026 modernization.
