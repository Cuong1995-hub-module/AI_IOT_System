#include "led.h"

namespace
{
    constexpr uint8_t LED_RED_PIN   = 4;
    constexpr uint8_t LED_GREEN_PIN = 5;
}

void LED_Init(void)
{
    pinMode(LED_RED_PIN, OUTPUT);
    pinMode(LED_GREEN_PIN, OUTPUT);

    LED_RedOff();
    LED_GreenOff();
}

void LED_RedOn(void)
{
    digitalWrite(LED_RED_PIN, HIGH);
}

void LED_RedOff(void)
{
    digitalWrite(LED_RED_PIN, LOW);
}

void LED_GreenOn(void)
{
    digitalWrite(LED_GREEN_PIN, HIGH);
}

void LED_GreenOff(void)
{
    digitalWrite(LED_GREEN_PIN, LOW);
}