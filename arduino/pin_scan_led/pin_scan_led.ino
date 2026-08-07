void setup() {
  Serial.begin(115200);
  for (int p = 2; p <= 13; p++) {
    pinMode(p, OUTPUT);
  }
}

void loop() {
  for (int p = 2; p <= 13; p++) {
    Serial.print("Pin ");
    Serial.println(p);
    digitalWrite(p, HIGH);
    delay(1000);
    digitalWrite(p, LOW);
  }
}