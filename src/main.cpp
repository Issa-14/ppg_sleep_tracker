#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h" 

MAX30105 sensor;

// ---- smoothing + timing/state ----
static float irSmooth = 0;
static uint32_t lastBeatMs = 0;

// ---- IR print + signal quality (RANGE) ----
static uint32_t lastIrPrint = 0;
static uint32_t lastQ = 0;
static uint32_t irMin = 0xFFFFFFFF;
static uint32_t irMax = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22);
  Wire.setClock(100000);

  Serial.println("Starting MAX30102...");

  if (!sensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found. Check wiring.");
    while (1) delay(10);
  }

  sensor.setup(
    0x1F,  // ledBrightness
    8,     // sampleAverage
    2,     // ledMode (2 = Red+IR)
    100,   // sampleRate
    411,   // pulseWidth
    4096   // adcRange
  );

  sensor.setPulseAmplitudeRed(0);
  sensor.setPulseAmplitudeGreen(0);

  Serial.println("MAX30102 ready. Printing IR...");
}

void loop() {
  sensor.check();

  while (sensor.available()) {
    uint32_t ir = sensor.getIR();
    uint32_t now = millis();

    // ---- Print IR at 50 Hz for plotting ----
    if (now - lastIrPrint >= 20) {
      Serial.print("IR,");
      Serial.println(ir);
      lastIrPrint = now;
    }

    // ---- Track signal range (quality proxy) over 1 second ----
    irMin = min(irMin, ir);
    irMax = max(irMax, ir);

    if (now - lastQ >= 1000) {
      Serial.print("RANGE,");
      Serial.println(irMax - irMin);

      irMin = 0xFFFFFFFF;
      irMax = 0;
      lastQ = now;
    }

    // ---- Light smoothing before beat detection ----
    irSmooth = 0.9f * irSmooth + 0.1f * (float)ir;

    // ---- Beat detection -> print BEAT events ----
    if (checkForBeat((uint32_t)irSmooth)) {
      if (lastBeatMs != 0) {
        uint32_t dt = now - lastBeatMs;

        // accept only plausible RR 
        if (dt >= 350 && dt <= 2000) {
          float bpm = 60000.0f / dt;

          Serial.print("BEAT,");
          Serial.print(now);
          Serial.print(",");
          Serial.println(bpm, 1);
        }
      }
      lastBeatMs = now;
    }

    sensor.nextSample();
  }
}
