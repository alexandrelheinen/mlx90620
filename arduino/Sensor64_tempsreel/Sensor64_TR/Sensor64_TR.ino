/**
 * Realtime MLX90620 example.
 *
 * Streams 64 object temperatures (°C) per frame over Serial at 9600 baud.
 * The sensor instance must live at file scope so it outlives setup().
 */

#include <MLX90620.h>

// 2 Hz refresh — see MLX90620::configure() for supported rates.
MLX90620 sensor(2);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  sensor.begin();
}

void loop() {
  sensor.loop();
}
