#include "features.h"

HRVTracker::HRVTracker(int window) : window(window) {}

void HRVTracker::addIBI(uint16_t ibi_ms) {}

float HRVTracker::rmssd() const {
    return 0.0f;
}
