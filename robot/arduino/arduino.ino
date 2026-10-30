#define speedPinR 9         // RIGHT PWM pin connect MODEL-X ENA
#define RightMotorDirPin1 12  // Right Motor direction pin 1 to MODEL-X IN1
#define RightMotorDirPin2 11  // Right Motor direction pin 2 to MODEL-X IN2
#define speedPinL 6         // Left PWM pin connect MODEL-X ENB
#define LeftMotorDirPin1 7    // Left Motor direction pin 1 to MODEL-X IN3
#define LeftMotorDirPin2 8    // Left Motor direction pin 1 to MODEL-X IN4

// Ultrasonic Sensor Pins
#define TrigPin A0  // Trigger pin
#define EchoPin A1  // Echo pin

// Buzzer Pin on Digital Pin 4
#define BuzzerPin 4

// LED Pin (Pin 13 for built-in or external LED)
#define LedPin 13

// State & Speed tracking variables
bool isMovingForward = false;
int carSpeed = 200;                 // Default speed
unsigned long lastPrintTime = 0;
const unsigned long printInterval = 500; // Print telemetry every 500ms

/*motor control*/
void go_Advance(void)  //Forward
{
  digitalWrite(RightMotorDirPin1, HIGH);
  digitalWrite(RightMotorDirPin2, LOW);
  digitalWrite(LeftMotorDirPin1, HIGH);
  digitalWrite(LeftMotorDirPin2, LOW);
  analogWrite(speedPinL, carSpeed);
  analogWrite(speedPinR, carSpeed);
}
void go_Left(int t=0)  //Turn left
{
  digitalWrite(RightMotorDirPin1, HIGH);
  digitalWrite(RightMotorDirPin2, LOW);
  digitalWrite(LeftMotorDirPin1, LOW);
  digitalWrite(LeftMotorDirPin2, HIGH);
  analogWrite(speedPinL, carSpeed);
  analogWrite(speedPinR, carSpeed);
  delay(t);
}
void go_Right(int t=0)  //Turn right
{
  digitalWrite(RightMotorDirPin1, LOW);
  digitalWrite(RightMotorDirPin2, HIGH);
  digitalWrite(LeftMotorDirPin1, HIGH);
  digitalWrite(LeftMotorDirPin2, LOW);
  analogWrite(speedPinL, carSpeed);
  analogWrite(speedPinR, carSpeed);
  delay(t);
}
void go_Back(int t=0)  //Reverse
{
  digitalWrite(RightMotorDirPin1, LOW);
  digitalWrite(RightMotorDirPin2, HIGH);
  digitalWrite(LeftMotorDirPin1, LOW);
  digitalWrite(LeftMotorDirPin2, HIGH);
  analogWrite(speedPinL, carSpeed);
  analogWrite(speedPinR, carSpeed);
  delay(t);
}
void stop_Stop()    //Stop
{
  digitalWrite(RightMotorDirPin1, LOW);
  digitalWrite(RightMotorDirPin2, LOW);
  digitalWrite(LeftMotorDirPin1, LOW);
  digitalWrite(LeftMotorDirPin2, LOW);
}

/* Set motor speed */
void set_Motorspeed(int speed_L, int speed_R)
{
  analogWrite(speedPinL, speed_L);
  analogWrite(speedPinR, speed_R);
}

/* Measure distance in centimeters */
int getDistance()
{
  digitalWrite(TrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(TrigPin, LOW);

  long duration = pulseIn(EchoPin, HIGH, 30000); // Timeout after 30ms (~5 meters)
  if (duration == 0) return 500; // Return max range if no echo received

  int distance = duration * 0.034 / 2; // Calculate distance in cm
  return distance;
}

/* Activate active buzzer and LED together */
void activate_buzzer(int durationMs)
{
  digitalWrite(BuzzerPin, HIGH);
  digitalWrite(LedPin, HIGH);   // Turn LED ON
  Serial.println("Buzzer & LED ON");

  delay(durationMs);

  digitalWrite(BuzzerPin, LOW);
  digitalWrite(LedPin, LOW);    // Turn LED OFF
  Serial.println("Buzzer & LED OFF");
}

// Pins initialize
void init_GPIO()
{
  pinMode(RightMotorDirPin1, OUTPUT);
  pinMode(RightMotorDirPin2, OUTPUT);
  pinMode(speedPinL, OUTPUT);

  pinMode(LeftMotorDirPin1, OUTPUT);
  pinMode(LeftMotorDirPin2, OUTPUT);
  pinMode(speedPinR, OUTPUT);

  pinMode(TrigPin, OUTPUT);
  pinMode(EchoPin, INPUT);

  // Initialize Buzzer and LED Pins
  pinMode(BuzzerPin, OUTPUT);
  digitalWrite(BuzzerPin, LOW);

  pinMode(LedPin, OUTPUT);
  digitalWrite(LedPin, LOW);

  stop_Stop();
}

void setup()
{
  init_GPIO();
  Serial.begin(9600);
  stop_Stop();
}

void loop()
{
  // Safety check when moving forward automatically
  if (isMovingForward) {
    if (getDistance() < 20) {
      stop_Stop();
      isMovingForward = false;
      Serial.println("Obstacle encountered while moving! Emergency stop.");
    }
  }

  // Continuous telemetry output (every 500ms)
  unsigned long currentMillis = millis();
  if (currentMillis - lastPrintTime >= printInterval) {
    lastPrintTime = currentMillis;
    int currentDistance = getDistance();

    Serial.print("Current Speed (PWM): ");
    Serial.print(carSpeed);
    Serial.print(" | Distance: ");
    Serial.print(currentDistance);
    Serial.println(" cm");
  }

  // Handle Serial Commands
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == 'F') {
      if (getDistance() > 20) {
        go_Advance();
        isMovingForward = true;
      } else {
        stop_Stop();
        isMovingForward = false;
        Serial.println("Obstacle in the way");
      }
    }
    else if (command == 'B') { go_Back(); isMovingForward = false; }
    else if (command == 'L') { go_Left(); isMovingForward = false; }
    else if (command == 'R') { go_Right(); isMovingForward = false; }
    else if (command == 'S') { stop_Stop(); isMovingForward = false; }

    // Buzzer & LED Command (Type 'V' to trigger)
    else if (command == 'V') {
      activate_buzzer(500);
    }

    // Speed level commands (1 to 3)
    else if (command == '1') {
      carSpeed = 100; // Level 1 (Slow)
      Serial.println("-> Speed changed to Level 1 (PWM: 100)");
    }
    else if (command == '2') {
      carSpeed = 175; // Level 2 (Medium)
      Serial.println("-> Speed changed to Level 2 (PWM: 175)");
    }
    else if (command == '3') {
      carSpeed = 250; // Level 3 (High)
      Serial.println("-> Speed changed to Level 3 (PWM: 250)");
    }

    else if (command == 'D') {    // DEBUG manual distance measure
      int currentDistance = getDistance();
      Serial.print("Manual Check - Distance: ");
      Serial.print(currentDistance);
      Serial.println(" cm");
      if (currentDistance < 20) {
        Serial.println("Obstacle in the way");
      }
    }
  }
}
