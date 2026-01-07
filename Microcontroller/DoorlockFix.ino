#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid ="---";
const char* password ="---";
const char* url ="---";
void setup() {
  Serial.begin(115200);
  delay(4000);

  Wifi.begin(ssid, password);
  Serial.print("Menyambungkan ke Wifi");
  while (WiFi.status()!= WL_CONNECTED){
    delay(500);
    Serial.println("Tunggu Sebentar");
  }
  Serial.println("WiFi Tersambung");

  if (WiFi.status()== WL_CONNECTED){
    HTTPClient http;
    http.begin(url);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(payload);
    } else {
      Serial.print("Error di HTTP request: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

}

void loop() {
  // put your main code here, to run repeatedly:

}
