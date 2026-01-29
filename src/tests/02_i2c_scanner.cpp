#include <Arduino.h>
#include <Wire.h>
//This is the first thing you’ll run after wiring sensors:
void setup() {
  Serial.begin(115200);
  delay(500);
  Wire.begin(21, 22); // SDA, SCL for ESP32
  Serial.println("I2C scan starting...");
}

void loop() {
  int count = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found I2C device at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      count++;
      delay(5);
    }
  }
  Serial.print("Total devices: ");
  Serial.println(count);
  Serial.println("Scan again in 5s...\n");
  delay(5000);
}
