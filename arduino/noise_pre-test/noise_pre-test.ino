const int POTI_PIN = A5;
const int N = 200;

int werte[N];

void setup() {
  Serial.begin(115200);
  delay(3000);

  Serial.println("Messung laeuft, Poti NICHT anfassen ...");

  for (int i = 0; i < N; i++) {
    werte[i] = analogRead(POTI_PIN);
    delay(5);
  }

  int minWert = 1023;
  int maxWert = 0;
  float summe = 0;

  for (int i = 0; i < N; i++) {
    if (werte[i] < minWert) minWert = werte[i];
    if (werte[i] > maxWert) maxWert = werte[i];
    summe += werte[i];
  }

  float mittelwert = summe / N;

  float quadratsumme = 0;
  for (int i = 0; i < N; i++) {
    float d = werte[i] - mittelwert;
    quadratsumme += d * d;
  }
  float sigma = sqrt(quadratsumme / (N - 1));

  Serial.println();
  Serial.println("=== Ergebnis Rausch-Vorabtest ===");
  Serial.print("Samples:        "); Serial.println(N);
  Serial.print("Minimum:        "); Serial.println(minWert);
  Serial.print("Maximum:        "); Serial.println(maxWert);
  Serial.print("Spannweite:     "); Serial.println(maxWert - minWert);
  Serial.print("Mittelwert:     "); Serial.println(mittelwert, 3);
  Serial.print("Sigma (LSB):    "); Serial.println(sigma, 3);
  Serial.println();
  Serial.println("Wert : Anzahl");

  int verschiedene = 0;
  for (int w = minWert; w <= maxWert; w++) {
    int anzahl = 0;
    for (int i = 0; i < N; i++) {
      if (werte[i] == w) anzahl++;
    }
    if (anzahl > 0) {
      verschiedene++;
      Serial.print(w); Serial.print(" : "); Serial.println(anzahl);
    }
  }

  Serial.print("Verschiedene Werte insgesamt: ");
  Serial.println(verschiedene);
  Serial.println("=== Ende ===");
}

void loop() {
  // leer: die Messung laeuft nur einmal beim Start
}