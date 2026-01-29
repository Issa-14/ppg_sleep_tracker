#pragma once
#include <Arduino.h>

class MovingAverageFilter { //Signal
public:
    MovingAverageFilter(int size);
    int32_t update(int32_t x);

private:
    int size;
};
