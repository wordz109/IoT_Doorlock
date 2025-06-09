#include <WiFi.h>
#include <HTTPClient.h>

#define WIFI_SSID "***********"
#define WIFI_PASSWORD "*****************"
#define FIREBASE_HOST "******************************"
#define DATABASE_SECRET "*************************************"
#define RELAY_PIN 5

String lastStatus = "";
String payload = "";
void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);  // Relay off awal

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Menghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Terhubung ke WiFi");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected, reconnecting...");
    WiFi.reconnect();
    delay(2000);
    return;
  }

  HTTPClient httpGet;
  String getUrl = String(FIREBASE_HOST) + "/status/status.json?auth=" + String(DATABASE_SECRET);
  httpGet.setTimeout(5000);
  httpGet.begin(getUrl);

  Serial.println("Mengambil status dari Firebase...");
  int httpCode = httpGet.GET();
  Serial.println(payload);

  if (httpCode == 200) {
    payload = httpGet.getString();
    payload.trim();
    payload.replace("\"", "");  // Hapus tanda kutip

    if (payload != lastStatus) {
      Serial.println("📥 Status Firebase: " + payload);
      lastStatus = payload;

      if (payload == "diizinkan") {
      
        Serial.println("✅ Akses diizinkan, relay ON");
        digitalWrite(RELAY_PIN, LOW);  // Relay ON
        delay(5000);                   // Tahan 5 detik
        digitalWrite(RELAY_PIN, HIGH); // Relay OFF
        Serial.println("⛔ Relay OFF, update status ke 'ditolak'");

        // Update status ke 'ditolak'
        HTTPClient httpPut;
        String putUrl = String(FIREBASE_HOST) + "/status/status.json?auth=" + String(DATABASE_SECRET);
        httpPut.begin(putUrl);
        httpPut.addHeader("Content-Type", "application/json");
        int putCode = httpPut.PUT("\"ditolak\"");
        if (putCode == 200) {
          Serial.println("🔄 Status berhasil diupdate ke 'ditolak'");
        } else {
          Serial.printf("❌ Gagal update status. Kode: %d\n", putCode);
        }
        httpPut.end();
      }
    }
  } else {
    Serial.printf("❌ Gagal ambil data. HTTP code: %d\n", httpCode);
  }
  httpGet.end();

  delay(3000);
}
