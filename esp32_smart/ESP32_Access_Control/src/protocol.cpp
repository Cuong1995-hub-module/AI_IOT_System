#include "protocol.h"

String BuildUIDMessage(const String &uid)
{
    return "U:" + uid;
}

String BuildStatusMessage(SystemStatus status)
{
    return "S:" + String((uint8_t)status);
}