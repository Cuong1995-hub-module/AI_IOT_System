#include <Arduino.h>

#include "led.h"
#include "debug.h"
#include "storage.h"
#include "web_config.h"
#include "wifi_manager.h"
#include "mqtt_manager.h"
#include "access_control.h"
#include "rfid.h"
#include "lcd_uart.h"

void setup()
{
    Debug_Init();

    LED_Init();

    // Khởi tạo UART trước khi AccessControl gửi READY
    LCDUART_Init();

    AccessControl_Init();

    RFID_Init();

    Storage_Init();

    WiFiManager_StartAP();

    WebConfig_Start();

    if (WiFiManager_Connect())
    {
        Debug_Println("WiFi Connected");

        MQTTManager_Init();

        if (MQTTManager_Connect())
        {
            Debug_Println("MQTT Connected");

            MQTTManager_Publish(
                "esp32/test",
                "Hello From ESP32");
        }
        else
        {
            Debug_Println("MQTT Failed");
        }
    }
    else
    {
        Debug_Println("WiFi Failed");
    }
}

void loop()
{
    WebConfig_Loop();

    // Tự reconnect MQTT
    if (!MQTTManager_IsConnected())
    {
        MQTTManager_Connect();
    }

    MQTTManager_Loop();

    String uid;

    if (RFID_ReadUID(uid))
    {
        Debug_Print("UID : ");
        Debug_Println(uid);

        AccessControl_OnRFID(uid);
    }

    AccessControl_Loop();
}