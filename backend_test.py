#!/usr/bin/env python3
"""
Backend Test Suite for Robot Task Assignment Bidding Algorithm
Tests the critical bug fix for robot bidding algorithm in server.py
"""

import requests
import json
import time
import sys
from typing import Dict, List, Optional

# Backend URL from environment
BACKEND_URL = "https://medifleet.preview.emergentagent.com/api"

class BiddingAlgorithmTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Distance matrix (same as backend server.py)
        self.distances = {
            "ENTRANCE": {"ENTRANCE": 0, "PHARMACY": 50, "ICU": 85, "ROOM_101": 85, "EMERGENCY": 120, "STORAGE": 150},
            "PHARMACY": {"ENTRANCE": 50, "PHARMACY": 0, "ICU": 95, "ROOM_101": 95, "EMERGENCY": 70, "STORAGE": 110},
            "ICU": {"ENTRANCE": 85, "PHARMACY": 95, "ICU": 0, "ROOM_101": 140, "EMERGENCY": 120, "STORAGE": 150},
            "ROOM_101": {"ENTRANCE": 85, "PHARMACY": 95, "ICU": 140, "ROOM_101": 0, "EMERGENCY": 120, "STORAGE": 150},
            "EMERGENCY": {"ENTRANCE": 120, "PHARMACY": 70, "ICU": 120, "ROOM_101": 120, "EMERGENCY": 0, "STORAGE": 90},
            "STORAGE": {"ENTRANCE": 150, "PHARMACY": 110, "ICU": 150, "ROOM_101": 150, "EMERGENCY": 90, "STORAGE": 0}
        }
    
    def calculate_bid_score(self, robot: Dict, destination: str) -> float:
        """Calculate bid score using same formula as backend"""
        location = robot.get("location", "ENTRANCE")
        battery = robot.get("battery", 100)
        
        # Get distance from robot's location to destination
        dest_distances = self.distances.get(location, {})
        distance = dest_distances.get(destination, 100)
        
        # Avoid division by zero
        if distance == 0:
            distance = 1
        
        # Bid score formula: (1000 / distance) * (battery / 100)
        bid_score = (1000 / distance) * (battery / 100)
        return bid_score
    
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
            
            print(f"[REQUEST] {method} {url} -> {response.status_code}")
            if data:
                print(f"[DATA] {json.dumps(data, indent=2)}")
            
            return response
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            raise
    
    def reset_robots(self) -> bool:
        """Reset all robots to ENTRANCE location"""
        print("\n=== RESETTING ROBOTS ===")
        try:
            response = self.make_request("POST", "/robots/reset-all")
            if response.status_code == 200:
                print("✅ All robots reset to ENTRANCE")
                return True
            else:
                print(f"❌ Failed to reset robots: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error resetting robots: {e}")
            return False
    
    def get_robots(self) -> List[Dict]:
        """Get all robots"""
        try:
            response = self.make_request("GET", "/robots")
            if response.status_code == 200:
                robots = response.json()
                print(f"📋 Retrieved {len(robots)} robots")
                for robot in robots:
                    print(f"   - {robot['name']}: {robot['status']} at {robot['location']} (Battery: {robot['battery']}%)")
                return robots
            else:
                print(f"❌ Failed to get robots: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting robots: {e}")
            return []
    
    def create_task(self, destination: str, priority: str = "medium") -> Optional[Dict]:
        """Create a new task"""
        print(f"\n=== CREATING TASK TO {destination} ===")
        task_data = {
            "destination": destination,
            "priority": priority
        }
        
        try:
            response = self.make_request("POST", "/tasks", task_data)
            if response.status_code == 200:
                task = response.json()
                print(f"✅ Task created: {task['id']} -> {destination}")
                return task
            else:
                print(f"❌ Failed to create task: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating task: {e}")
            return None
    
    def wait_for_task_assignment(self, task_id: str, timeout: int = 15) -> Optional[Dict]:
        """Wait for task to be assigned to a robot"""
        print(f"⏳ Waiting for task {task_id} assignment...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.make_request("GET", f"/tasks/{task_id}")
                if response.status_code == 200:
                    task = response.json()
                    status = task.get("status", "")
                    print(f"   Status: {status}")
                    
                    if status == "assigned":
                        print(f"✅ Task assigned to robot: {task.get('robot_name', 'Unknown')}")
                        return task
                    elif status in ["pending", "bidding"]:
                        time.sleep(1)
                        continue
                    else:
                        print(f"❌ Unexpected task status: {status}")
                        return task
                else:
                    print(f"❌ Failed to get task: {response.status_code}")
                    return None
            except Exception as e:
                print(f"❌ Error checking task: {e}")
                return None
        
        print(f"⏰ Timeout waiting for task assignment")
        return None
    
    def predict_winner(self, robots: List[Dict], destination: str) -> Optional[Dict]:
        """Predict which robot should win based on bid scores"""
        idle_robots = [r for r in robots if r.get("status") == "idle"]
        if not idle_robots:
            return None
        
        best_robot = None
        best_score = 0
        
        print(f"\n📊 BID SCORE CALCULATION FOR {destination}:")
        for robot in idle_robots:
            score = self.calculate_bid_score(robot, destination)
            location = robot.get("location", "ENTRANCE")
            battery = robot.get("battery", 100)
            distance = self.distances.get(location, {}).get(destination, 100)
            
            print(f"   {robot['name']}: Location={location}, Battery={battery}%, Distance={distance}m")
            print(f"   → Bid Score = (1000/{distance}) * ({battery}/100) = {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_robot = robot
        
        if best_robot:
            print(f"🏆 Predicted winner: {best_robot['name']} (Score: {best_score:.2f})")
        
        return best_robot
    
    def verify_robot_status(self, expected_busy_robot_id: str, all_robots: List[Dict]) -> bool:
        """Verify that only the assigned robot is busy"""
        print(f"\n🔍 VERIFYING ROBOT STATUS:")
        
        current_robots = self.get_robots()
        if not current_robots:
            return False
        
        success = True
        for robot in current_robots:
            expected_status = "busy" if robot["id"] == expected_busy_robot_id else "idle"
            actual_status = robot["status"]
            
            if actual_status == expected_status:
                print(f"✅ {robot['name']}: {actual_status} (correct)")
            else:
                print(f"❌ {robot['name']}: {actual_status} (expected: {expected_status})")
                success = False
        
        return success
    
    def test_task_to_destination(self, destination: str) -> bool:
        """Test task assignment to a specific destination"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING TASK TO {destination}")
        print(f"{'='*60}")
        
        # Step 1: Reset robots
        if not self.reset_robots():
            return False
        
        time.sleep(2)  # Allow reset to complete
        
        # Step 2: Get current robot state
        robots = self.get_robots()
        if not robots:
            print("❌ No robots available")
            return False
        
        # Step 3: Predict winner
        predicted_winner = self.predict_winner(robots, destination)
        if not predicted_winner:
            print("❌ No idle robots available for bidding")
            return False
        
        # Step 4: Create task
        task = self.create_task(destination)
        if not task:
            return False
        
        # Step 5: Wait for assignment
        assigned_task = self.wait_for_task_assignment(task["id"])
        if not assigned_task:
            return False
        
        # Step 6: Verify assignment
        assigned_robot_id = assigned_task.get("robot_id")
        assigned_robot_name = assigned_task.get("robot_name")
        
        print(f"\n📋 ASSIGNMENT VERIFICATION:")
        print(f"   Expected: {predicted_winner['name']} (ID: {predicted_winner['id']})")
        print(f"   Actual:   {assigned_robot_name} (ID: {assigned_robot_id})")
        
        assignment_correct = assigned_robot_id == predicted_winner["id"]
        if assignment_correct:
            print("✅ Correct robot assigned!")
        else:
            print("❌ Wrong robot assigned!")
        
        # Step 7: Verify robot status
        status_correct = self.verify_robot_status(assigned_robot_id, robots)
        
        # Overall result
        success = assignment_correct and status_correct
        print(f"\n🎯 TEST RESULT FOR {destination}: {'✅ PASS' if success else '❌ FAIL'}")
        
        return success
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all test scenarios"""
        print("🚀 STARTING ROBOT BIDDING ALGORITHM TESTS")
        print("=" * 80)
        
        test_results = {}
        
        # Test scenarios from the review request
        test_destinations = ["ICU", "PHARMACY", "STORAGE"]
        
        for destination in test_destinations:
            try:
                result = self.test_task_to_destination(destination)
                test_results[destination] = result
                time.sleep(3)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test for {destination} failed with error: {e}")
                test_results[destination] = False
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = len(test_results)
        
        for destination, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {destination:12} : {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Bidding algorithm is working correctly!")
        else:
            print("⚠️  SOME TESTS FAILED - Bidding algorithm needs attention!")
        
        return test_results

def main():
    """Main test execution"""
    print("Robot Task Assignment Bidding Algorithm Test Suite")
    print("Testing critical bug fix in backend/server.py process_bidding() function")
    print()
    
    tester = BiddingAlgorithmTester()
    
    try:
        # Test backend connectivity
        print("🔗 Testing backend connectivity...")
        response = tester.make_request("GET", "/")
        if response.status_code != 200:
            print(f"❌ Backend not accessible: {response.status_code}")
            sys.exit(1)
        print("✅ Backend is accessible")
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"💥 Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()