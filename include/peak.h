#pragma once
#include <Arduino.h>

class PeakDetector { //Heartbeats
public:
    PeakDetector(int32_t threshold, uint32_t minIntervalMs);
    bool update(int32_t sample, uint32_t timeMs);
    uint16_t lastIBI_ms() const;

private:
    uint32_t lastPeakTime = 0;
    uint16_t lastIBI = 0;
};
