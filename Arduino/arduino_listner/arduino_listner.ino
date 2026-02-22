const int IN1 = 8;
const int IN2 = 9;
const int ENA = 5;  // must be PWM pin

String input = "";

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

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
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 200);
  }

  else if (cmd == "REV") {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, 200);
  }

  else if (cmd == "STOP") {
    analogWrite(ENA, 0);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
  }
}

