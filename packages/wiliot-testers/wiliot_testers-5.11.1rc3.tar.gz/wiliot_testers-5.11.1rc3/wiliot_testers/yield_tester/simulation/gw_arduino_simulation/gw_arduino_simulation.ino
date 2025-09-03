#include <Arduino.h>

bool isRunning = true;
bool printPacket = false;
int TIME_BETWEEN_PACKETS = 25;
String currentPacket;
int count = 0;
unsigned long startTime;

// Function to generate a random hexadecimal string of a fixed length
String generateRandomHex(int length) {
    String randomHex = "";
    for (int i = 0; i < length; i++) {
        int hexValue = random(0, 16);
        if (hexValue < 10) {
            randomHex += char(hexValue + '0'); // Numbers 0-9
        } else {
            randomHex += char(hexValue - 10 + 'A'); // Letters A-F
        }
    }
    return randomHex;
}

// Function to generate the full string with time and packet data
String generateFormattedString() {
    // Calculate the elapsed time in seconds
    float elapsedTime = (millis() - startTime) / 1000.0;

    // Create the packet
    String packet = "04" + generateRandomHex(76) + "23";

    // Create the full formatted string
    String formattedString = "time:";
    formattedString += String(elapsedTime, 6); // Time with 6 decimal places
    formattedString += "process_packet(\"";
    formattedString += packet;
    formattedString += "\")";

    return formattedString;
}

void setup() {
    Serial.begin(921600);
    randomSeed(analogRead(0));
    startTime = millis(); // Initialize the start time
    currentPacket = generateFormattedString(); // Initialize the first packet
    Serial.println(F("Wiliot Yield Simulation"));
}

void loop() {

    if (Serial.available() > 0) {
        String input = Serial.readString();
        if (input == "!version\r\n") {
            Serial.println("WILIOT_GW_BLE_CHIP_SW_VER=4.1.4");
        } else if (input == "!gateway_app\r\n") {
            Serial.println("Command Complete Event");
            delay(500);
            printPacket = true;
        } else if (input == "!reset\r\n") {
            printPacket = false;
        }
        else{
          Serial.println("Command Complete Event");
        }
    }

    if (printPacket) {
        if (count == 0) {
            currentPacket = generateFormattedString();
        }
        Serial.println(currentPacket);
        count = (count + 1) % 3;
        delay(TIME_BETWEEN_PACKETS);
    }
}