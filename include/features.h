#pragma once
#include <Arduino.h>

class HRVTracker {
public:
    HRVTracker(int window);
    void addIBI(uint16_t ibi_ms);
    float rmssd() const;

private:
    int window;
};
