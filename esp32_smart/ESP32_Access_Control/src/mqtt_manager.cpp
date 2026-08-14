#include "mqtt_manager.h"

#include <WiFi.h>
#include <PubSubClient.h>

#include "storage.h"
#include "debug.h"
#include "access_control.h"

static WiFiClient wifiClient;
static PubSubClient mqttClient(wifiClient);

static String host;
static uint16_t port;
static String user;
static String password;


//====================================================
// MQTT Callback
//====================================================
static void MQTT_Callback(char *topic,
                          byte *payload,
                          unsigned int length)
{
    Debug_Print("Topic : ");
    Debug_Println(topic);

    String msg;

    for (unsigned int i = 0; i < length; i++)
    {
        msg += (char)payload[i];
    }

    Debug_Print("Payload : ");
    Debug_Println(msg);

    AccessControl_OnMessage(String(topic), msg);
}
//====================================================
// MQTT Init
//====================================================
void MQTTManager_Init()
{
    if (!Storage_LoadMQTT(host, port, user, password))
    {
        Debug_Println("MQTT Config Not Found");
        return;
    }

    mqttClient.setServer(host.c_str(), port);
    mqttClient.setCallback(MQTT_Callback);

    Debug_Println("MQTT Init OK");

    Debug_Print("HOST : ");
    Debug_Println(host);

    Debug_Print("PORT : ");
    Debug_Println(String(port));

    Debug_Print("USER : ");
    Debug_Println(user);

    Debug_Print("PASS : ");
    Debug_Println(password);
}

//====================================================
// MQTT Connect
//====================================================
bool MQTTManager_Connect()
{
    Debug_Println("========== MQTT ==========");

    Debug_Print("Broker : ");
    Debug_Print(host);

    Debug_Print(":");
    Debug_Println(String(port));

    Debug_Print("WiFi Status : ");
    Debug_Println(String(WiFi.status()));

    // Test TCP
    WiFiClient test;

    if (test.connect(host.c_str(), port))
    {
        Debug_Println("TCP OK");
        test.stop();
    }
    else
    {
        Debug_Println("TCP FAILED");
    }

    Debug_Print("Connecting MQTT... ");

    if (mqttClient.connect("esp32"))
    {
        Debug_Println("OK");

        mqttClient.subscribe("door/control");
        Debug_Println("Subscribe : door/control");

        return true;
    }

    Debug_Print("FAILED, state = ");
    Debug_Println(String(mqttClient.state()));

    return false;
}

//====================================================
// MQTT Status
//====================================================
bool MQTTManager_IsConnected()
{
    return mqttClient.connected();
}

//====================================================
// MQTT Loop
//====================================================
void MQTTManager_Loop()
{
    mqttClient.loop();
}

//====================================================
// MQTT Publish
//====================================================
bool MQTTManager_Publish(const char *topic,
                         const char *payload)
{
    if (!mqttClient.connected())
    {
        Debug_Println("MQTT Not Connected");
        return false;
    }

    bool ok = mqttClient.publish(topic, payload);

    Debug_Print("Publish : ");
    Debug_Print(topic);

    Debug_Print(" -> ");

    Debug_Print(payload);

    Debug_Print(" : ");

    Debug_Println(ok ? "OK" : "FAILED");

    return ok;
}