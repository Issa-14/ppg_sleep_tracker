#include <Arduino.h>
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("Serial OK");
}
void loop() {
  Serial.println("tick");
  delay(1000);
}
