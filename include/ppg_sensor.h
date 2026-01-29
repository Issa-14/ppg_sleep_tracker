#pragma once
#include <Arduino.h>

class PPGSensor { //MAX30102
public:
    bool begin();
    int32_t readIR();
};
