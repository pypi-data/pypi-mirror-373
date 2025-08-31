//**Global variables**

int led = 13; // Pin for the LED
int timer = 250; // Delay time in milliseconds


//**Functions**

// No functions defined


//**Setup**

void setup() {
	pinMode(led, OUTPUT); // Set the LED pin as output
	Serial.begin(115200);
}


//**Loop**

void loop() {
	digitalWrite(led, HIGH); delay(timer);
digitalWrite(led, LOW);  delay(timer);
	Serial.write("Hello!");
}

