#ifndef CONFIG_H
#define CONFIG_H

//================ GPIO =================

// RFID
#define RFID_SCK_PIN     12
#define RFID_MISO_PIN    13
#define RFID_MOSI_PIN    11
#define RFID_SS_PIN      10
#define RFID_RST_PIN      9

// LED
#define RED_LED_PIN       4
#define GREEN_LED_PIN     5

// BUZZER
#define BUZZER_PIN        6

// UART
#define UART_TX_PIN      17
#define UART_RX_PIN      18

// I2C (nếu sau này ESP32 dùng)
#define I2C_SDA_PIN       8
#define I2C_SCL_PIN      15


#endif