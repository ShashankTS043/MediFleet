#!/usr/bin/env python3
"""
MQTT Integration Test Suite for MediFleet Task Events
Tests MQTT publishing to test.mosquitto.org:1883 for task lifecycle events
"""

import requests
import json
import time
import sys
import threading
from typing import Dict, List, Optional, Any
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# Backend URL from environment
BACKEND_URL = "https://medifleet.preview.emergentagent.com/api"

# MQTT Configuration (same as backend)
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_QOS = 1

class MQTTTestClient:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.received_messages = {}
        self.connected = False
        self.lock = threading.Lock()
        
        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            print("✅ MQTT Test Client connected successfully")
            # Subscribe to all test topics
            topics = ["tasks/new", "tasks/assigned", "tasks/complete"]
            for topic in topics:
                client.subscribe(topic, qos=MQTT_QOS)
                print(f"📡 Subscribed to topic: {topic}")
        else:
            self.connected = False
            print(f"❌ MQTT Test Client connection failed: {reason_code}")
    
    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected = False
        print(f"⚠️ MQTT Test Client disconnected: {reason_code}")
    
    def on_message(self, client, userdata, msg):
        with self.lock:
            topic = msg.topic
            try:
                payload = json.loads(msg.payload.decode())
                timestamp = datetime.now(timezone.utc).isoformat()
                
                if topic not in self.received_messages:
                    self.received_messages[topic] = []
                
                self.received_messages[topic].append({
                    "payload": payload,
                    "timestamp": timestamp,
                    "qos": msg.qos
                })
                
                print(f"📨 Received MQTT message on {topic}: {payload}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to decode MQTT message on {topic}: {e}")
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            print(f"🔌 Connecting MQTT test client to {MQTT_BROKER}:{MQTT_PORT}")
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            print(f"❌ MQTT test client connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def clear_messages(self):
        """Clear received messages"""
        with self.lock:
            self.received_messages.clear()
    
    def get_messages(self, topic: str) -> List[Dict]:
        """Get messages for a specific topic"""
        with self.lock:
            return self.received_messages.get(topic, []).copy()
    
    def wait_for_message(self, topic: str, timeout: int = 10) -> Optional[Dict]:
        """Wait for a message on a specific topic"""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            messages = self.get_messages(topic)
            if messages:
                return messages[-1]  # Return latest message
            time.sleep(0.1)
        return None

class MediFleetMQTTTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.mqtt_client = MQTTTestClient()
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"[API] {method} {endpoint} -> {response.status_code}")
            return response
        except Exception as e:
            print(f"[ERROR] API request failed: {e}")
            raise
    
    def setup_test_environment(self) -> bool:
        """Setup test environment"""
        print("\n=== SETTING UP TEST ENVIRONMENT ===")
        
        # Connect MQTT test client
        if not self.mqtt_client.connect():
            print("❌ Failed to connect MQTT test client")
            return False
        
        # Reset robots to ensure clean state
        try:
            response = self.make_request("POST", "/robots/reset-all")
            if response.status_code == 200:
                print("✅ Robots reset to clean state")
            else:
                print(f"⚠️ Robot reset returned: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Robot reset failed: {e}")
        
        # Clear any existing MQTT messages
        self.mqtt_client.clear_messages()
        
        # Wait a moment for everything to settle
        time.sleep(2)
        
        return True
    
    def test_backend_connectivity(self) -> bool:
        """Test backend API connectivity"""
        print("\n=== TESTING BACKEND CONNECTIVITY ===")
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                print("✅ Backend API is accessible")
                return True
            else:
                print(f"❌ Backend API returned: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend API connectivity failed: {e}")
            return False
    
    def test_task_creation_mqtt(self) -> bool:
        """Test MQTT message publishing when creating a task"""
        print("\n=== TESTING TASK CREATION MQTT ===")
        
        # Clear previous messages
        self.mqtt_client.clear_messages()
        
        # Create a task
        task_data = {
            "destination": "PHARMACY",
            "priority": "medium"
        }
        
        print(f"📝 Creating task: {task_data}")
        response = self.make_request("POST", "/tasks", task_data)
        
        if response.status_code != 200:
            print(f"❌ Task creation failed: {response.status_code}")
            return False
        
        task = response.json()
        task_id = task["id"]
        print(f"✅ Task created with ID: {task_id}")
        
        # Wait for MQTT message on tasks/new
        print("⏳ Waiting for tasks/new MQTT message...")
        message = self.mqtt_client.wait_for_message("tasks/new", timeout=5)
        
        if not message:
            print("❌ No MQTT message received on tasks/new")
            return False
        
        # Verify message payload
        payload = message["payload"]
        expected_fields = ["task_id", "destination", "priority", "created_at"]
        
        print(f"📨 Received tasks/new message: {payload}")
        
        success = True
        for field in expected_fields:
            if field not in payload:
                print(f"❌ Missing field in payload: {field}")
                success = False
            else:
                print(f"✅ Field present: {field} = {payload[field]}")
        
        # Verify field values
        if payload.get("task_id") != task_id:
            print(f"❌ Task ID mismatch: expected {task_id}, got {payload.get('task_id')}")
            success = False
        
        if payload.get("destination") != "PHARMACY":
            print(f"❌ Destination mismatch: expected PHARMACY, got {payload.get('destination')}")
            success = False
        
        if payload.get("priority") != "medium":
            print(f"❌ Priority mismatch: expected medium, got {payload.get('priority')}")
            success = False
        
        return success
    
    def test_task_assignment_mqtt(self) -> bool:
        """Test MQTT message publishing when task is assigned"""
        print("\n=== TESTING TASK ASSIGNMENT MQTT ===")
        
        # Clear previous messages
        self.mqtt_client.clear_messages()
        
        # Create a task
        task_data = {
            "destination": "ICU",
            "priority": "high"
        }
        
        print(f"📝 Creating task for assignment test: {task_data}")
        response = self.make_request("POST", "/tasks", task_data)
        
        if response.status_code != 200:
            print(f"❌ Task creation failed: {response.status_code}")
            return False
        
        task = response.json()
        task_id = task["id"]
        print(f"✅ Task created with ID: {task_id}")
        
        # Wait for tasks/new message first
        print("⏳ Waiting for tasks/new message...")
        new_message = self.mqtt_client.wait_for_message("tasks/new", timeout=5)
        if not new_message:
            print("❌ No tasks/new message received")
            return False
        print("✅ tasks/new message received")
        
        # Wait for bidding to complete and tasks/assigned message
        print("⏳ Waiting for bidding to complete and tasks/assigned message...")
        assigned_message = self.mqtt_client.wait_for_message("tasks/assigned", timeout=15)
        
        if not assigned_message:
            print("❌ No MQTT message received on tasks/assigned")
            return False
        
        # Verify message payload
        payload = assigned_message["payload"]
        expected_fields = ["task_id", "robot_id", "destination", "distance"]
        
        print(f"📨 Received tasks/assigned message: {payload}")
        
        success = True
        for field in expected_fields:
            if field not in payload:
                print(f"❌ Missing field in payload: {field}")
                success = False
            else:
                print(f"✅ Field present: {field} = {payload[field]}")
        
        # Verify field values
        if payload.get("task_id") != task_id:
            print(f"❌ Task ID mismatch: expected {task_id}, got {payload.get('task_id')}")
            success = False
        
        if payload.get("destination") != "ICU":
            print(f"❌ Destination mismatch: expected ICU, got {payload.get('destination')}")
            success = False
        
        # Verify robot_id is not empty
        robot_id = payload.get("robot_id")
        if not robot_id:
            print("❌ Robot ID is empty")
            success = False
        else:
            print(f"✅ Robot assigned: {robot_id}")
        
        # Verify distance is a number
        distance = payload.get("distance")
        if not isinstance(distance, (int, float)):
            print(f"❌ Distance is not a number: {distance}")
            success = False
        else:
            print(f"✅ Distance: {distance}")
        
        return success
    
    def test_task_completion_mqtt(self) -> bool:
        """Test MQTT message publishing when task is completed"""
        print("\n=== TESTING TASK COMPLETION MQTT ===")
        
        # Clear previous messages
        self.mqtt_client.clear_messages()
        
        # Create a task and wait for assignment
        task_data = {
            "destination": "STORAGE",
            "priority": "low"
        }
        
        print(f"📝 Creating task for completion test: {task_data}")
        response = self.make_request("POST", "/tasks", task_data)
        
        if response.status_code != 200:
            print(f"❌ Task creation failed: {response.status_code}")
            return False
        
        task = response.json()
        task_id = task["id"]
        print(f"✅ Task created with ID: {task_id}")
        
        # Wait for assignment
        print("⏳ Waiting for task assignment...")
        assigned_message = self.mqtt_client.wait_for_message("tasks/assigned", timeout=15)
        
        if not assigned_message:
            print("❌ Task was not assigned, cannot test completion")
            return False
        
        robot_id = assigned_message["payload"].get("robot_id")
        print(f"✅ Task assigned to robot: {robot_id}")
        
        # Mark task as completed
        completion_time = datetime.now(timezone.utc).isoformat()
        update_data = {
            "status": "completed",
            "completed_at": completion_time
        }
        
        print(f"🏁 Marking task as completed: {update_data}")
        response = self.make_request("PATCH", f"/tasks/{task_id}", update_data)
        
        if response.status_code != 200:
            print(f"❌ Task completion update failed: {response.status_code}")
            return False
        
        print("✅ Task marked as completed")
        
        # Wait for tasks/complete message
        print("⏳ Waiting for tasks/complete MQTT message...")
        complete_message = self.mqtt_client.wait_for_message("tasks/complete", timeout=5)
        
        if not complete_message:
            print("❌ No MQTT message received on tasks/complete")
            return False
        
        # Verify message payload
        payload = complete_message["payload"]
        expected_fields = ["task_id", "robot_id", "completed_at"]
        
        print(f"📨 Received tasks/complete message: {payload}")
        
        success = True
        for field in expected_fields:
            if field not in payload:
                print(f"❌ Missing field in payload: {field}")
                success = False
            else:
                print(f"✅ Field present: {field} = {payload[field]}")
        
        # Verify field values
        if payload.get("task_id") != task_id:
            print(f"❌ Task ID mismatch: expected {task_id}, got {payload.get('task_id')}")
            success = False
        
        if payload.get("robot_id") != robot_id:
            print(f"❌ Robot ID mismatch: expected {robot_id}, got {payload.get('robot_id')}")
            success = False
        
        return success
    
    def test_full_workflow(self) -> bool:
        """Test complete workflow: create → assign → complete"""
        print("\n=== TESTING FULL WORKFLOW ===")
        
        # Clear previous messages
        self.mqtt_client.clear_messages()
        
        # Create task
        task_data = {
            "destination": "EMERGENCY",
            "priority": "urgent"
        }
        
        print(f"📝 Starting full workflow test with task: {task_data}")
        response = self.make_request("POST", "/tasks", task_data)
        
        if response.status_code != 200:
            print(f"❌ Task creation failed: {response.status_code}")
            return False
        
        task = response.json()
        task_id = task["id"]
        print(f"✅ Task created with ID: {task_id}")
        
        # Step 1: Verify tasks/new
        print("⏳ Step 1: Waiting for tasks/new message...")
        new_message = self.mqtt_client.wait_for_message("tasks/new", timeout=5)
        if not new_message:
            print("❌ Step 1 failed: No tasks/new message")
            return False
        print("✅ Step 1 passed: tasks/new message received")
        
        # Step 2: Verify tasks/assigned
        print("⏳ Step 2: Waiting for tasks/assigned message...")
        assigned_message = self.mqtt_client.wait_for_message("tasks/assigned", timeout=15)
        if not assigned_message:
            print("❌ Step 2 failed: No tasks/assigned message")
            return False
        
        robot_id = assigned_message["payload"].get("robot_id")
        print(f"✅ Step 2 passed: tasks/assigned message received (robot: {robot_id})")
        
        # Step 3: Complete task and verify tasks/complete
        completion_time = datetime.now(timezone.utc).isoformat()
        update_data = {
            "status": "completed",
            "completed_at": completion_time
        }
        
        print("🏁 Step 3: Completing task...")
        response = self.make_request("PATCH", f"/tasks/{task_id}", update_data)
        if response.status_code != 200:
            print(f"❌ Step 3 failed: Task completion update failed: {response.status_code}")
            return False
        
        print("⏳ Step 3: Waiting for tasks/complete message...")
        complete_message = self.mqtt_client.wait_for_message("tasks/complete", timeout=5)
        if not complete_message:
            print("❌ Step 3 failed: No tasks/complete message")
            return False
        
        print("✅ Step 3 passed: tasks/complete message received")
        
        # Verify all messages have correct task_id
        messages = [
            ("tasks/new", new_message),
            ("tasks/assigned", assigned_message),
            ("tasks/complete", complete_message)
        ]
        
        success = True
        for topic, message in messages:
            if message["payload"].get("task_id") != task_id:
                print(f"❌ Task ID mismatch in {topic}: expected {task_id}, got {message['payload'].get('task_id')}")
                success = False
        
        if success:
            print("🎉 Full workflow test PASSED: All MQTT messages published correctly!")
        else:
            print("❌ Full workflow test FAILED: Task ID mismatches detected")
        
        return success
    
    def check_backend_logs(self):
        """Check backend logs for MQTT-related messages"""
        print("\n=== CHECKING BACKEND LOGS ===")
        try:
            # Check supervisor logs for backend
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                mqtt_logs = [line for line in logs.split('\n') if 'MQTT' in line or 'mqtt' in line]
                
                if mqtt_logs:
                    print("📋 Recent MQTT-related log entries:")
                    for log in mqtt_logs[-10:]:  # Show last 10 MQTT logs
                        print(f"   {log}")
                else:
                    print("⚠️ No MQTT-related log entries found in recent logs")
            else:
                print("⚠️ Could not read backend logs")
                
        except Exception as e:
            print(f"⚠️ Error reading backend logs: {e}")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all MQTT tests"""
        print("🚀 STARTING MEDIFLEET MQTT INTEGRATION TESTS")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test environment setup failed")
            return {}
        
        # Test backend connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity test failed")
            return {}
        
        test_results = {}
        
        # Run individual tests
        tests = [
            ("Task Creation MQTT", self.test_task_creation_mqtt),
            ("Task Assignment MQTT", self.test_task_assignment_mqtt),
            ("Task Completion MQTT", self.test_task_completion_mqtt),
            ("Full Workflow", self.test_full_workflow)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*60}")
                print(f"🧪 RUNNING: {test_name}")
                print(f"{'='*60}")
                
                result = test_func()
                test_results[test_name] = result
                
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"\n🎯 {test_name}: {status}")
                
                # Brief pause between tests
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                test_results[test_name] = False
        
        # Check backend logs
        self.check_backend_logs()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 MQTT INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name:25} : {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL MQTT TESTS PASSED - MQTT integration is working correctly!")
        else:
            print("⚠️  SOME MQTT TESTS FAILED - MQTT integration needs attention!")
        
        return test_results
    
    def cleanup(self):
        """Cleanup test resources"""
        print("\n=== CLEANING UP ===")
        self.mqtt_client.disconnect()
        print("✅ MQTT test client disconnected")

def main():
    """Main test execution"""
    print("MediFleet MQTT Integration Test Suite")
    print("Testing MQTT publishing to test.mosquitto.org:1883 for task events")
    print()
    
    tester = MediFleetMQTTTester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        all_passed = all(results.values()) if results else False
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Test suite failed with error: {e}")
        sys.exit(1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()