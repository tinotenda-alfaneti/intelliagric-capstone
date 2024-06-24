#include <Arduino.h>
#include <ArduinoOTA.h>
#include <WiFi.h>
#include <DHT.h>
#include <Firebase_ESP_Client.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <LiquidCrystal_I2C.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

#include "config.h" /* Contains WIFI_SSID, WIFI_PASSWORD, API_KEY, DATABASE_URL, and PROJECT_ID */

#define MOIS_PIN 34 
#define TEMP_PIN  17
#define DHT11_PIN 14
#define uS_TO_S_FACTOR 1000000ULL  /* Conversion factor for microseconds to seconds */
#define TIME_TO_SLEEP  5            /* Time ESP32 will go to sleep (in seconds) */
#define LCD_COL 16
#define LCD_ROW 2

RTC_DATA_ATTR String farmerId;

FirebaseData fbdo; /* Define Firebase Data object */
FirebaseAuth auth;
FirebaseConfig config;
bool signupOK = false;

Preferences preferences;

DHT dht11(DHT11_PIN, DHT11);

float soilTemp;
int soilMois;
float pH;
String npk;
float humi;
float tempC;
unsigned long lastUpdate = 0;
int displayMode = 0;


OneWire oneWire(TEMP_PIN);
DallasTemperature DS18B20(&oneWire);
LiquidCrystal_I2C lcd(0x27, 16, 2);

/********** SETUP **********/
void setup(){
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  DS18B20.begin();
  dht11.begin();
  lcd.init(); 
  lcd.backlight();

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  ArduinoOTA.setHostname(SERIAL_NUM);
  ArduinoOTA.setPassword(OTA_PASSWORD);
  ArduinoOTA.begin();

  pinMode(BUILTIN_LED, OUTPUT);
  
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  config.token_status_callback = tokenStatusCallback;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  if (Firebase.authenticated() == true) {
    signupOK = true;
    }

  preferences.begin("config", false); /* Open preferences with "config" namespace, RW access */
  farmerId = preferences.getString("farmerId", "");
  farmerId = ""; /* to comment out during deployment */
  if (farmerId == "") {
    farmerId = getFarmerId(SERIAL_NUM);
    preferences.putString("farmerId", farmerId);
    if (farmerId != "") {
      Serial.print("Farmer ID: ");
      Serial.println(farmerId);
    } else {
      Serial.println("Failed to get farmer ID");
    }
  }

  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR); /* Setup ESP32 to wake up after */
}

/********** LOOP **********/
void loop() {

  ArduinoOTA.handle();

  lcdScreenControl();

  if (Firebase.ready()){
    DS18B20.requestTemperatures();
    
    soilTemp = DS18B20.getTempCByIndex(0);  // Read temperature in °C
    soilMois = analogRead(MOIS_PIN); // Moisture sensor
    pH = 7; // dummy Soil pH
    npk = "7-14-7"; // dummy Soil NPK
    humi  = dht11.readHumidity(); // humidity reading
    tempC = dht11.readTemperature(); // temp in degrees

    String basePath = "iot/" + farmerId;

    if (Firebase.RTDB.setString(&fbdo, basePath + "/npk", npk)){
      Serial.print("NPK SENT ");
      Serial.println(npk);
    } else {
      Serial.println("NPK FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setFloat(&fbdo, basePath + "/temp", soilTemp)){
      Serial.print("TEMP SENT ");
      Serial.println(soilTemp);
    } else {
      Serial.println("TEMP FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setInt(&fbdo, basePath + "/mois", soilMois)){
      Serial.print("MOIS SENT ");
      Serial.println(soilMois);
    } else {
      Serial.println("MOIS FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setInt(&fbdo, basePath + "/ph", pH)){
      Serial.print("PH SENT ");
      Serial.println(pH);
    } else {
      Serial.println("PH FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setFloat(&fbdo, basePath + "/humidity", humi)){
      Serial.print("HUMI SENT ");
      Serial.println(humi);
    } else {
      Serial.println("HUMI FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setFloat(&fbdo, basePath + "/air-temp", tempC)){
      Serial.print("AIR TEMP SENT ");
      Serial.println(tempC);
    } else {
      Serial.println("AIR TEMP FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    esp_light_sleep_start(); /* sleep after perfoming  */
  }
}

String getFarmerId(const char* serialNumber) {

  String documentPath = "iot_devices/" + String(SERIAL_NUM);

  if (Firebase.Firestore.getDocument(&fbdo, PROJECT_ID, "", documentPath.c_str())) {
    if (fbdo.httpCode() == 200) {
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

void lcdScreenControl() {
  
  humi  = dht11.readHumidity();
  tempC = dht11.readTemperature();

  unsigned long timeDiff = millis() - lastUpdate;

  if (timeDiff > 3000) {
    displayMode = (displayMode + 1) % 2; // Rotate between 0, 1
    lastUpdate = millis(); 
    lcd.clear();
  }

  // Display based on the current mode
  switch (displayMode) {
    case 0: 
      lcd.setCursor(0, 0);
      lcd.print("AirTemp:");
      lcd.setCursor(10, 0); 
      lcd.print(tempC);
      lcd.setCursor(0, 1);
      lcd.print("SoilTemp:");
      lcd.setCursor(10, 1);
      lcd.print(soilTemp);
      break;
    case 1: 
      lcd.setCursor(0, 0);
      lcd.print("Humid:");
      lcd.setCursor(7, 0); 
      lcd.print(humi);
       lcd.setCursor(0, 1);
      lcd.print("Moist:");
      lcd.setCursor(7, 1);
      lcd.print(soilMois);
      break;
  }
}
