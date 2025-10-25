#!/usr/bin/env python3
"""
Test MQTT completion flow
"""

import requests
import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# Backend URL
BACKEND_URL = "https://medifleet.preview.emergentagent.com/api"

# MQTT Configuration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

class CompletionMQTTListener:
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
            client.subscribe("tasks/complete", qos=1)
            print("📡 Subscribed to tasks/complete")
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

def create_and_wait_for_assignment():
    """Create a task and wait for it to be assigned"""
    try:
        # Create task
        response = requests.post(
            f"{BACKEND_URL}/tasks",
            json={"destination": "ICU", "priority": "high"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Task creation failed: {response.status_code}")
            return None, None
        
        task = response.json()
        task_id = task["id"]
        print(f"✅ Task created: {task_id}")
        
        # Wait for assignment
        print("⏳ Waiting for task assignment...")
        for i in range(15):  # Wait up to 15 seconds
            response = requests.get(f"{BACKEND_URL}/tasks/{task_id}")
            if response.status_code == 200:
                task_data = response.json()
                if task_data.get("status") == "assigned":
                    robot_id = task_data.get("robot_id")
                    print(f"✅ Task assigned to robot: {robot_id}")
                    return task_id, robot_id
            time.sleep(1)
        
        print("❌ Task was not assigned within timeout")
        return task_id, None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def complete_task(task_id):
    """Mark a task as completed"""
    try:
        completion_time = datetime.now(timezone.utc).isoformat()
        response = requests.patch(
            f"{BACKEND_URL}/tasks/{task_id}",
            json={"status": "completed", "completed_at": completion_time},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Task {task_id} marked as completed")
            return True
        else:
            print(f"❌ Failed to complete task: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error completing task: {e}")
        return False

def main():
    print("🚀 MQTT Completion Test")
    print("=" * 50)
    
    # Start MQTT listener
    listener = CompletionMQTTListener()
    if not listener.connect():
        print("❌ Failed to connect MQTT listener")
        return
    
    print("\n⏳ Waiting 2 seconds for MQTT to settle...")
    time.sleep(2)
    
    # Clear any existing messages
    listener.messages.clear()
    
    # Create task and wait for assignment
    print("\n📝 Creating and assigning task...")
    task_id, robot_id = create_and_wait_for_assignment()
    
    if not task_id or not robot_id:
        print("❌ Failed to create and assign task")
        listener.disconnect()
        return
    
    # Complete the task
    print(f"\n🏁 Completing task {task_id}...")
    if not complete_task(task_id):
        print("❌ Failed to complete task")
        listener.disconnect()
        return
    
    # Wait for completion MQTT message
    print("\n⏳ Waiting 10 seconds for completion MQTT message...")
    time.sleep(10)
    
    # Analyze received messages
    print(f"\n📊 Analysis:")
    print(f"Total MQTT messages received: {len(listener.messages)}")
    
    if listener.messages:
        print("\n📨 Received messages:")
        for i, msg in enumerate(listener.messages, 1):
            print(f"  {i}. Topic: {msg['topic']}")
            print(f"     Payload: {msg['payload']}")
            print()
        
        # Check if our task completion message was received
        completion_messages = [msg for msg in listener.messages 
                             if msg['payload'].get('task_id') == task_id]
        
        if completion_messages:
            print(f"✅ Found completion message for task {task_id}")
            msg = completion_messages[0]
            payload = msg['payload']
            
            # Verify payload structure
            expected_fields = ['task_id', 'robot_id', 'completed_at']
            missing_fields = [field for field in expected_fields if field not in payload]
            
            if missing_fields:
                print(f"❌ Missing fields in payload: {missing_fields}")
            else:
                print("✅ All expected fields present in payload")
            
            # Check robot_id
            if payload.get('robot_id') == robot_id:
                print(f"✅ Correct robot_id in completion message: {robot_id}")
            else:
                print(f"❌ Robot ID mismatch: expected {robot_id}, got {payload.get('robot_id')}")
        else:
            print(f"❌ No completion message found for task {task_id}")
    else:
        print("❌ No MQTT messages received")
    
    # Cleanup
    listener.disconnect()
    print("\n✅ Test completed")

if __name__ == "__main__":
    main()