#ifndef DEBUG_H
#define DEBUG_H

#include <Arduino.h>

void Debug_Init();

void Debug_Print(const String &msg);

void Debug_Println();
void Debug_Println(const String &msg);

void Debug_Banner();

#endif