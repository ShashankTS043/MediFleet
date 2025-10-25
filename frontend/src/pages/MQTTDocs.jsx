import { Code, Copy, Check, Wifi, Zap, MessageSquare } from "lucide-react";
import { useState } from "react";

export default function MQTTDocs() {
  const [copiedCode, setCopiedCode] = useState(null);

  const copyToClipboard = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const topics = [
    {
      topic: "tasks/new",
      direction: "Server → Robot",
      description: "Broadcast when a new task is created and enters bidding phase",
      payload: `{
  "task_id": "abc123",
  "destination": "ICU",
  "priority": "high",
  "created_at": "2025-01-25T10:30:00Z"
}`
    },
    {
      topic: "tasks/assigned",
      direction: "Server → Robot",
      description: "Notification when a task is assigned to a specific robot",
      payload: `{
  "task_id": "abc123",
  "robot_id": "robot_01",
  "destination": "ICU",
  "distance": 85
}`
    },
    {
      topic: "robots/status",
      direction: "Robot → Server",
      description: "Periodic status updates from robots",
      payload: `{
  "robot_id": "robot_01",
  "location": "ENTRANCE",
  "battery": 95,
  "status": "idle"
}`
    },
    {
      topic: "tasks/complete",
      direction: "Robot → Server",
      description: "Robot reports task completion",
      payload: `{
  "task_id": "abc123",
  "robot_id": "robot_01",
  "completed_at": "2025-01-25T10:35:00Z"
}`
    }
  ];

  const esp32Code = `#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker
const char* mqtt_broker = "mqtt.medifleet.local";
const int mqtt_port = 1883;
const char* mqtt_username = "robot_01";
const char* mqtt_password = "your_password";

WiFiClient espClient;
PubSubClient client(espClient);

String robotId = "robot_01";
String currentLocation = "ENTRANCE";
int batteryLevel = 100;

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  
  // Connect to MQTT
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(messageCallback);
  
  connectMQTT();
}

void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(robotId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected!");
      
      // Subscribe to relevant topics
      client.subscribe("tasks/new");
      client.subscribe("tasks/assigned");
      
      Serial.println("Subscribed to topics");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void messageCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Handle different topics
  if (strcmp(topic, "tasks/new") == 0) {
    handleNewTask(message);
  } else if (strcmp(topic, "tasks/assigned") == 0) {
    handleTaskAssigned(message);
  }
}

void handleNewTask(String message) {
  // Parse JSON and decide if robot should bid
  Serial.println("New task available for bidding");
  // Add bidding logic here
}

void handleTaskAssigned(String message) {
  // Parse JSON and start moving to destination
  Serial.println("Task assigned to this robot");
  // Add movement logic here
}

void publishStatus() {
  String payload = "{\"robot_id\":\"" + robotId + "\",";
  payload += "\"location\":\"" + currentLocation + "\",";
  payload += "\"battery\":" + String(batteryLevel) + ",";
  payload += "\"status\":\"idle\"}";
  
  client.publish("robots/status", payload.c_str());
  Serial.println("Status published");
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop();
  
  // Publish status every 5 seconds
  static unsigned long lastStatusUpdate = 0;
  if (millis() - lastStatusUpdate > 5000) {
    publishStatus();
    lastStatusUpdate = millis();
  }
}`;

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl mb-4">
            <MessageSquare className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-slate-800 mb-4">MQTT Integration Guide</h1>
          <p className="text-base text-slate-600 max-w-2xl mx-auto">
            Complete documentation for hardware team to integrate ESP32 robots with MediFleet
          </p>
        </div>

        {/* Connection Info */}
        <div className="glass rounded-3xl p-8 mb-8 card-hover">
          <div className="flex items-center space-x-3 mb-6">
            <Wifi className="w-6 h-6 text-cyan-600" />
            <h2 className="text-2xl font-bold text-slate-800">Connection Details</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-slate-700 mb-2">MQTT Broker</h3>
              <code className="block bg-slate-800 text-cyan-400 p-3 rounded-lg text-sm">
                mqtt.medifleet.local:1883
              </code>
            </div>
            <div>
              <h3 className="font-semibold text-slate-700 mb-2">Protocol</h3>
              <code className="block bg-slate-800 text-cyan-400 p-3 rounded-lg text-sm">
                MQTT v3.1.1
              </code>
            </div>
            <div>
              <h3 className="font-semibold text-slate-700 mb-2">QoS Level</h3>
              <code className="block bg-slate-800 text-cyan-400 p-3 rounded-lg text-sm">
                QoS 1 (At least once)
              </code>
            </div>
            <div>
              <h3 className="font-semibold text-slate-700 mb-2">Keep Alive</h3>
              <code className="block bg-slate-800 text-cyan-400 p-3 rounded-lg text-sm">
                60 seconds
              </code>
            </div>
          </div>
        </div>

        {/* MQTT Topics */}
        <div className="glass rounded-3xl p-8 mb-8 card-hover">
          <div className="flex items-center space-x-3 mb-6">
            <Zap className="w-6 h-6 text-cyan-600" />
            <h2 className="text-2xl font-bold text-slate-800">MQTT Topics</h2>
          </div>
          <div className="space-y-6">
            {topics.map((item, index) => (
              <div key={index} className="bg-white rounded-xl p-6 border-2 border-slate-100 hover:border-cyan-200 transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <code className="text-lg font-mono font-bold text-cyan-600">{item.topic}</code>
                    <p className="text-sm text-slate-500 mt-1">{item.direction}</p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(item.payload, `topic-${index}`)}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    title="Copy payload"
                  >
                    {copiedCode === `topic-${index}` ? (
                      <Check className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4 text-slate-400" />
                    )}
                  </button>
                </div>
                <p className="text-slate-600 mb-4">{item.description}</p>
                <div className="bg-slate-50 rounded-lg p-4">
                  <p className="text-xs text-slate-500 mb-2 font-semibold">PAYLOAD STRUCTURE:</p>
                  <pre className="text-xs text-slate-700 overflow-x-auto">{item.payload}</pre>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ESP32 Example Code */}
        <div className="glass rounded-3xl p-8 card-hover">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Code className="w-6 h-6 text-cyan-600" />
              <h2 className="text-2xl font-bold text-slate-800">ESP32 Arduino Example</h2>
            </div>
            <button
              onClick={() => copyToClipboard(esp32Code, 'esp32')}
              className="flex items-center space-x-2 px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors"
            >
              {copiedCode === 'esp32' ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Code</span>
                </>
              )}
            </button>
          </div>
          <div className="bg-slate-900 rounded-xl p-6 overflow-x-auto">
            <pre className="text-sm text-cyan-400 font-mono">{esp32Code}</pre>
          </div>
          
          <div className="mt-6 p-4 bg-cyan-50 border-2 border-cyan-200 rounded-xl">
            <h3 className="font-semibold text-slate-800 mb-2">📚 Required Libraries:</h3>
            <ul className="space-y-1 text-sm text-slate-700">
              <li>• <code className="bg-white px-2 py-1 rounded">WiFi.h</code> - Built-in ESP32 WiFi library</li>
              <li>• <code className="bg-white px-2 py-1 rounded">PubSubClient</code> - Install via Arduino Library Manager</li>
              <li>• <code className="bg-white px-2 py-1 rounded">ArduinoJson</code> - For JSON parsing (recommended)</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-slate-600">
          <p>Need help? Contact the development team or visit our <a href="/about" className="text-cyan-600 hover:underline">About page</a></p>
        </div>
      </div>
    </div>
  );
}