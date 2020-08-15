#include <Adafruit_Fingerprint.h>
#include <EEPROM.h>
#include <LiquidCrystal.h> 

SoftwareSerial mySerial(8, 9);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);  


int Contrast=10;
const short ADMIN = 2;
const short USER = 1;
const short UNKNOWNUSER = 0;
#define relaypin 7
#define doorinterval 1000



long readFloat(unsigned int addr){
  union{
    byte b[4];
    long f;
  } data;
  for (int i = 0 ; i < 4; i++){
    data.b[i] = EEPROM.read(addr + i);
  }
  return data.f;
}


void writeFloat(unsigned int addr, long x){
  union{
    byte b[4];
    long f;
  } data;
  data.f = x;
  for(int i = 0 ; i < 4 ; i++){
    EEPROM.write(addr + i, data.b[i]);
  }
}



void setup()  
{
  
  analogWrite(6,Contrast);
  lcd.begin(16, 2);
  Serial.begin(9600);
  Serial.print('X');
  pinMode(relaypin, OUTPUT);
  // set the data rate for the sensor serial port
  finger.begin(57600);
  if (finger.verifyPassword()) {
//    Serial.println("Found fingerprint sensor!");
  } else {
//    Serial.print("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }

  EEPROM.write(1,ADMIN);
  EEPROM.write(2,ADMIN);
  EEPROM.put(128,95243055);
  EEPROM.put(132,95243004);

}



void loop(){
      unsigned long startTimer1;
      if(Serial.available()>0){
        char serIn = Serial.read();
        while(serIn == 'L'){
        serIn = 't';
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Admin Mode");
        lcd.setCursor(0,1);
        lcd.print("Please Wait");
        delay(25);
        startTimer1 = millis();
        bool adminLoggedIn = false; 
        while(!adminLoggedIn && millis()-startTimer1 <= 25000){
          adminLoggedIn = checkAdmin();
        } 
        if (adminLoggedIn){
          Serial.print('M');
          char choice ='0';
          while (choice != 'e'){
            Serial.print('o');
            choice = readnumberTimer();
            switch (choice) {
              case 'a' : Serial.print('A');getFingerprintEnroll(); break;
              case 'k' : Serial.print('K');delay(1000);deleteFingerprint();break;
              case 'c' : Serial.print('C');addAdmin();break;
              case 'd' : Serial.print('D');deleteAdmin();break;
              case 'v' : Serial.print('V');sendstids();break;
              case 'e' : Serial.print('l'); break;
              default : Serial.print(choice); break;
            }
          }
          break;
        }
        else {
          serialFlush();
          break;
        }
      }
      }
      uint8_t id = getFingerprintIDez();
      if (id < 128){
        digitalWrite(relaypin, HIGH);
        delay(doorinterval);
        digitalWrite(relaypin, LOW);
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("ID : ");
        lcd.print(id);
        lcd.setCursor(0,1);
        lcd.print("Access Granted!");
        delay(2500);
       }
      else {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Please Put");
        lcd.setCursor(0,1);
        lcd.print("A Valid Finger");
        delay(100);
      }
}




void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}  


uint8_t readnumber(void) {
  //serialFlush();
//  Serial.println("now");
  
  uint8_t num = 0;
  while (num == 0) {
    while (Serial.available() < 1);

    num = Serial.parseInt();
    
//    Serial.print(num);
  }
  return num;
}

//long readnumberlong(void) {
////  serialFlush();
////  Serial.println("now");
//  
//  float num = 0;
//  while (num == 0) {
//    //Serial.println("before");
//    while (Serial.available() >= 4);
//    //Serial.println("after");
//    num = Serial.parseFloat();
////    Serial.print(num);
//  }
//  return num;
//}

char readnumberTimer(void) {
  //serialFlush();
  unsigned long startTimer1;
  char num = '0';
  startTimer1 = millis();
  while (millis()-startTimer1 <= 25000){ 
    if(Serial.available() >= 1){
      num = Serial.read();
      if(num != '0')
        return num;
    }
  }
  return 'e';
  
}

bool checkAdmin(){

  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK)  return false;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK)  return false;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK){
    return false;
  }
  uint8_t readValue = EEPROM.read(finger.fingerID);
  if(readValue == ADMIN){
    //Serial.print("Admin ID: ");
    //Serial.println(finger.fingerID);
    delay(20);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Admin : ");
    lcd.print(finger.fingerID);
    lcd.setCursor(0,1);
    lcd.print("Is Working...");
    return true;
  }
  return false;
}

uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  switch (p) {
    case FINGERPRINT_OK:
      //Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      //Serial.println("No finger detected");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      //Serial.println("Communication error");
      return p;
    case FINGERPRINT_IMAGEFAIL:
      //Serial.println("Imaging error");
      return p;
    default:
      //Serial.println("Unknown error");
      return p;
  }

  // OK success!

  p = finger.image2Tz();
  switch (p) {
    case FINGERPRINT_OK:
      //Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      //Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      //Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      //Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      //Serial.println("Could not find fingerprint features");
      return p;
    default:
      //Serial.println("Unknown error");
      return p;
  }
  
  // OK converted!
  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    //Serial.println("Found a print match!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    //Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_NOTFOUND) {
    //Serial.println("Did not find a match");
    return p;
  } else {
    //Serial.println("Unknown error");
    return p;
  }   
  
  // found a match!
  //Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  //Serial.print(" with confidence of "); Serial.println(finger.confidence); 

  return finger.fingerID;
}

// returns -1 if failed, otherwise returns ID #
int getFingerprintIDez() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK)  return -1;
  
  // found a match!
  //Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  //Serial.print(" with confidence of "); Serial.println(finger.confidence);
  return finger.fingerID; 
}


uint8_t getFingerprintEnroll() {
  int p = -1;
  

  /*for(int i = 1; i < 128 ; i++){
    uint8_t status = EEPROM.read(i);
    if (status == 0){
        Serial.print("First Empty id : ");
        Serial.println(i);
        break;
    }
  }*/
 
//  id = readnumber();
  serialFlush();
  String garbage = Serial.readStringUntil('q');
  String recieve = Serial.readStringUntil('z');
  Serial.print('i');
  int id = -1; 
  long sid;
//  id = recieve.substring(0, recieve.length() - 8).toInt();
  for(int i = 3 ; i < 128 ; i++){
    int val = EEPROM.read(i);
    if(val == UNKNOWNUSER){
      id = i;
      break;
    }
  }
  if(id == -1){
    Serial.print('U');
    return -1;
  }
  sid = recieve.substring(recieve.length() - 8, recieve.length()).toInt();
  if (id == 0) {// ID #0 not allowed, try again!
     return p;
  }
  uint8_t romValue = EEPROM.read(id);
  if(romValue != UNKNOWNUSER){
    Serial.print('Y');
    return p;
  }
  
//  Serial.print('W');
//   serialFlush();
//  delay(100);
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.print('t');
      break;
    case FINGERPRINT_NOFINGER:
      Serial.print('f');
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.print('e');
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.print('e');
      break;
    default:
      Serial.print('e');
      break;
    }
  }

  // OK success!

  p = finger.image2Tz(1);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.print('c');
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.print('e');
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.print('e');
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.print('e');
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.print('e');
      return p;
    default:
      Serial.print('e');
      return p;
  }
  
  Serial.print("r");
  delay(2000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  //Serial.print("ID "); Serial.println(id);
  p = -1;
  //Serial.println("Place same finger again");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.print('t');
      break;
    case FINGERPRINT_NOFINGER:
      Serial.print('f');
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.print('e');
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.print('e');
      break;
    default:
      Serial.print('e');
      break;
    }
  }

  // OK success!

  p = finger.image2Tz(2);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.print('c');
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.print('e');
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.print('e');
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.print('e');
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.print('e');
      return p;
    default:
      Serial.print('e');
      return p;
  }
  
  // OK converted!
  //Serial.print("Creating model for #");  Serial.println(id);
  
  p = finger.createModel();
  if (p == FINGERPRINT_OK) {
    Serial.print('p');
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.print('e');
    return p;
  } else if (p == FINGERPRINT_ENROLLMISMATCH) {
    Serial.print('e');
    return p;
  } else {
    Serial.print('e');
    return p;
  }   
  
  //Serial.print("ID "); Serial.println(id);
  serialFlush();
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
//    Serial.print('s');
    EEPROM.write(id,USER);
    String d = String(id);
    String se = 'p' + d + 'h';
    lcd.clear();
    lcd.print(se);
//    Serial.print('p');
//    Serial.print(id);
//    Serial.print('h');
    Serial.println(se);
    EEPROM.put(128 +(id -1)*4, sid);
    delay(100);
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.print('e');
    return p;
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.print('e');
    return p;
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.print('e');
    return p;
  } else {
    Serial.print('e');
    return p;
  }   
}

void addAdmin(){
  uint8_t id = readnumber();
  Serial.print('i');
  uint8_t romValue = EEPROM.read(id);
  if (romValue == ADMIN){
    Serial.print('X');
  }
  else if (romValue == USER){
    EEPROM.write(id, ADMIN);
    Serial.print('s');
  }
  else{
    Serial.print('e');
  }
}

uint8_t deleteFingerprint() {
  uint8_t id = readnumber();
  Serial.print('i');
  lcd.clear();
  lcd.print('i');
  uint8_t p = -1;
  uint8_t romValue = EEPROM.read(id);
  if(romValue == USER){
    p = finger.deleteModel(id);
  
    if (p == FINGERPRINT_OK) {
      Serial.print('d');
      EEPROM.write(id,UNKNOWNUSER);
      long zer = 0;
      EEPROM.put(128 + (id -1)*4, zer);
    } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
      Serial.print('e');
      return p;
    } else if (p == FINGERPRINT_BADLOCATION) {
      Serial.print('e');
      return p;
    } else if (p == FINGERPRINT_FLASHERR) {
      Serial.print('e');
      return p;
    } else {
      Serial.print('e');
      return p;
    }    
  } 
  else if(romValue == ADMIN){
    Serial.print('X');
  }
  else{
    Serial.println('e');
  }
}

void deleteAdmin(){
    uint8_t id = readnumber();
    Serial.print('i');
    uint8_t isAdmin = EEPROM.read(id);
    if (id == 1 || id == 2){
      lcd.clear();
      lcd.setCursor(0,0);
      long sid;
      EEPROM.get((id-1)*4+128,sid);
      lcd.print(sid);
      Serial.print('X');
      return;
    }
    if(isAdmin == ADMIN){
      EEPROM.write(id,USER);
      Serial.print('s');
      lcd.clear();
      return;
    }
    else{
      Serial.print('e');
      return;
    }
}



void sendstids(){
   long value;
  for(int i = 128; i <= 632; i += 4){
    EEPROM.get(i, value);
    Serial.println(value);
  }
//  Serial.print('h');
    serialFlush();
}
