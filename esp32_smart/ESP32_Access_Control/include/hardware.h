#ifndef HARDWARE_H
#define HARDWARE_H

#include <Arduino.h>

void Hardware_Init();

void RedLED(bool state);

void GreenLED(bool state);

void Beep(uint16_t ms);

#endif