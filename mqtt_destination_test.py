#!/usr/bin/env python3
"""
MQTT Destination Test - Verify MQTT publishing for ALL destinations
Tests the critical bug fix: MQTT messages only published for PHARMACY destination
"""

import requests
import json
import time
import sys
import threading
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt

# Backend URL from environment
BACKEND_URL = "https://medifleet.preview.emergentagent.com/api"

# MQTT Configuration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_QOS = 1

class MQTTListener:
    def __init__(self):
        self.messages = []
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="medifleet_destination_test")
        self.connected = False
        self.lock = threading.Lock()
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            print(f"✅ MQTT Listener: Connected to {MQTT_BROKER}:{MQTT_PORT}")
            # Subscribe to all task topics
            client.subscribe("tasks/new", qos=MQTT_QOS)
            client.subscribe("tasks/assigned", qos=MQTT_QOS)
            client.subscribe("tasks/complete", qos=MQTT_QOS)
            print("📡 MQTT Listener: Subscribed to all task topics")
        else:
            print(f"❌ MQTT Listener: Connection failed - reason code: {reason_code}")
    
    def on_message(self, client, userdata, msg):
        with self.lock:
            try:
                payload = json.loads(msg.payload.decode())
                message_data = {
                    "topic": msg.topic,
                    "payload": payload,
                    "timestamp": time.time()
                }
                self.messages.append(message_data)
                print(f"📨 MQTT: {msg.topic} -> {payload}")
            except json.JSONDecodeError as e:
                print(f"❌ MQTT: Failed to decode message: {e}")
    
    def start(self):
        """Start MQTT listener"""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            print(f"🔌 MQTT: Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            print(f"❌ MQTT: Connection error: {e}")
            return False
    
    def stop(self):
        """Stop MQTT listener"""
        self.client.loop_stop()
        self.client.disconnect()
        print("🔌 MQTT: Disconnected")
    
    def get_messages(self):
        """Get all received messages"""
        with self.lock:
            return self.messages.copy()
    
    def clear_messages(self):
        """Clear all received messages"""
        with self.lock:
            self.messages.clear()

def create_task(destination: str, priority: str = "medium") -> Optional[Dict]:
    """Create a task for the given destination"""
    task_data = {
        "destination": destination,
        "priority": priority
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/tasks", json=task_data)
        if response.status_code == 200:
            task = response.json()
            print(f"✅ Task created: {task['id']} -> {destination}")
            return task
        else:
            print(f"❌ Failed to create task: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None

def wait_for_assignment(task_id: str, timeout: int = 10) -> Optional[Dict]:
    """Wait for task to be assigned"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BACKEND_URL}/tasks/{task_id}")
            if response.status_code == 200:
                task = response.json()
                if task.get("status") == "assigned":
                    return task
                elif task.get("status") in ["pending", "bidding"]:
                    time.sleep(1)
                    continue
            return None
        except Exception as e:
            print(f"❌ Error checking task: {e}")
            return None
    return None

def complete_task(task_id: str) -> bool:
    """Complete a task"""
    try:
        response = requests.patch(f"{BACKEND_URL}/tasks/{task_id}", json={
            "status": "completed",
            "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        })
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error completing task: {e}")
        return False

def test_destination_mqtt(destination: str, mqtt_listener: MQTTListener) -> Dict[str, bool]:
    """Test MQTT publishing for a specific destination"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING MQTT FOR DESTINATION: {destination}")
    print(f"{'='*80}")
    
    # Clear previous messages
    mqtt_listener.clear_messages()
    
    results = {
        "tasks/new": False,
        "tasks/assigned": False,
        "tasks/complete": False
    }
    
    # Step 1: Create task (should publish tasks/new)
    print(f"📝 Step 1: Creating task to {destination}...")
    task = create_task(destination)
    if not task:
        print(f"❌ Failed to create task for {destination}")
        return results
    
    task_id = task["id"]
    time.sleep(2)  # Allow MQTT message to be published
    
    # Check for tasks/new message
    messages = mqtt_listener.get_messages()
    for msg in messages:
        if (msg["topic"] == "tasks/new" and 
            msg["payload"].get("task_id") == task_id and
            msg["payload"].get("destination") == destination):
            results["tasks/new"] = True
            print(f"✅ Step 1: tasks/new message received for {destination}")
            break
    
    if not results["tasks/new"]:
        print(f"❌ Step 1: No tasks/new message for {destination}")
    
    # Step 2: Wait for assignment (should publish tasks/assigned)
    print(f"⏳ Step 2: Waiting for task assignment...")
    assigned_task = wait_for_assignment(task_id)
    if assigned_task:
        print(f"✅ Task assigned to robot: {assigned_task.get('robot_name')}")
        time.sleep(2)  # Allow MQTT message to be published
        
        # Check for tasks/assigned message
        messages = mqtt_listener.get_messages()
        for msg in messages:
            if (msg["topic"] == "tasks/assigned" and 
                msg["payload"].get("task_id") == task_id and
                msg["payload"].get("destination") == destination):
                results["tasks/assigned"] = True
                print(f"✅ Step 2: tasks/assigned message received for {destination}")
                break
        
        if not results["tasks/assigned"]:
            print(f"❌ Step 2: No tasks/assigned message for {destination}")
        
        # Step 3: Complete task (should publish tasks/complete)
        print(f"🏁 Step 3: Completing task...")
        if complete_task(task_id):
            time.sleep(2)  # Allow MQTT message to be published
            
            # Check for tasks/complete message
            messages = mqtt_listener.get_messages()
            for msg in messages:
                if (msg["topic"] == "tasks/complete" and 
                    msg["payload"].get("task_id") == task_id):
                    results["tasks/complete"] = True
                    print(f"✅ Step 3: tasks/complete message received for {destination}")
                    break
            
            if not results["tasks/complete"]:
                print(f"❌ Step 3: No tasks/complete message for {destination}")
        else:
            print(f"❌ Step 3: Failed to complete task for {destination}")
    else:
        print(f"❌ Step 2: Task assignment failed for {destination}")
    
    # Summary for this destination
    success_count = sum(results.values())
    print(f"\n🎯 MQTT RESULT FOR {destination}: {success_count}/3 events successful")
    for event, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {event}: {status}")
    
    return results

def main():
    """Main test execution"""
    print("🚀 MQTT DESTINATION TEST - Testing ALL destinations")
    print("Bug Report: MQTT messages only published for PHARMACY destination")
    print("=" * 80)
    
    # Start MQTT listener
    mqtt_listener = MQTTListener()
    if not mqtt_listener.start():
        print("❌ Failed to start MQTT listener")
        sys.exit(1)
    
    try:
        # Reset robots
        print("\n🔄 Resetting robots...")
        response = requests.post(f"{BACKEND_URL}/robots/reset-all")
        if response.status_code == 200:
            print("✅ Robots reset successfully")
        else:
            print("⚠️ Robot reset may have failed")
        
        time.sleep(3)  # Allow reset to complete
        
        # Test all 6 destinations from review request
        destinations = ["ENTRANCE", "ICU", "PHARMACY", "ROOM_101", "EMERGENCY", "STORAGE"]
        all_results = {}
        
        for destination in destinations:
            try:
                results = test_destination_mqtt(destination, mqtt_listener)
                all_results[destination] = results
                time.sleep(3)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test for {destination} failed with error: {e}")
                all_results[destination] = {"tasks/new": False, "tasks/assigned": False, "tasks/complete": False}
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 FINAL MQTT DESTINATION TEST SUMMARY")
        print("=" * 80)
        
        total_destinations = len(destinations)
        total_events = total_destinations * 3  # 3 events per destination
        successful_events = 0
        successful_destinations = 0
        
        for destination, results in all_results.items():
            success_count = sum(results.values())
            successful_events += success_count
            
            if success_count == 3:
                successful_destinations += 1
                status = "✅ PASS (3/3)"
            else:
                status = f"❌ FAIL ({success_count}/3)"
            
            print(f"   {destination:12} : {status}")
        
        print(f"\nOverall Results:")
        print(f"   Destinations: {successful_destinations}/{total_destinations} fully working")
        print(f"   MQTT Events:  {successful_events}/{total_events} successful")
        print(f"   Expected:     {total_events} MQTT messages ({total_destinations} destinations × 3 events each)")
        
        if successful_destinations == total_destinations:
            print("\n🎉 SUCCESS: MQTT publishing works for ALL destinations!")
            print("✅ Bug fix verified - MQTT messages published for all destinations")
        else:
            failed_destinations = [dest for dest, results in all_results.items() if sum(results.values()) < 3]
            print(f"\n⚠️  PARTIAL SUCCESS: {len(failed_destinations)} destinations failed")
            print(f"❌ Failed destinations: {failed_destinations}")
            
            # Check if only PHARMACY works (original bug)
            pharmacy_results = all_results.get("PHARMACY", {})
            pharmacy_success = sum(pharmacy_results.values()) == 3
            
            if pharmacy_success and successful_destinations == 1:
                print("🚨 CRITICAL: Original bug still exists - only PHARMACY works!")
            elif successful_destinations > 1:
                print("✅ PARTIAL FIX: More than just PHARMACY works now")
        
        # Exit with appropriate code
        all_passed = successful_destinations == total_destinations
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        sys.exit(1)
    finally:
        mqtt_listener.stop()

if __name__ == "__main__":
    main()