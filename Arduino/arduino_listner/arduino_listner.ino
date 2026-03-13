const int R_EN = 8;
const int L_EN = 9;
const int RPWM = 5;
const int LPWM = 6;  // must be PWM pin

String input = "";

void setup() {
  // had to redo code since using a new motor controller
  // pinMode(IN1, OUTPUT);
  // pinMode(IN2, OUTPUT);
  // pinMode(RPWM, OUTPUT);
  // pinMode(LED_BUILTIN, OUTPUT);
  // Serial.begin(9600);
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);

  analogWrite(RPWM, 0);
  analogWrite(LPWM, 0);

  delay(1000);
  Serial.begin(9600);

}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      input.trim();
      handleCommand(input);
      input = "";
    } else {
      input += c;
    }
  }
}

void handleCommand(String cmd) {
  digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN)); // debug blink

  if (cmd == "FWD") {
    // digitalWrite(IN1, HIGH);
    // digitalWrite(IN2, LOW);
    // analogWrite(RPWM, 200);
    analogWrite(RPWM, 200);
    analogWrite(LPWM, 0);
  }

  else if (cmd == "REV") {
    // digitalWrite(IN1, LOW);
    // digitalWrite(IN2, HIGH);
    // analogWrite(RPWM, 200);
    analogWrite(RPWM, 0);
    analogWrite(LPWM, 200);
  }

  else if (cmd == "STOP") {
    // analogWrite(RPWM, 0);
    // digitalWrite(IN1, LOW);
    // digitalWrite(IN2, LOW);
    analogWrite(RPWM, 0);
    analogWrite(LPWM, 0);
  }
}

