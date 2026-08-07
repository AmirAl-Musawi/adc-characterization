const int POTI_PIN = A0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println(analogRead(POTI_PIN));
  delay(300);
}
