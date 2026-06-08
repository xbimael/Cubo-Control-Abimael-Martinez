// =========================================================================
// LIBRERÍAS Y CONFIGURACIÓN DE PINES
// =========================================================================
#include <util/atomic.h>
#include <SoftwareSerial.h>

#define ENCA 2
#define ENCB 3
#define e1 11
#define m1 10
#define en 12

// =========================================================================
// PARÁMETROS DEL MOTOR Y VARIABLES GLOBALES
// =========================================================================
float gearbox = 210.0;
float ppv = 64.0; // Se divide entre 4 porque el encoder es de cuadratura, pero solo se lee un pulso de subida
float ppv2rad = 6.2832 / (gearbox * ppv);

// Variables volátiles para interrupciones
volatile long pos_i = 0;
int lastState = 0;

// =========================================================================
// CONFIGURACIÓN INICIAL (SETUP)
// =========================================================================
void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  
  pinMode(ENCA, INPUT);
  pinMode(ENCB, INPUT);
  pinMode(e1, OUTPUT);
  pinMode(m1, OUTPUT);
  pinMode(en, OUTPUT);
  
  Serial1.flush();
  Serial.println("Cleaning serial buffer and wainting for connection... \n");
  Serial.println("Waiting data...");
  delay(500);
  
  attachInterrupt(digitalPinToInterrupt(ENCA), readPosition, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCB), readPosition, CHANGE);
  
  // Conexión con MATLAB / Frontend
  int connectionState = 0;
  while (connectionState == 0) {
    if (Serial1.available()) {
      Serial.println("Serial1 available");
      connectionState = Serial1.parseFloat();
      Serial.println(connectionState);
    }
  }
  delay(1000);
  Serial1.println(1);
  Serial.println("Connected");
  
  runMotor(1, 0, e1, m1, en);
  delay(1000);
}

// =========================================================================
// BUCLE PRINCIPAL (LOOP)
// =========================================================================
void loop() {
  pos_i = 0;

  // Selección del Modo de Operación
  int operatingMode = 0;
  if (Serial1.available()) {
    operatingMode = Serial1.parseFloat();
  }
  
  // OperatingMode=1: Motor Warm up
  if (operatingMode == 1) {
    Op1_WarmUp();
  }
  // OperatingMode=2: Open loop mode
  if (operatingMode == 2) {
    Op2_OpenLoop();      
  }
  // OperatingMode=3: Velocity control (actions)
  if (operatingMode == 3) {
    Op3_VelocityControlAction();
  }
  // OperatingMode=4: Velocity control (zeros/poles)
  if (operatingMode == 4) {
    Op4_VelocityControlZP();
  }
  // OperatingMode=5: Position control (actions)
  if (operatingMode == 5) {
    Op5_PositionControlAction();
  }
  // OperatingMode=6: Position control (zeros/poles)
  if (operatingMode == 6) {
    Op6_PositionControlZP();  
  }
}

// =========================================================================
// FUNCIONES DE CONTROL DE HARDWARE
// =========================================================================

void runMotor(int dir, int u_out, int pin_e, int pin_m, int pin_en) {
  analogWrite(pin_en, u_out);
  if (dir == 1) {
    digitalWrite(pin_e, HIGH);
    digitalWrite(pin_m, LOW);
  } else if (dir == -1) {
    digitalWrite(pin_e, LOW);
    digitalWrite(pin_m, HIGH);
  } else {
    analogWrite(pin_en, 0);
  }
}

void ScaleAndRun(float u) {
  int dir = -1;
  if (u < 0) {
    dir = 1;
  }
  int pwr = (int)fabs(u) * 255 / 12;
  if (pwr > 255) {
    pwr = 255;
  }
  runMotor(dir, pwr, e1, m1, en);
}

void readPosition() {
  int valA = digitalRead(ENCA);
  int valB = digitalRead(ENCB);
  
  int currentState = (valA << 1) | valB;
  
  if (lastState != currentState) {
    if ((lastState == 0 && currentState == 1) || 
        (lastState == 1 && currentState == 3) || 
        (lastState == 3 && currentState == 2) || 
        (lastState == 2 && currentState == 0)) {
      pos_i++;
    } else {
      pos_i--;
    }
    lastState = currentState;
  }
}

// =========================================================================
// MODOS DE OPERACIÓN (OP1 - OP6)
// =========================================================================

void Op1_WarmUp() {
  Serial.println("Operating Mode= Motor warm up");
  if (Serial1.available()) {
    int tsim = Serial1.parseFloat();
    Serial.print("Warm up time:");
    Serial.println(tsim);
    
    runMotor(1, 255, e1, m1, en);
    delay(tsim * 1000);
    runMotor(1, 0, e1, m1, en);
    
    Serial1.println(1);  // Warm up flag
    Serial.println("Experiment finished");
  }
}

void Op2_OpenLoop() {
  Serial.println("Operating Mode= identificacion");
  if (Serial1.available()) {
    Serial.println("Serial1 available");
    float u = Serial1.parseFloat();
    float tsim = Serial1.parseFloat();
    long tsam = Serial1.parseFloat();
    delay(200);
    ScaleAndRun(u);

    long t1 = micros(); 
    long t2 = micros();
    int pos = 0, pos0 = 0;
    float velocity_prev = 0;
    
    while ((float)(t2 - t1) / 1.0e6 < (tsim + 0.1)) {
      pos0 = pos;
      float pos0Rad = float(pos0) * ppv2rad;
      
      long deltaT = micros() - t2;
      while (deltaT < tsam) {
        deltaT = micros() - t2;
      }
      t2 = t2 + deltaT;
      
      ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        pos = pos_i;               
      }
      
      float posRad = float(pos) * ppv2rad;
      float deltaTs = float(deltaT) / (1000000.0);
      float deltaPosRad = posRad - pos0Rad;
      float velocity1 = deltaPosRad / deltaTs;
      
      // --- FILTRO DE SEGURIDAD ---
      if (abs(velocity1) > 1000.0) { 
        velocity1 = velocity_prev; 
      } else {
        velocity_prev = velocity1;
      }
                           
      float timeFer = float(double(t2 - t1) * 0.000001);
      Serial1.println(velocity1);
      Serial1.println(timeFer, 4);
      Serial1.println(u);
    }
    runMotor(1, 0, e1, m1, en);
    Serial.println("Experiment finished");
  }
}

void Op3_VelocityControlAction() {
  Serial.println("Operating Mode: Velocity control (actions)");
  if (Serial1.available()) {
    Serial.println("Serial1 available");
    int isDigital = Serial1.parseInt(); 
    float vt   = Serial1.parseFloat();
    float tsim = Serial1.parseFloat();
    long  tsam = Serial1.parseFloat();
    float kp   = Serial1.parseFloat();
    float ki   = Serial1.parseFloat();
    float kd   = Serial1.parseFloat();
    delay(20);

    float pos = 0; float pos0 = 0;
    float velocity1 = 0, velocity2 = 0;
    float velocity_prev = 0;
    float error = 0; float Ierror = 0;
    
    long t1 = micros();
    long t2 = micros();
    long deltaT = micros() - t2;
      
    while ((float)(t2 - t1) / 1.0e6 < (tsim + 0.1)) {
      pos0 = pos;
      velocity2 = velocity1;
      float pos0Rad = float(pos0) * ppv2rad;
      
      while (deltaT < tsam) {
        deltaT = micros() - t2;
      }
      t2 = t2 + deltaT;
      
      ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        pos = pos_i;
      }
      
      float posRad = float(pos) * ppv2rad;
      float deltaTs = float(deltaT) / (1000000.0);
      float deltaPosRad = posRad - pos0Rad;
      velocity1 = deltaPosRad / deltaTs;

      // --- FILTRO DE SEGURIDAD ---
      if (abs(velocity1) > 1000.0) { 
        velocity1 = velocity_prev; 
      } else {
        velocity_prev = velocity1;
      }

      float deltaVelRad = (velocity1 - velocity2) / deltaTs;                    
      error = vt - velocity1;
      float Derror = deltaVelRad / deltaTs;
      Ierror = Ierror + error * deltaTs;
        
      float usc = (kp * error + kd * Derror + ki * Ierror);
      ScaleAndRun(usc);

      Serial1.println(velocity1, 4);
      Serial1.println(float(double(t2 - t1) * 0.000001), 4);
      Serial1.println(usc);
      deltaT = 0;
    }
  }
  Serial.println("Experiment finished");
  runMotor(1, 0, e1, m1, en);
}

void Op4_VelocityControlZP() {
  Serial.println("Operating Mode: Regulador Real de Velocidad");
  if (Serial1.available()) {
    int   isDigital = Serial1.parseInt();
    float vt        = Serial1.parseFloat();
    float tsim      = Serial1.parseFloat();
    long  tsam      = Serial1.parseFloat();
    float k         = Serial1.parseFloat();
    float c         = Serial1.parseFloat();
    float p         = Serial1.parseFloat();
    float c_i       = Serial1.parseFloat();
    float p_i       = Serial1.parseFloat();
    delay(20);

    int   pos = 0, pos0 = 0;
    float velocity_prev = 0;
    float error2 = 0, error1 = 0, error0 = 0;
    float u2 = 0, u1 = 0, u0 = 0;

    long t1 = micros();
    long t2 = micros();
    float T = float(tsam) / 1000000.0;

    // --- Cálculo de coeficientes (fuera del bucle) ---
    float b_2, b_1, b_0, a_1, a_0;

    if (isDigital == 0) {
      float g  = 2.0 / T;
      float g2 = g * g;

      if (fabsf(c_i) < 1e-4 && fabsf(p_i) < 1e-4) {
        float num2 = k * (g + c);
        float num0 = k * (c - g);
        float den2 = (g + p);
        float den0 = (p - g);

        b_2 = num2 / den2;
        b_1 = num0 / den2;   
        b_0 = 0.0;
        a_1 = den0 / den2;
        a_0 = 0.0;
      }
      else {
        float num2 = k * (g2 + g * (c + c_i) + (c * c_i));
        float num1 = k * (2 * (c * c_i) - 2 * g2);
        float num0 = k * (g2 - g * (c + c_i) + (c * c_i));

        float den2 = g2 + g * (p + p_i) + (p * p_i);
        float den1 = 2 * (p * p_i) - 2 * g2;
        float den0 = g2 - g * (p + p_i) + (p * p_i);

        a_1 = den1 / den2;
        a_0 = den0 / den2;
        b_2 = num2 / den2;
        b_1 = num1 / den2;
        b_0 = num0 / den2;
      }
    }
    else {
      b_2 = k;  
      b_1 = k * (-c - c_i);  
      b_0 = k * (c * c_i);
      a_1 = -p - p_i;   
      a_0 = p * p_i;
    }

    // --- Bucle de control ---
    long deltaT = 0;
    while ((float)(t2 - t1) / 1.0e6 < (tsim + 0.1)) {
      pos0 = pos;
      float pos0Rad = float(pos0) * ppv2rad;

      while (deltaT < tsam) {
        deltaT = micros() - t2;
      }
      t2 = t2 + deltaT;

      ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        pos = pos_i;
      }

      float posRad      = float(pos) * ppv2rad;
      float deltaTs     = float(deltaT) / 1000000.0;
      float deltaPosRad = posRad - pos0Rad;
      float velocity1   = deltaPosRad / deltaTs;

      // --- FILTRO DE SEGURIDAD ---
      if (abs(velocity1) > 1000.0) { 
        velocity1 = velocity_prev; 
      } else {
        velocity_prev = velocity1;
      }

      error2 = vt - velocity1;
      u2 = ((b_2 * error2 + b_1 * error1 + b_0 * error0) - a_1 * u1 - a_0 * u0);
      
      if (u2 >  255) u2 =  255;
      if (u2 < -255) u2 = -255;

      ScaleAndRun(u2);

      Serial1.println(velocity1, 4);
      Serial1.println(float(double(t2 - t1) * 1.0e-6), 4);
      Serial1.println(u2);

      error0 = error1; error1 = error2;
      u0 = u1;         u1 = u2;
      deltaT = 0;
    }
  }
  runMotor(1, 0, e1, m1, en);
  Serial.println("Experiment finished");
}

void Op5_PositionControlAction() {
  Serial.println("Operating Mode: Position control (actions)");
  if (Serial1.available()) {
    Serial.println("Serial1 available");
    int isDigital = Serial1.parseInt(); 
    float pt   = Serial1.parseFloat();
    float tsim = Serial1.parseFloat();
    long  tsam = Serial1.parseFloat();
    float kp   = Serial1.parseFloat();
    float ki   = Serial1.parseFloat();
    float kd   = Serial1.parseFloat();
    delay(20);
    
    float pos = 0; float pos0 = 0;
    float error = 0; float Ierror = 0; float Derror = 0;
    long t1 = micros();
    long t2 = micros();
      
    long deltaT = micros() - t2;
    while ((float)(t2 - t1) / 1.0e6 < (tsim + 0.1)) {
      pos0 = pos;
      float pos0Rad = float(pos0) * ppv2rad;
      while (deltaT < tsam){
        deltaT = micros() - t2;
      }
      t2 = t2 + deltaT;
        
      ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        pos = pos_i;
      }
      float posRad = float(pos) * ppv2rad;
      float deltaTs = float(deltaT) / (1000000.0);
      float deltaPosRad = posRad - pos0Rad;
        
      error = pt - posRad;
      Derror = -deltaPosRad / deltaTs;
      Ierror = Ierror + error * deltaTs;

      float usc = (kp * error + kd * Derror + ki * Ierror);
      if (usc > 12)  usc = 12;
      if (usc < -12) usc = -12;
      
      ScaleAndRun(usc);

      Serial1.println(posRad, 4);
      Serial1.println(float(double(t2 - t1) * 0.000001), 4);
      Serial1.println(usc);
      deltaT = 0;
    }
  }
  Serial.println("Experiment finished");
  runMotor(1, 0, e1, m1, en);
}

void Op6_PositionControlZP() {
  Serial.println("Operating mode: Position control (zeros/poles)");
  if (Serial1.available()) {
    int isDigital = Serial1.parseInt(); 
    float pt      = Serial1.parseFloat(); 
    float tsim    = Serial1.parseFloat();
    long  tsam    = Serial1.parseFloat(); 
    float k       = Serial1.parseFloat();
    float c       = Serial1.parseFloat();
    float p       = Serial1.parseFloat();
    float c_i     = Serial1.parseFloat();
    float p_i     = Serial1.parseFloat();
    delay(20);

    float pos = 0; 
    float u2 = 0, u1 = 0, u0 = 0;
    float error2 = 0, error1 = 0, error0 = 0;
    
    long t1 = micros();
    long t2 = micros();
    float T = float(tsam) / 1000000.0; 
    Serial.print("Tiempo de muestreo");
    Serial.print(T);
    
    float b_2, b_1, b_0, a_1, a_0;

    if (isDigital == 0) {
      float g = 2.0 / T;
      float g2 = g * g;

      if (fabsf(c_i) < 1e-4 && fabsf(p_i) < 1e-4) {
        b_2 = k * (g + c) / (g + p);
        b_1 = k * (c - g) / (g + p);
        b_0 = 0.0;
        a_1 = (p - g) / (g + p);
        a_0 = 0.0;
      } 
      else {
        float num2 = k * (g2 + g * (c + c_i) + (c * c_i));
        float num1 = k * (2 * (c * c_i) - 2 * g2);
        float num0 = k * (g2 - g * (c + c_i) + (c * c_i));

        float den2 = g2 + g * (p + p_i) + (p * p_i);
        float den1 = 2 * (p * p_i) - 2 * g2;
        float den0 = g2 - g * (p + p_i) + (p * p_i);

        a_1 = den1 / den2;
        a_0 = den0 / den2;
        b_2 = num2 / den2;
        b_1 = num1 / den2;
        b_0 = num0 / den2;
      }
    } 
    else {
      b_2 = k;  
      b_1 = k * (-c - c_i);  
      b_0 = k * (c * c_i);
      a_1 = -p - p_i;   
      a_0 = p * p_i;
    }

    long deltaT = 0;
    while ((float)(t2 - t1) / 1.0e6 < (tsim + 0.1)) {
      t2 = micros();

      while (deltaT < tsam) {
        deltaT = micros() - t2;
      }
      t2 = t2 + deltaT;

      ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        pos = pos_i;
      }
      
      float posRad = float(pos) * ppv2rad;
      error2 = pt - posRad;
      u2 = ((b_2 * error2 + b_1 * error1 + b_0 * error0) - a_1 * u1 - a_0 * u0);

      if (u2 >  12) u2 =  12;
      if (u2 < -12) u2 = -12;

      ScaleAndRun(u2);

      Serial1.println(posRad, 4);
      Serial1.println(float(double(micros() - t1) * 1.0e-6), 4);
      Serial1.println(u2);

      error0 = error1; error1 = error2;
      u0 = u1; u1 = u2;
      deltaT = 0;
    }
  }
  runMotor(1, 0, e1, m1, en);
  Serial.println("Experiment finished");
}