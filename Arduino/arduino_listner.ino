const int IN1 = 8;
const int IN2 = 9;
const int ENA = 5; // PWM pin

void setup() {
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(ENA, OUTPUT);

stopMotor();
    Serial.begin(115200);
}

void loop() {
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();

        if (cmd.startsWith("FWD")) {
            int spd = getSpeed(cmd);
            digitalWrite(IN1, HIGH);
            digitalWrite(IN2, LOW);
            analogWrite(ENA, spd);
        }
        else if (cmd.startsWith("REV")) {
            int spd = getSpeed(cmd);
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, HIGH);
            analogWrite(ENA, spd);
        }
        else if (cmd == "STOP") {
            stopMotor();
        }
    }
}

int getSpeed(String cmd) {
    int i = cmd.indexOf(' ');
    int spd = (i > 0) ? cmd.substring(i + 1).toInt() : 255;
    if (spd < 0) spd = 0;
    if (spd > 255) spd = 255;
    return spd;
}

void stopMotor() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
}