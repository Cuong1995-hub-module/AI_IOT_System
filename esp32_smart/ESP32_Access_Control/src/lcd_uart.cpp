#include "lcd_uart.h"
#include "config.h"

void LCDUART_Init(void)
{
    Serial2.begin(115200, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
}

void LCDUART_SendUID(const String &uid)
{
    Serial2.print("U:");
    Serial2.println(uid);
}

void LCDUART_SendStatus(uint8_t status)
{
    Serial2.print("S:");
    Serial2.println(status);
}