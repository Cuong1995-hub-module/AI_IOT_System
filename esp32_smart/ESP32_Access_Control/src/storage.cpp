#include "storage.h"

#include <Preferences.h>

Preferences prefs;

void Storage_Init()
{

}
void Storage_SaveWiFi(const String &ssid,
                      const String &password)
{
    prefs.begin("wifi", false);

    prefs.putString("ssid", ssid);
    prefs.putString("pass", password);

    prefs.end();
}
bool Storage_LoadWiFi(String &ssid,
                      String &password)
{
    prefs.begin("wifi", true);

    ssid = prefs.getString("ssid", "");
    password = prefs.getString("pass", "");

    prefs.end();

    return !ssid.isEmpty();
}
void Storage_SaveMQTT(const String &host,
                      uint16_t port,
                      const String &user,
                      const String &password)
{
    prefs.begin("mqtt", false);

    prefs.putString("host", host);
    prefs.putUShort("port", port);
    prefs.putString("user", user);
    prefs.putString("pass", password);

    prefs.end();
}
bool Storage_LoadMQTT(String &host,
                      uint16_t &port,
                      String &user,
                      String &password)
{
    prefs.begin("mqtt", true);

    host = prefs.getString("host", "");
    port = prefs.getUShort("port", 1883);
    user = prefs.getString("user", "");
    password = prefs.getString("pass", "");

    prefs.end();

    return !host.isEmpty();
}