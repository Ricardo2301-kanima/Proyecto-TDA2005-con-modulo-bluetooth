#include "AudioTools.h"
#include "BluetoothA2DPSink.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid     = "WIFI";
const char* password = "PASSWORD";

// Rutas del servidor Node.js
const char* streamUrl = "http://192.168.X.X:3000/stream";
const char* statusUrl = "http://192.168.X.X:3000/status";

// Pines I2S para el DAC PCM5102A
#define I2S_BCLK 26
#define I2S_LRC  25
#define I2S_DOUT 22

I2SStream i2s;
BluetoothA2DPSink a2dp_sink;

// Componentes para el Web Stream (MP3)
URLStream urlStream(ssid, password);
MP3DecoderHelix decoder;
EncodedAudioStream webAudioStream(&i2s, &decoder);
StreamCopy webCopier(webAudioStream, urlStream);

bool isWebStreaming = false;
unsigned long lastStatusCheck = 0;
const unsigned long STATUS_INTERVAL_MS = 3000;

// Callback: Intercepta los datos del Bluetooth antes de enviarlos al I2S
void bt_data_callback(const uint8_t *data, uint32_t length) {
    // Si el servidor web está transmitiendo, descartamos los paquetes Bluetooth (Mute)
    if (!isWebStreaming) {
        i2s.write(data, length);
    }
}

void checkServerStatus() {
    if (millis() - lastStatusCheck < STATUS_INTERVAL_MS) return;
    lastStatusCheck = millis();

    HTTPClient http;
    http.begin(statusUrl);
    int httpCode = http.GET();

    if (httpCode == 200) {
        String payload = http.getString();
        JsonDocument doc;
        deserializeJson(doc, payload);
        
        bool serverPlaying = doc["isPlaying"];

        if (serverPlaying && !isWebStreaming) {
            Serial.println("Servidor web activo. Iniciando decodificación MP3...");
            isWebStreaming = true;
            urlStream.begin(streamUrl);
            webAudioStream.begin();
        } 
        else if (!serverPlaying && isWebStreaming) {
            Serial.println("Servidor web inactivo. Retornando a Bluetooth...");
            isWebStreaming = false;
            urlStream.end();
            webAudioStream.end();
            
            // Reconfigurar I2S a los parámetros estándar de Bluetooth (44.1kHz, 16 bits, Stereo)
            auto config = i2s.defaultConfig(TX_MODE);
            config.sample_rate = 44100;
            config.channels = 2;
            config.bits_per_sample = 16;
            i2s.begin(config);
        }
    }
    http.end();
}

void setup() {
    Serial.begin(115200);

    // 1. Configurar pines I2S para el PCM5102A
    auto config = i2s.defaultConfig(TX_MODE);
    config.pin_bck  = I2S_BCLK;
    config.pin_ws   = I2S_LRC;
    config.pin_data = I2S_DOUT;
    config.sample_rate = 44100;
    config.channels = 2;
    config.bits_per_sample = 16;
    i2s.begin(config);

    // 2. Configurar Bluetooth con callback manual
    a2dp_sink.set_stream_reader(bt_data_callback, false);
    a2dp_sink.start("ESP32_Audio_DAC");

    // 3. Configurar conexión inicial
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Conectado.");
}

void loop() {
    checkServerStatus();

    // Si el web stream está activo, procesamos los chunks MP3 y los enviamos al DAC
    if (isWebStreaming) {
        webCopier.copy();
    }
}
