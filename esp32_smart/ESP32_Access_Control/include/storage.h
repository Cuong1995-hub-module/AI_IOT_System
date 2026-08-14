#ifndef STORAGE_H
#define STORAGE_H

#include <Arduino.h>

void Storage_Init();

//================ WIFI =================

void Storage_SaveWiFi(const String &ssid,
                      const String &password);

bool Storage_LoadWiFi(String &ssid,
                      String &password);

//================ MQTT =================

void Storage_SaveMQTT(const String &host,
                      uint16_t port,
                      const String &user,
                      const String &password);

bool Storage_LoadMQTT(String &host,
                      uint16_t &port,
                      String &user,
                      String &password);

#endif