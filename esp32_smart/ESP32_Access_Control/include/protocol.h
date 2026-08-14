#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <Arduino.h>

enum SystemStatus
{
    STATUS_ERROR = 0,
    STATUS_PASS,
    STATUS_WAIT
};

String BuildUIDMessage(const String &uid);

String BuildStatusMessage(SystemStatus status);

#endif