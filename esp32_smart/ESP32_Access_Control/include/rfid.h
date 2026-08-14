#ifndef RFID_H
#define RFID_H

#include <Arduino.h>

void RFID_Init(void);

bool RFID_ReadUID(String &uid);

#endif