#!/usr/bin/env python3
"""
Comprehensive MQTT Test - Test all three MQTT topics in sequence
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

class ComprehensiveMQTTListener:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.messages = {}  # Organized by topic
        self.connected = False
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            print("✅ MQTT Listener connected")
            # Subscribe to all task topics
            topics = ["tasks/new", "tasks/assigned", "tasks/complete"]
            for topic in topics:
                client.subscribe(topic, qos=1)
                print(f"📡 Subscribed to {topic}")
        else:
            print(f"❌ MQTT connection failed: {reason_code}")
    
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            if topic not in self.messages:
                self.messages[topic] = []
            
            message_info = {
                "payload": payload,
                "timestamp": time.time(),
                "qos": msg.qos
            }
            self.messages[topic].append(message_info)
            print(f"📨 {topic}: {payload}")
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
    
    def clear_messages(self):
        self.messages.clear()
    
    def get_messages_for_task(self, task_id):
        """Get all messages for a specific task ID"""
        task_messages = {}
        for topic, messages in self.messages.items():
            task_messages[topic] = [
                msg for msg in messages 
                if msg['payload'].get('task_id') == task_id
            ]
        return task_messages

def create_task(destination="STORAGE", priority="medium"):
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
            return None
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None

def wait_for_assignment(task_id, timeout=15):
    """Wait for task to be assigned"""
    print(f"⏳ Waiting for task {task_id} assignment...")
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        try:
            response = requests.get(f"{BACKEND_URL}/tasks/{task_id}")
            if response.status_code == 200:
                task_data = response.json()
                status = task_data.get("status")
                if status == "assigned":
                    robot_id = task_data.get("robot_id")
                    print(f"✅ Task assigned to robot: {robot_id}")
                    return robot_id
                elif status in ["pending", "bidding"]:
                    time.sleep(1)
                    continue
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error checking task status: {e}")
            return None
    
    print("❌ Task assignment timeout")
    return None

def complete_task(task_id):
    """Mark task as completed"""
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

def verify_message_payload(topic, payload, expected_fields):
    """Verify message payload has expected fields"""
    missing_fields = [field for field in expected_fields if field not in payload]
    if missing_fields:
        print(f"❌ {topic}: Missing fields {missing_fields}")
        return False
    else:
        print(f"✅ {topic}: All expected fields present")
        return True

def main():
    print("🚀 Comprehensive MQTT Integration Test")
    print("Testing all three MQTT topics: tasks/new, tasks/assigned, tasks/complete")
    print("=" * 80)
    
    # Start MQTT listener
    listener = ComprehensiveMQTTListener()
    if not listener.connect():
        print("❌ Failed to connect MQTT listener")
        return False
    
    print("\n⏳ Waiting 3 seconds for MQTT to settle...")
    time.sleep(3)
    
    # Clear any existing messages
    listener.clear_messages()
    
    # Test workflow
    print("\n" + "="*60)
    print("🧪 TESTING COMPLETE MQTT WORKFLOW")
    print("="*60)
    
    # Step 1: Create task
    print("\n📝 Step 1: Creating task...")
    task = create_task("EMERGENCY", "urgent")
    if not task:
        listener.disconnect()
        return False
    
    task_id = task["id"]
    
    # Step 2: Wait for tasks/new message
    print("\n⏳ Step 2: Waiting for tasks/new message...")
    time.sleep(3)
    
    # Step 3: Wait for assignment and tasks/assigned message
    print("\n⏳ Step 3: Waiting for task assignment...")
    robot_id = wait_for_assignment(task_id)
    if not robot_id:
        print("❌ Task was not assigned")
        listener.disconnect()
        return False
    
    # Wait a bit more for tasks/assigned message
    time.sleep(2)
    
    # Step 4: Complete task and wait for tasks/complete message
    print("\n🏁 Step 4: Completing task...")
    if not complete_task(task_id):
        listener.disconnect()
        return False
    
    # Wait for completion message
    time.sleep(3)
    
    # Step 5: Analyze all messages
    print("\n" + "="*60)
    print("📊 ANALYZING MQTT MESSAGES")
    print("="*60)
    
    task_messages = listener.get_messages_for_task(task_id)
    
    # Expected message structure
    expected_payloads = {
        "tasks/new": ["task_id", "destination", "priority", "created_at"],
        "tasks/assigned": ["task_id", "robot_id", "destination", "distance"],
        "tasks/complete": ["task_id", "robot_id", "completed_at"]
    }
    
    all_tests_passed = True
    
    for topic, expected_fields in expected_payloads.items():
        print(f"\n🔍 Checking {topic}:")
        
        if topic not in task_messages or not task_messages[topic]:
            print(f"❌ No {topic} message received for task {task_id}")
            all_tests_passed = False
            continue
        
        if len(task_messages[topic]) > 1:
            print(f"⚠️  Multiple {topic} messages received ({len(task_messages[topic])})")
        
        # Check the first (or only) message
        message = task_messages[topic][0]
        payload = message["payload"]
        
        print(f"   Payload: {payload}")
        
        # Verify payload structure
        if not verify_message_payload(topic, payload, expected_fields):
            all_tests_passed = False
            continue
        
        # Verify specific field values
        if payload.get("task_id") != task_id:
            print(f"❌ {topic}: Task ID mismatch")
            all_tests_passed = False
        else:
            print(f"✅ {topic}: Correct task ID")
        
        # Topic-specific validations
        if topic == "tasks/new":
            if payload.get("destination") != "EMERGENCY":
                print(f"❌ {topic}: Wrong destination")
                all_tests_passed = False
            if payload.get("priority") != "urgent":
                print(f"❌ {topic}: Wrong priority")
                all_tests_passed = False
        
        elif topic == "tasks/assigned":
            if payload.get("robot_id") != robot_id:
                print(f"❌ {topic}: Wrong robot ID")
                all_tests_passed = False
            if not isinstance(payload.get("distance"), (int, float)):
                print(f"❌ {topic}: Distance is not a number")
                all_tests_passed = False
        
        elif topic == "tasks/complete":
            if payload.get("robot_id") != robot_id:
                print(f"❌ {topic}: Wrong robot ID")
                all_tests_passed = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    total_topics = len(expected_payloads)
    successful_topics = sum(1 for topic in expected_payloads.keys() 
                          if topic in task_messages and task_messages[topic])
    
    print(f"MQTT Topics tested: {total_topics}")
    print(f"MQTT Topics working: {successful_topics}")
    print(f"Overall result: {'✅ PASS' if all_tests_passed else '❌ FAIL'}")
    
    if all_tests_passed:
        print("\n🎉 ALL MQTT INTEGRATION TESTS PASSED!")
        print("✅ tasks/new: Published when task is created")
        print("✅ tasks/assigned: Published when task is assigned after bidding")
        print("✅ tasks/complete: Published when task is marked completed")
        print("✅ All message payloads have correct structure and data")
    else:
        print("\n⚠️  SOME MQTT TESTS FAILED")
        print("Check the detailed analysis above for specific issues")
    
    # Cleanup
    listener.disconnect()
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)