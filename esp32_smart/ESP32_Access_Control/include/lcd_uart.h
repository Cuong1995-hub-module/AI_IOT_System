#ifndef LCD_UART_H
#define LCD_UART_H

#include <Arduino.h>
enum LCDStatus
{
    LCD_ERROR = 0,
    LCD_PASS,
    LCD_WAIT,
    LCD_READY,
    LCD_TIMEOUT
};

void LCDUART_Init(void);
void LCDUART_SendUID(const String &uid);
void LCDUART_SendStatus(uint8_t status);

#endif