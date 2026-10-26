
#define speedPinR 9    //  RIGHT PWM pin connect MODEL-X ENA
#define RightMotorDirPin1  12    //Right Motor direction pin 1 to MODEL-X IN1 
#define RightMotorDirPin2  11    //Right Motor direction pin 2 to MODEL-X IN2
#define speedPinL 6    // Left PWM pin connect MODEL-X ENB
#define LeftMotorDirPin1  7    //Left Motor direction pin 1 to MODEL-X IN3 
#define LeftMotorDirPin2  8   //Left Motor direction pin 1 to MODEL-X IN4 

// Ultrasonic Sensor Pins
#define TrigPin A0  // Trigger pin is Input for ultrasonic sensor
#define EchoPin A1  // Echo pin is Output for ultrasonic sensor

/*motor control*/
void go_Advance(void)  //Forward
{
  digitalWrite(RightMotorDirPin1, HIGH);
  digitalWrite(RightMotorDirPin2,LOW);
  digitalWrite(LeftMotorDirPin1,HIGH);
  digitalWrite(LeftMotorDirPin2,LOW);
  analogWrite(speedPinL,200);
  analogWrite(speedPinR,200);
}
void go_Left(int t=0)  //Turn left
{
  digitalWrite(RightMotorDirPin1, HIGH);
  digitalWrite(RightMotorDirPin2,LOW);
  digitalWrite(LeftMotorDirPin1,LOW);
  digitalWrite(LeftMotorDirPin2,HIGH);
  analogWrite(speedPinL,200);
  analogWrite(speedPinR,200);
  delay(t);
}
void go_Right(int t=0)  //Turn right
{
  digitalWrite(RightMotorDirPin1, LOW);
  digitalWrite(RightMotorDirPin2,HIGH);
  digitalWrite(LeftMotorDirPin1,HIGH);
  digitalWrite(LeftMotorDirPin2,LOW);
  analogWrite(speedPinL,200);
  analogWrite(speedPinR,200);
  delay(t);
}
void go_Back(int t=0)  //Reverse
{
  digitalWrite(RightMotorDirPin1, LOW);
  digitalWrite(RightMotorDirPin2,HIGH);
  digitalWrite(LeftMotorDirPin1,LOW);
  digitalWrite(LeftMotorDirPin2,HIGH);
  analogWrite(speedPinL,200);
  analogWrite(speedPinR,200);
  delay(t);
}
void stop_Stop()    //Stop
{
  digitalWrite(RightMotorDirPin1, LOW);
  digitalWrite(RightMotorDirPin2,LOW);
  digitalWrite(LeftMotorDirPin1,LOW);
  digitalWrite(LeftMotorDirPin2,LOW);
}
/*set motor speed */
void set_Motorspeed(int speed_L,int speed_R)
{
  analogWrite(speedPinL,speed_L); 
  analogWrite(speedPinR,speed_R);   
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
  
  int distance = duration * 0.034 / 2; // Calculate distance in cm. Speed of sound=340 m/s or 0.034 cm/microseconds.
  return distance;
}

//Pins initialize
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

	stop_Stop();
}

void setup()
{
	init_GPIO();
  Serial.begin(9600);
  stop_Stop();
}

void loop(){
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == 'F') {
      if (getDistance() < 20) {   // Obstacle detected
        go_Advance();
      } else {
        stop_Stop();
        Serial.println("Obstacle in the way! Cannot move forward.");
      }
    } else if (command == 'B') go_Back();
    else if (command == 'L') go_Left();
    else if (command == 'R') go_Right();
    else if (command == 'S') stop_Stop();
    else if (command == 'D') {    // DEBUG for ultrasonic sensor distance measure
      int currentDistance = getDistance();
      Serial.print("Distance: ");
      Serial.print(currentDistance);
      Serial.println(" cm");
    } 
  }
  
  
}
