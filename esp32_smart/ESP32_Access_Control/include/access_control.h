#ifndef ACCESS_CONTROL_H
#define ACCESS_CONTROL_H

#include <Arduino.h>

void AccessControl_Init(void);
void AccessControl_Loop(void);

void AccessControl_OnRFID(const String &uid);
void AccessControl_OnMessage(const String &topic,
                             const String &payload);

#endif