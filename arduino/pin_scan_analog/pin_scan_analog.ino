void setup() {
  Serial.begin(115200);
}

void loop() {
  for (int i = 0; i < 6; i++) {
    Serial.print("A");
    Serial.print(i);
    Serial.print("=");
    Serial.print(analogRead(A0 + i));
    Serial.print("  ");
  }
  Serial.println();
  delay(500);
}