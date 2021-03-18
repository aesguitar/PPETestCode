byte read_pins[] = {A0, A1, A2, A3};
byte num_pins = 4;

//12 bit resolution over 3.3 volts
//10 mV/degC
const double conv_fact = 3.3/4096.0*100.0;

void setup() {
  Serial.begin(9600);
  analogReadResolution(12);

  byte i = 0;
  for(i; i < num_pins; i++)
  {
    pinMode(read_pins[i], INPUT);
  }

}

/*
 * Format dependencies:
 *    sensor ids should range from 1,...,n
 *    "[sensor id]: [value]\n"
 */

void loop() {
  // put your main code here, to run repeatedly:
  byte i = 0;
  int reading = 0;
  double temp = 0.0;
  String message;
  
  for(i; i < num_pins; i++)
  {
    reading = analogRead(read_pins[i]);
    temp = (double) reading * conv_fact;
    message = String(i+1) + String(": ") + String(temp) + String('\n');
    Serial.print(message);
  }

}
