#ifndef UART_H
#define UART_H

#include <Arduino.h>

void UART_Init();
void UART_Send(const String &data);
void UART_SendUID(const String &uid);

void UART_SendStatus(uint8_t status);
#endif