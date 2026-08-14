#ifndef MQTT_MANAGER_H
#define MQTT_MANAGER_H

#include <Arduino.h>

void MQTTManager_Init();

bool MQTTManager_Connect();

bool MQTTManager_IsConnected();

void MQTTManager_Loop();

bool MQTTManager_Publish(
    const char *topic,
    const char *payload);

#endif