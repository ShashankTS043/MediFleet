#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Critical bug: MQTT messages only published for PHARMACY destination. Need to publish for ALL destinations (ENTRANCE, ICU, PHARMACY, ROOM_101, EMERGENCY, STORAGE)"

backend:
  - task: "Fix MQTT publishing for all destinations"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Enhanced MQTT implementation with improved connection handling. Added explicit print statements, wait_for_publish with timeout, on_publish callback, auto-reconnect logic. Removed any connection-check barriers - now publishes even if not connected (client buffers). Added verbose logging at each publish point to track all destinations. No destination-specific conditions exist in code."
      - working: true
        agent: "testing"
        comment: "MQTT PUBLISHING VERIFIED FOR ALL DESTINATIONS. Comprehensive testing confirms MQTT messages are published successfully for all 6 destinations (ENTRANCE, ICU, PHARMACY, ROOM_101, EMERGENCY, STORAGE). Backend logs show 'Publishing MQTT for destination: X' for every destination. All tasks/new events published correctly. Tasks/assigned and tasks/complete events also working for destinations with available robots. Bug fix confirmed - MQTT publishing no longer limited to PHARMACY only."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 4
  run_ui: false

test_plan:
  current_focus:
    - "Fix MQTT publishing for all destinations"
  stuck_tasks: []
  test_all: false
  test_priority: "critical_first"

agent_communication:
  - agent: "main"
    message: "Fixed MQTT publishing to work for ALL destinations. Enhanced publish_mqtt_message() to: 1) Remove mqtt_connected check - always publish (client buffers), 2) Add wait_for_publish() with 5s timeout, 3) Add on_publish callback for confirmation, 4) Add auto-reconnect on disconnect, 5) Added verbose print statements at each publish location with destination name. Added print statements in create_task (tasks/new), process_bidding (tasks/assigned), update_task (tasks/complete). No destination filtering exists. Need to test with ICU, ROOM_101, EMERGENCY, STORAGE to verify all destinations work."
  - agent: "testing"
    message: "CRITICAL BUG FIX VERIFIED: MQTT publishing now works for ALL destinations. Tested all 6 destinations specified in review request. Results: tasks/new messages published successfully for ENTRANCE, ICU, PHARMACY, ROOM_101, EMERGENCY, STORAGE (6/6 = 100%). Backend logs confirm 'Publishing MQTT for destination: X' for every destination. Tasks/assigned and tasks/complete events also working correctly when robots are available. Original bug (MQTT only for PHARMACY) is FIXED. The main agent's implementation is working correctly."