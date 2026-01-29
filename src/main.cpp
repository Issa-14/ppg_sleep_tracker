#include <Arduino.h>
#include "ppg_sensor.h"
#include "filter.h"
#include "peak.h"
#include "features.h"

PPGSensor ppg;
MovingAverageFilter filter(5);
PeakDetector peak(2000, 300);
HRVTracker hrv(60);

void setup() {
    Serial.begin(115200);
    Serial.println("Project structure ready");
}

void loop() {
    delay(1000);
    Serial.println("Waiting for hardware...");
}
