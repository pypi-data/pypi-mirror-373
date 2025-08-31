//**Global variables**
#include <Arduino.h>


int led = 13; // Pin for the LED
int timer = 1000; // Delay time in milliseconds


//**Functions**

// No functions defined


//**Setup**

void setup() {
	pinMode(led, OUTPUT); // Set the LED pin as output
	Serial.
}


//**Loop**

void loop() {
	digitalWrite(led, HIGH); delay(timer);
	digitalWrite(led, LOW);  delay(timer);
}

