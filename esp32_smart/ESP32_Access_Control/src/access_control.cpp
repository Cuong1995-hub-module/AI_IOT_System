#include "access_control.h"
#include "buzzer.h"
#include "debug.h"
#include "led.h"
#include "lcd_uart.h"
#include "mqtt_manager.h"
namespace
{
    enum class AccessState
    {
        READY,
        WAITING,
        GRANTED,
        DENIED,
        TIMEOUT
    };

    constexpr uint32_t BLINK_INTERVAL = 200;

    AccessState currentState = AccessState::READY;

    uint32_t stateStartTime = 0;
    uint32_t blinkTimer = 0;

    bool ledState = false;
    uint8_t blinkCount = 0;

    void ResetBlink(void)
{
    blinkTimer = millis();
    blinkCount = 0;
    ledState = false;
}
    //------------------------------------------------
    // READY
    //------------------------------------------------
    void HandleReady(void)
    {
        LED_GreenOff();
        LED_RedOn();
    }

    //------------------------------------------------
    // WAITING
    //------------------------------------------------
   void HandleWaiting(void)
{
    // Nháy LED đỏ mỗi 200 ms
    if (millis() - blinkTimer >= BLINK_INTERVAL)
    {
        blinkTimer = millis();

        ledState = !ledState;

        if (ledState)
        {
            LED_RedOn();
        }
        else
        {
            LED_RedOff();
        }
    }

    // Chờ tối đa 5 giây
    if (millis() - stateStartTime >= 5000)
    {
        LED_RedOff();

        currentState = AccessState::TIMEOUT;

       LCDUART_SendStatus(LCD_TIMEOUT);

        ResetBlink();

        Debug_Println("Access Timeout");
    }
}

    //------------------------------------------------
    // GRANTED
    //------------------------------------------------
    void HandleGranted(void)
    {
        if (millis() - blinkTimer < BLINK_INTERVAL)
        {
            return;
        }

        blinkTimer = millis();

        ledState = !ledState;

        if (ledState)
        {
            LED_RedOff();
            LED_GreenOn();
        }
        else
        {
            LED_GreenOff();
        }

        blinkCount++;

        // 10 lần đổi trạng thái = 5 lần nháy
        if (blinkCount >= 10)
        {
            LED_GreenOff();
            LED_RedOn();

            currentState = AccessState::READY;
            LCDUART_SendStatus(LCD_READY);

            ResetBlink();

            Debug_Println("Grant Finish");
        }
    }

    //------------------------------------------------
    // DENIED
    //------------------------------------------------
    void HandleDenied(void)
    {
        if (millis() - blinkTimer < BLINK_INTERVAL)
        {
            return;
        }

        blinkTimer = millis();

        ledState = !ledState;

        if (ledState)
        {
            LED_RedOn();
        }
        else
        {
            LED_RedOff();
        }

        blinkCount++;

        // 6 lần đổi trạng thái = 3 lần nháy
        if (blinkCount >= 6)
        {
            currentState = AccessState::READY;
            LCDUART_SendStatus(LCD_READY);
            ResetBlink();

            Debug_Println("Denied Finish");
        }
    }

    //------------------------------------------------
    // TIMEOUT
    //------------------------------------------------
  void HandleTimeout(void)
{
    if (millis() - blinkTimer >= BLINK_INTERVAL)
    {
        blinkTimer = millis();

        ledState = !ledState;

        if (ledState)
        {
            LED_RedOn();
            Buzzer_On();
        }
        else
        {
            LED_RedOff();
            Buzzer_Off();
        }

        blinkCount++;

        // 3 lần nháy = 6 lần đổi trạng thái
        if (blinkCount >= 6)
        {
            LED_RedOn();
            LED_GreenOff();
            Buzzer_Off();

            currentState = AccessState::READY;
            LCDUART_SendStatus(LCD_READY);
            ResetBlink();
            Debug_Println("Back To Ready");
        }
    }
}

} // namespace

//------------------------------------------------
// Public
//------------------------------------------------

void AccessControl_Init(void)
{
    currentState = AccessState::READY;

    stateStartTime = millis();
    ResetBlink();

    LED_GreenOff();
    LED_RedOn();

    Buzzer_Init();     // Thêm
    Buzzer_Off();      // Thêm
    LCDUART_SendStatus(LCD_READY);  

    Debug_Println("Access Control Ready");
}
//------------------------------------------------
// Loop
//------------------------------------------------

void AccessControl_Loop(void)
{
    switch (currentState)
    {
        case AccessState::READY:
            HandleReady();
            break;

        case AccessState::WAITING:
            HandleWaiting();
            break;

        case AccessState::GRANTED:
            HandleGranted();
            break;

        case AccessState::DENIED:
            HandleDenied();
            break;

        case AccessState::TIMEOUT:
            HandleTimeout();
            break;
    }
}

//------------------------------------------------
// RFID
//------------------------------------------------

void AccessControl_OnRFID(const String &uid)
{
    Buzzer_On();
    delay(50);
    Buzzer_Off();

    Debug_Print("RFID UID : ");
    Debug_Println(uid);

    LCDUART_SendUID(uid);
    LCDUART_SendStatus(LCD_WAIT);

    currentState = AccessState::WAITING;

    stateStartTime = millis();

    ResetBlink();

    MQTTManager_Publish(
        "door/rfid",
        uid.c_str());
}

//------------------------------------------------
// MQTT Message
//------------------------------------------------

void AccessControl_OnMessage(const String &topic,
                             const String &payload)
{
    Debug_Print("Topic : ");
    Debug_Println(topic);

    Debug_Print("Payload : ");
    Debug_Println(payload);

    if (topic != "door/control")
    {
        return;
    }

    if (payload == "OPEN")
    {
        currentState = AccessState::GRANTED;

        LCDUART_SendStatus(LCD_PASS);    // Thêm

        ResetBlink();

        Debug_Println("Access Granted");
    }
    else if (payload == "DENY")
    {
        currentState = AccessState::DENIED;

        LCDUART_SendStatus(LCD_ERROR);   // Thêm

        ResetBlink();

        Debug_Println("Access Denied");
    }
}
