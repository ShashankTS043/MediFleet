#!/usr/bin/env python3
"""
Simple MQTT Test - Create a task and listen for MQTT messages
"""

import requests
import json
import time
import threading
import paho.mqtt.client as mqtt

# Backend URL
BACKEND_URL = "https://medifleet.preview.emergentagent.com/api"

# MQTT Configuration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

class SimpleMQTTListener:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.messages = []
        self.connected = False
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            print("✅ MQTT Listener connected")
            # Subscribe to all task topics
            client.subscribe("tasks/new", qos=1)
            client.subscribe("tasks/assigned", qos=1)
            client.subscribe("tasks/complete", qos=1)
            print("📡 Subscribed to all task topics")
        else:
            print(f"❌ MQTT connection failed: {reason_code}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            message_info = {
                "topic": msg.topic,
                "payload": payload,
                "timestamp": time.time()
            }
            self.messages.append(message_info)
            print(f"📨 MQTT Message: {msg.topic} -> {payload}")
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def connect(self):
        try:
            print(f"🔌 Connecting to {MQTT_BROKER}:{MQTT_PORT}")
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            print(f"❌ MQTT connection error: {e}")
            return False
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

def create_task(destination="PHARMACY", priority="medium"):
    """Create a task via API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/tasks",
            json={"destination": destination, "priority": priority},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            task = response.json()
            print(f"✅ Task created: {task['id']} -> {destination}")
            return task
        else:
            print(f"❌ Task creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None

def main():
    print("🚀 Simple MQTT Test")
    print("=" * 50)
    
    # Start MQTT listener
    listener = SimpleMQTTListener()
    if not listener.connect():
        print("❌ Failed to connect MQTT listener")
        return
    
    print("\n⏳ Waiting 2 seconds for MQTT to settle...")
    time.sleep(2)
    
    # Clear any existing messages
    listener.messages.clear()
    
    # Create a task
    print("\n📝 Creating test task...")
    task = create_task("PHARMACY", "medium")
    
    if not task:
        print("❌ Failed to create task")
        listener.disconnect()
        return
    
    task_id = task["id"]
    
    # Wait and check for MQTT messages
    print(f"\n⏳ Waiting 15 seconds for MQTT messages for task {task_id}...")
    time.sleep(15)
    
    # Analyze received messages
    print(f"\n📊 Analysis:")
    print(f"Total MQTT messages received: {len(listener.messages)}")
    
    if listener.messages:
        print("\n📨 Received messages:")
        for i, msg in enumerate(listener.messages, 1):
            print(f"  {i}. Topic: {msg['topic']}")
            print(f"     Payload: {msg['payload']}")
            print(f"     Time: {time.ctime(msg['timestamp'])}")
            print()
        
        # Check if our task ID appears in any message
        our_messages = [msg for msg in listener.messages 
                       if msg['payload'].get('task_id') == task_id]
        
        if our_messages:
            print(f"✅ Found {len(our_messages)} messages for our task {task_id}")
            for msg in our_messages:
                print(f"   - {msg['topic']}: {msg['payload']}")
        else:
            print(f"❌ No messages found for our task {task_id}")
            print("   This suggests MQTT publishing is not working correctly")
    else:
        print("❌ No MQTT messages received at all")
        print("   This could indicate:")
        print("   1. Backend MQTT client is not connected")
        print("   2. Backend is not publishing messages")
        print("   3. Network connectivity issues")
    
    # Cleanup
    listener.disconnect()
    print("\n✅ Test completed")

if __name__ == "__main__":
    main()