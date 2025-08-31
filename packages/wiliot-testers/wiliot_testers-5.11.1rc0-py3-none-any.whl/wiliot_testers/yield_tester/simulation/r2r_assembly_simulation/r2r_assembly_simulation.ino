#include <avr/wdt.h>
#define PULL_UP_GPIO 11
#define PULL_DOWN_GPIO 12
#define LED_GPIO 13
#define PULSE_TIME 50  //ms

int time_list_sec[] = {40, 20};
int x = 0;
String idn = "Williot R2R Assembly Simulation 1.0";

void setup() {
    Serial.begin(1000000);  // Start the Serial monitor with speed of 9600 Bauds
    Serial.setTimeout(10);
    Serial.println(idn);

    pinMode(PULL_UP_GPIO,OUTPUT);
    pinMode(PULL_DOWN_GPIO,OUTPUT);
    pinMode(LED_GPIO,OUTPUT);
    
    digitalWrite(LED_GPIO, LOW);
    digitalWrite(PULL_DOWN_GPIO, HIGH);
    digitalWrite(PULL_UP_GPIO, LOW);
    

}

void pulseOut(void)
{
   digitalWrite(PULL_UP_GPIO, HIGH);
   digitalWrite(PULL_DOWN_GPIO, LOW);
   digitalWrite(LED_GPIO, HIGH);
   delay(PULSE_TIME);
   digitalWrite(PULL_UP_GPIO, LOW);
   digitalWrite(PULL_DOWN_GPIO, HIGH);
   digitalWrite(LED_GPIO, LOW);
}

void loop() {
    delay(time_list_sec[x % 2] * 1000);
    pulseOut();
    Serial.println("Sent Trigger");
    x++;
}
