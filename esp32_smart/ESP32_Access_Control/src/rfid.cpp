#include "rfid.h"

#include "config.h"
#include "debug.h"

#include <SPI.h>
#include <MFRC522.h>

namespace
{
    MFRC522 mfrc522(RFID_SS_PIN, RFID_RST_PIN);
}

void RFID_Init(void)
{
    SPI.begin(
        RFID_SCK_PIN,
        RFID_MISO_PIN,
        RFID_MOSI_PIN,
        RFID_SS_PIN);

    mfrc522.PCD_Init();

    Debug_Println("RFID Ready");
}

bool RFID_ReadUID(String &uid)
{
    if (!mfrc522.PICC_IsNewCardPresent())
    {
        return false;
    }

    if (!mfrc522.PICC_ReadCardSerial())
    {
        return false;
    }

    uid = "";

    for (byte i = 0; i < mfrc522.uid.size; i++)
    {
        if (mfrc522.uid.uidByte[i] < 0x10)
        {
            uid += "0";
        }

        uid += String(mfrc522.uid.uidByte[i], HEX);
    }

    uid.toUpperCase();

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();

    return true;
}