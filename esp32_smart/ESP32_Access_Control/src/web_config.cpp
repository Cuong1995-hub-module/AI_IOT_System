#include "web_config.h"

#include <WebServer.h>
#include "wifi_manager.h"
#include "debug.h"
#include "storage.h"
#include "mqtt_manager.h"

WebServer server(80);

void WebConfig_Start()
{
    server.on("/", HTTP_GET, []()
    {
        String html;

        html += "<!DOCTYPE html>";
        html += "<html>";
        html += "<head>";
        html += "<meta charset='UTF-8'>";
        html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
        html += "<title>ESP32 Access Control</title>";

        html += "<style>";
        html += "body{font-family:Arial,sans-serif;"
                "max-width:500px;"
                "margin:20px auto;"
                "padding:20px;"
                "font-size:22px;"
                "background:#f5f5f5;}";

        html += "h2{text-align:center;font-size:34px;color:#1976D2;}";

        html += "h3{color:#1976D2;}";

        html += "label{font-weight:bold;}";

        html += "input{"
                "width:100%;"
                "padding:15px;"
                "font-size:22px;"
                "margin-top:8px;"
                "margin-bottom:20px;"
                "border-radius:8px;"
                "border:1px solid #999;"
                "box-sizing:border-box;"
                "}";

        html += "input[type=submit]{"
                "background:#1976D2;"
                "color:white;"
                "font-weight:bold;"
                "border:none;"
                "cursor:pointer;"
                "}";

        html += "</style>";

        html += "</head>";

        html += "<body>";

        html += "<h2>ESP32 ACCESS CONTROL</h2>";

        html += "<form action='/save' method='POST'>";

        // ==========================
        // WiFi
        // ==========================

        html += "<h3>WiFi</h3>";

        html += "<label>SSID</label>";
        html += "<input type='text' name='ssid'>";

        html += "<label>Password</label>";
        html += "<input type='password' name='password'>";

        html += "<hr>";

        // ==========================
        // MQTT
        // ==========================

        html += "<h3>MQTT</h3>";

        html += "<label>Host</label>";
        html += "<input type='text' name='host' value='192.168.1.29'>";

        html += "<label>Port</label>";
        html += "<input type='number' name='port' value='1883'>";

        html += "<label>User</label>";
        html += "<input type='text' name='user'>";

        html += "<label>Password</label>";
        html += "<input type='password' name='mqtt_password'>";

        html += "<input type='submit' value='SAVE'>";

        html += "</form>";

        html += "</body>";
        html += "</html>";

        server.send(200, "text/html", html);
    });

    server.on("/save", HTTP_POST, []()
    {
        String ssid = server.arg("ssid");
        String wifiPassword = server.arg("password");

        String host = server.arg("host");
        uint16_t port = server.arg("port").toInt();
        String user = server.arg("user");
        String mqttPassword = server.arg("mqtt_password");

        Debug_Println("");
        Debug_Println("===== WIFI =====");

        Debug_Print("SSID : ");
        Debug_Println(ssid);

        Debug_Print("PASS : ");
        Debug_Println(wifiPassword);

        Debug_Println("");

        Debug_Println("===== MQTT =====");

        Debug_Print("HOST : ");
        Debug_Println(host);

        Debug_Print("PORT : ");
        Debug_Println(String(port));

        Debug_Print("USER : ");
        Debug_Println(user);

        Debug_Print("PASS : ");
        Debug_Println(mqttPassword);

        Storage_SaveWiFi(ssid, wifiPassword);
        Storage_SaveMQTT(host, port, user, mqttPassword);

        Debug_Println("");
    Debug_Println("===== TEST WIFI =====");

if (WiFiManager_Connect())
{
    Debug_Println("WiFi Test OK");

    MQTTManager_Init();

    if (MQTTManager_Connect())
    {
        Debug_Println("MQTT Test OK");
    }
    else
    {
        Debug_Println("MQTT Test FAILED");
    }
}
else
{
    Debug_Println("WiFi Test FAILED");
}

        server.send(
            200,
            "text/html",
            "<h2>Configuration Saved</h2>"
            "<p>ESP32 is restarting...</p>");

        //delay(1000);

        //ESP.restart();
    });

    server.begin();

    Debug_Println("Web Server Started");
}

void WebConfig_Loop()
{
    server.handleClient();
}