int last[14];

void setup() {
  Serial.begin(115200);
  for (int p = 2; p <= 13; p++) {
    pinMode(p, INPUT_PULLUP);
    last[p] = HIGH;
  }
}

void loop() {
  for (int p = 2; p <= 13; p++) {
    int v = digitalRead(p);
    if (v != last[p]) {
      Serial.print("Pin ");
      Serial.print(p);
      Serial.println(v == LOW ? " gedrueckt" : " losgelassen");
      last[p] = v;
    }
  }
  delay(20);
}