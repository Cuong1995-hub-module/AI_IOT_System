#include "hardware.h"
#include "config.h"

void Hardware_Init()
{
    pinMode(RED_LED_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
}

void RedLED(bool state)
{
    digitalWrite(RED_LED_PIN, state);
}

void GreenLED(bool state)
{
    digitalWrite(GREEN_LED_PIN, state);
}

void Beep(uint16_t ms)
{
    digitalWrite(BUZZER_PIN, HIGH);
    delay(ms);
    digitalWrite(BUZZER_PIN, LOW);
}