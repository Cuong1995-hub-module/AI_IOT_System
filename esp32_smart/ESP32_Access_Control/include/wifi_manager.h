#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>

void WiFiManager_Init();

bool WiFiManager_Connect();

bool WiFiManager_IsConnected();

void WiFiManager_Disconnect();

String WiFiManager_GetIP();

void WiFiManager_StartAP();
void WebConfig_HandleClient();

#endif