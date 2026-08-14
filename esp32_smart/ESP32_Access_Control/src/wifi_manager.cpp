#include "wifi_manager.h"

#include <WiFi.h>

#include "storage.h"
#include "debug.h"

bool WiFiManager_Connect()
{
    String ssid;
    String password;

    if (!Storage_LoadWiFi(ssid, password))
    {
        Debug_Println("WiFi Config Not Found");
        return false;
    }

    Debug_Print("Connecting to ");
    Debug_Println(ssid);

    // Chế độ AP + STA
    WiFi.mode(WIFI_AP_STA);

    WiFi.disconnect(true);
    delay(100);

    WiFi.begin(ssid.c_str(), password.c_str());

    unsigned long start = millis();

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Debug_Print(".");

        if (millis() - start >= 10000)
        {
            Debug_Println();
            Debug_Println("WiFi Connect Timeout");
            return false;
        }
    }

    Debug_Println();
    Debug_Println("WiFi Connected");

    Debug_Print("STA IP : ");
    Debug_Println(WiFi.localIP().toString());

    return true;
}

bool WiFiManager_IsConnected()
{
    return WiFi.status() == WL_CONNECTED;
}

void WiFiManager_Disconnect()
{
    WiFi.disconnect(true);
}

String WiFiManager_GetIP()
{
    return WiFi.localIP().toString();
}

void WiFiManager_StartAP()
{
    // Giữ đồng thời AP + STA
    WiFi.mode(WIFI_AP_STA);

    WiFi.softAP("ESP32_ACCESS_CONTROL");

    Debug_Println();
    Debug_Println("===== ACCESS POINT =====");

    Debug_Print("SSID   : ");
    Debug_Println("ESP32_ACCESS_CONTROL");

    Debug_Print("AP IP  : ");
    Debug_Println(WiFi.softAPIP().toString());
}