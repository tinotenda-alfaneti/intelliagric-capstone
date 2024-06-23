#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <Preferences.h>
// Provide the token generation process info.
#include "addons/TokenHelper.h"
// Provide the RTDB payload printing info
#include "addons/RTDBHelper.h"

#include "config.h" // Contains WIFI_SSID, WIFI_PASSWORD, API_KEY, DATABASE_URL, and PROJECT_ID

#define MOIS_PIN 34 // ESP32 pin GPIO34 (ADC0) that connects to AOUT pin of moisture sensor
#define TEMP_PIN  17
#define uS_TO_S_FACTOR 1000000ULL  /* Conversion factor for microseconds to seconds */
#define TIME_TO_SLEEP  5            /* Time ESP32 will go to sleep (in seconds) */

RTC_DATA_ATTR String farmerId;

// Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;
bool signupOK = false;

Preferences preferences;

float soilTemp;
int soilMois;
float pH;
String npk;


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
  
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  // Assign the callback function for the long running token generation task
  config.token_status_callback = tokenStatusCallback;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  if (Firebase.authenticated() == true) {
    signupOK = true;
    }

  preferences.begin("config", false); // Open preferences with "config" namespace, RW access
  farmerId = preferences.getString("farmerId", "");
  if (farmerId == "") {
    farmerId = getFarmerId(SERIAL_NUM);
    preferences.putString("farmerId", farmerId);
    if (farmerId != "") {
      Serial.print("Farmer ID: ");
      Serial.println(farmerId);
    } else {
      Serial.println("Failed to get farmer ID");
    }
  } else {
    Serial.println("Failed to get farmer ID");
  }

  // Setup ESP32 to wake up after
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
}

void loop() {

  // Put your main code here, to run repeatedly
  if (Firebase.ready()){
    DS18B20.requestTemperatures();       // Send the command to get temperatures
    soilTemp = DS18B20.getTempCByIndex(0);  // Read temperature in °C
    soilMois = analogRead(MOIS_PIN); // Moisture sensor
    
    pH = 7; // dummy Soil pH
    npk = "7-14-7"; // dummy Soil NPK

    String basePath = "iot/" + farmerId;

    // Write NPK to the database path device/npk
    if (Firebase.RTDB.setString(&fbdo, basePath + "/npk", npk)){
      Serial.println("NPK SENT");
    } else {
      Serial.println("NPK FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    // Write temperature to the database path device/temp
    if (Firebase.RTDB.setFloat(&fbdo, basePath + "/temp", soilTemp)){
      Serial.println("TEMP SENT");
    } else {
      Serial.println("TEMP FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    // Write soil moisture to the database path device/mois
    if (Firebase.RTDB.setInt(&fbdo, basePath + "/mois", soilMois)){
      Serial.println("MOIS SENT");
    } else {
      Serial.println("MOIS FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    // Write soil pH to the database path device/ph
    if (Firebase.RTDB.setInt(&fbdo, basePath + "/ph", pH)){
      Serial.println("PH SENT");
    } else {
      Serial.println("PH FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    // sleep after perfoming routine
    esp_light_sleep_start();
  }
}

String getFarmerId(const char* serialNumber) {

  String documentPath = "iot_devices/" + String(SERIAL_NUM);

  // Fetch the document
  if (Firebase.Firestore.getDocument(&fbdo, PROJECT_ID, "", documentPath.c_str())) {
    if (fbdo.httpCode() == 200) {
      // Parse the JSON response
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, fbdo.payload());
      JsonObject fields = doc["fields"];
      String farmerId = fields["farmer_id"]["stringValue"].as<String>();
      return farmerId;
    } else {
      Serial.printf("Error getting document: %s\n", fbdo.errorReason().c_str());
    }
  } else {
    Serial.printf("Failed to get document: %s\n", fbdo.errorReason().c_str());
  }
  return "";
}
