const int POTI_PIN = A0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  unsigned long t_us = micros();
  int raw = analogRead(POTI_PIN);
  Serial.print(t_us);
  Serial.print(",");
  Serial.println(raw);
}
