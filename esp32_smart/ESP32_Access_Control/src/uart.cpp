#include "uart.h"
#include "config.h"

void UART_Init()
{
    Serial2.begin(115200, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
}

void UART_Send(const String &data)
{
    Serial2.println(data);
}
void UART_SendUID(const String &uid)
{
    Serial2.println("U:" + uid);
}

void UART_SendStatus(uint8_t status)
{
    Serial2.print("S:");
    Serial2.println(status);
}