#include "peak.h"

PeakDetector::PeakDetector(int32_t threshold, uint32_t minIntervalMs) {}

bool PeakDetector::update(int32_t sample, uint32_t timeMs) {
    return false; // placeholder
}

uint16_t PeakDetector::lastIBI_ms() const {
    return lastIBI;
}
