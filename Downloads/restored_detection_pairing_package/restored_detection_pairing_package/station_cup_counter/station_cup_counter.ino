#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const String STATION_ID = "A01";

const int pingPin = 7;
const int ledPin = 4;
const int trigPin = 5;
const int echoPin = 6;

const float MOTION_THRESHOLD = 10.0;
const float CUP_INCREMENT = 0.70;
const float MIN_CUP_DROP = 0.50;

const int MEDIAN_SAMPLES = 5;
const int STABLE_READS = 4;
const int CALIBRATION_READS = 10;
const unsigned long ACTIVE_TIMEOUT = 5000;

float BASELINE_EMPTY = 0.0;

float readings[MEDIAN_SAMPLES];
int readIndex = 0;
bool bufferFull = false;
int lastCupCount = 0;
int stableStreak = 0;
int candidateCount = 0;
bool systemActive = false;
bool returnInProgress = false;
unsigned long lastMotionTime = 0;
unsigned long lastReadyPrint = 0;

LiquidCrystal_I2C lcd(0x27, 16, 2);

float getDistance() {
  pinMode(pingPin, OUTPUT);
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  digitalWrite(pingPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(pingPin, LOW);
  pinMode(pingPin, INPUT);
  long duration = pulseIn(pingPin, HIGH);
  return (float)duration / 29.0 / 2.0;
}

float getMotionDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 30000);
  if (duration == 0) return 999.0;
  return (float)duration / 29.0 / 2.0;
}

float getMedian() {
  float sorted[MEDIAN_SAMPLES];
  int count = bufferFull ? MEDIAN_SAMPLES : readIndex;
  if (count == 0) return BASELINE_EMPTY;
  for (int i = 0; i < count; i++) sorted[i] = readings[i];
  for (int i = 0; i < count - 1; i++)
    for (int j = 0; j < count - i - 1; j++)
      if (sorted[j] > sorted[j + 1]) {
        float t = sorted[j]; sorted[j] = sorted[j + 1]; sorted[j + 1] = t;
      }
  return sorted[count / 2];
}

int countCups(float distanceCm) {
  float drop = BASELINE_EMPTY - distanceCm;
  if (drop < MIN_CUP_DROP) return 0;
  if (drop < 4.0) return 1;
  return 1 + max(0, (int)round((drop - 6.91) / CUP_INCREMENT));
}

void updateLCD(int cupCount, bool active) {
  lcd.clear();
  if (!active) {
    lcd.setCursor(0, 0);
    lcd.print("  Cup Counter  ");
    lcd.setCursor(0, 1);
    lcd.print("  Waiting...   ");
  } else {
    lcd.setCursor(0, 0);
    lcd.print("Cups in bin:    ");
    lcd.setCursor(0, 1);
    lcd.print("  >> ");
    lcd.print(cupCount);
    lcd.print(" cup");
    if (cupCount != 1) lcd.print("s");
    lcd.print("     ");
  }
}

void calibrate() {
  Serial.println("--- Calibrating, keep bin empty! ---");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Calibrating...");
  lcd.setCursor(0, 1);
  lcd.print("Keep bin empty!");

  float total = 0;
  for (int i = 0; i < CALIBRATION_READS; i++) {
    total += getDistance();
    delay(100);
  }
  BASELINE_EMPTY = total / CALIBRATION_READS;

  Serial.print("--- Baseline set to: ");
  Serial.print(BASELINE_EMPTY);
  Serial.println(" cm ---");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Baseline:");
  lcd.setCursor(0, 1);
  lcd.print(BASELINE_EMPTY);
  lcd.print(" cm  Ready!");
  delay(2000);
}

void blinkLed(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(ledPin, LOW);
    delay(150);
    digitalWrite(ledPin, HIGH);
    delay(150);
  }
}

void processBorrow(int cups, int boxes) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Dispensing...");
  lcd.setCursor(0, 1);
  lcd.print("Cups: ");
  lcd.print(cups);
  blinkLed(2);
  delay(1000);
  Serial.println("DONE");
  updateLCD(lastCupCount, systemActive);
}

void processReturn(int cups, int boxes) {
  returnInProgress = true;
  systemActive = true;
  digitalWrite(ledPin, HIGH);

  int targetCupCount = lastCupCount + cups;
  unsigned long startTime = millis();
  unsigned long timeoutMs = 25000;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Return cups:");
  lcd.setCursor(0, 1);
  lcd.print("Waiting... 0/");
  lcd.print(cups);

  Serial.print("RETURN_WAIT_CUPS,");
  Serial.println(cups);

  while (millis() - startTime < timeoutMs) {
    float distanceCm = getDistance();
    readings[readIndex] = distanceCm;
    readIndex = (readIndex + 1) % MEDIAN_SAMPLES;
    if (readIndex == 0) bufferFull = true;

    float medianDist = getMedian();
    int newCandidate = countCups(medianDist);

    if (newCandidate == candidateCount) {
      stableStreak++;
    } else {
      candidateCount = newCandidate;
      stableStreak = 1;
    }

    if (stableStreak >= STABLE_READS && candidateCount != lastCupCount) {
      lastCupCount = candidateCount;
      Serial.print("CUP_COUNT,");
      Serial.print(STATION_ID);
      Serial.print(",");
      Serial.println(lastCupCount);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Return cups:");
      lcd.setCursor(0, 1);
      int returned = lastCupCount - (targetCupCount - cups);
      if (returned < 0) returned = 0;
      lcd.print("Got ");
      lcd.print(returned);
      lcd.print("/");
      lcd.print(cups);
    }

    if (cups <= 0 || lastCupCount >= targetCupCount) {
      blinkLed(3);
      delay(500);
      returnInProgress = false;
      Serial.println("DONE");
      updateLCD(lastCupCount, systemActive);
      return;
    }

    delay(100);
  }

  returnInProgress = false;
  Serial.println("ERROR_RETURN_TIMEOUT");
  updateLCD(lastCupCount, systemActive);
}

void processCommand(String cmd) {
  int firstComma = cmd.indexOf(',');
  int secondComma = cmd.indexOf(',', firstComma + 1);

  if (firstComma == -1 || secondComma == -1) {
    Serial.println("ERROR_BAD_FORMAT");
    return;
  }

  String mode = cmd.substring(0, firstComma);
  int cups = cmd.substring(firstComma + 1, secondComma).toInt();
  int boxes = cmd.substring(secondComma + 1).toInt();

  if (mode == "BORROW") { processBorrow(cups, boxes); return; }
  if (mode == "RETURN") { processReturn(cups, boxes); return; }

  Serial.println("ERROR_UNKNOWN_MODE");
}

void setup() {
  Serial.begin(9600);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("  Cup Counter  ");
  lcd.setCursor(0, 1);
  lcd.print("  Starting...  ");
  delay(1000);

  calibrate();
  updateLCD(0, false);

  Serial.print("STATION_READY,");
  Serial.println(STATION_ID);
}

void loop() {
  if (millis() - lastReadyPrint > 3000) {
    Serial.print("STATION_READY,");
    Serial.println(STATION_ID);
    lastReadyPrint = millis();
  }

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    processCommand(cmd);
  }

  float motionDist = getMotionDistance();

  if (motionDist <= MOTION_THRESHOLD) {
    lastMotionTime = millis();
    if (!systemActive) {
      systemActive = true;
      digitalWrite(ledPin, HIGH);
      Serial.println(">>> MOTION DETECTED - System active");
      updateLCD(lastCupCount, true);
    }
  }

  if (systemActive && !returnInProgress && (millis() - lastMotionTime > ACTIVE_TIMEOUT)) {
    systemActive = false;
    digitalWrite(ledPin, LOW);
    Serial.println(">>> No motion - System sleeping");
    updateLCD(lastCupCount, false);
  }

  if (!systemActive) {
    delay(200);
    return;
  }

  float distanceCm = getDistance();
  readings[readIndex] = distanceCm;
  readIndex = (readIndex + 1) % MEDIAN_SAMPLES;
  if (readIndex == 0) bufferFull = true;

  float medianDist = getMedian();
  float drop = BASELINE_EMPTY - medianDist;
  if (drop < 0) drop = 0;

  int newCandidate = countCups(medianDist);

  if (newCandidate == candidateCount) {
    stableStreak++;
  } else {
    candidateCount = newCandidate;
    stableStreak = 1;
  }

  if (stableStreak >= STABLE_READS && candidateCount != lastCupCount) {
    lastCupCount = candidateCount;
    Serial.print("CUP_COUNT,");
    Serial.print(STATION_ID);
    Serial.print(",");
    Serial.println(lastCupCount);
    updateLCD(lastCupCount, true);
  }

  

  delay(200);
}
