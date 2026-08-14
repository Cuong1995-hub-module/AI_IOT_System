#include "buzzer.h"

#include <Arduino.h>

namespace
{
    constexpr uint8_t BUZZER_PIN = 6;
}

void Buzzer_Init(void)
{
    pinMode(BUZZER_PIN, OUTPUT);

    digitalWrite(BUZZER_PIN, LOW);
}

void Buzzer_On(void)
{
    digitalWrite(BUZZER_PIN, HIGH);
}

void Buzzer_Off(void)
{
    digitalWrite(BUZZER_PIN, LOW);
}