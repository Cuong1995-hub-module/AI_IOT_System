#include "debug.h"

#define DEBUG_TX 17
#define DEBUG_RX 18

HardwareSerial DebugSerial(1);

void Debug_Init()
{
    DebugSerial.begin(115200, SERIAL_8N1, DEBUG_RX, DEBUG_TX);
}

void Debug_Print(const String &msg)
{
    DebugSerial.print(msg);
}

// Thêm hàm này
void Debug_Println()
{
    DebugSerial.println();
}

void Debug_Println(const String &msg)
{
    DebugSerial.println(msg);
}

void Debug_Banner()
{
    Debug_Println();
    Debug_Println("================================");
    Debug_Println(" ESP32 ACCESS CONTROL");
    Debug_Println(" Firmware v1.0");
    Debug_Println("================================");
}