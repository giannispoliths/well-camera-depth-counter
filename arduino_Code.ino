#define ENCODER_A A4
#define ENCODER_B A5

const float WHEEL_CIRCUMFERENCE_MM = 222.1;
const int   PPR = 400;
const float MM_PER_PULSE = WHEEL_CIRCUMFERENCE_MM / (PPR * 4.0);

volatile long pulseCount = 0;
volatile byte lastAB = 0;

const int QEM[16] = {0,-1,1,0, 1,0,0,-1, -1,0,0,1, 0,1,-1,0};

ISR(PCINT1_vect) {
  byte AB = (digitalRead(ENCODER_A) << 1) | digitalRead(ENCODER_B);
  pulseCount += QEM[(lastAB << 2) | AB];
  lastAB = AB;
}

void setup() {
  Serial.begin(9600);
  pinMode(ENCODER_A, INPUT_PULLUP);
  pinMode(ENCODER_B, INPUT_PULLUP);
  PCICR  |= (1 << PCIE1);
  PCMSK1 |= (1 << PCINT12) | (1 << PCINT13);
  lastAB = (digitalRead(ENCODER_A) << 1) | digitalRead(ENCODER_B);
}

void loop() {
  if (Serial.available()) {
    if (Serial.read() == 'R') {
      noInterrupts();
      pulseCount = 0;
      interrupts();
    }
  }

  noInterrupts();
  long count = pulseCount;
  interrupts();

  float depthM = (count * MM_PER_PULSE) / 1000.0;
  Serial.println(depthM, 2);
  delay(200);
}