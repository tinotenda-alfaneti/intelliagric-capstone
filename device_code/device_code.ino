#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <OneWire.h>
#include <DallasTemperature.h>

//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"

#include "config.h"
// Insert your network credentials

#define MOIS_PIN 34 // ESP32 pin GPIO34 (ADC0) that connects to AOUT pin of moisture sensor
#define TEMP_PIN  17

//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;
bool signupOK = false;

float t;

OneWire oneWire(TEMP_PIN);
DallasTemperature DS18B20(&oneWire);
 

void setup(){
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  DS18B20.begin();
  
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Sign up */
  if (Firebase.signUp(&config, &auth, "", "")){
    Serial.println("ok");
    signupOK = true;
  }
  else{
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void loop() {
  
  // put your main code here, to run repeatedly:
  if (Firebase.ready() && signupOK && (millis() - sendDataPrevMillis > 15000 || sendDataPrevMillis == 0)){
    sendDataPrevMillis = millis();
    DS18B20.requestTemperatures();       // send the command to get temperatures
    t = DS18B20.getTempCByIndex(0);  // read temperature in °C
    int m = analogRead(MOIS_PIN); // moisture sensor
    float pH = 7; // soil pH
    String npk = "7-14-7"; // soil NPK
    
    // Write NPK on the database path device/npk
    if (Firebase.RTDB.setString(&fbdo, "device/npk", npk)){
      Serial.println("PASSED");
    }
    else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
    
    // Write temperature on the database path device/temp
    if (Firebase.RTDB.setFloat(&fbdo, "device/temp", t)){
      Serial.println("PASSED");
    }
    else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
     // Write soil moisture on the database path device/mois
    if (Firebase.RTDB.setInt(&fbdo, "device/mois", m)){
      Serial.println("PASSED");
    }
    else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
    // Write soil pH on the database path device/ph
    if (Firebase.RTDB.setInt(&fbdo, "device/ph", pH)){
      Serial.println("PASSED");
    }
    else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
  }

}
