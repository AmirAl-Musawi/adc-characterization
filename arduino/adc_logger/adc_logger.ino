const int POTI_PIN = A0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  unsigned long t_us = micros();
  int raw = analogRead(POTI_PIN);
  
  char buf[20];
  snprintf(buf, sizeof(buf), "%09lu,%03d", t_us, raw);
  Serial.println(buf);
}
