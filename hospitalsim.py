import heapq
import os 
import pygame
import sys
import math
import time
import random
import json
import threading
import paho.mqtt.client as mqtt

# --- MQTT Configuration ---
MQTT_BROKER = "mqtt.medifleet.local" # Use hostname provided
MQTT_PORT = 1883
MQTT_KEEP_ALIVE = 60

# Topics
TASK_NEW_TOPIC = "tasks/new"
ROBOTS_BIDS_TOPIC = "robots/bids" # For robots to publish bids
TASKS_ASSIGNED_TOPIC = "tasks/assigned" # For server to assign (Sim listens conceptually)
ROBOTS_STATUS_TOPIC = "robots/status"
TASKS_COMPLETE_TOPIC = "tasks/complete"

# Global MQTT Client
mqtt_client = None
mqtt_connected = False

# --- A* Pathfinding Code (Unchanged) ---
class Node:
    """A node class for A* Pathfinding."""
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position; self.g = 0; self.h = 0; self.f = 0
    def __eq__(self, other): return self.position == other.position
    def __lt__(self, other): return self.f < other.f
    def __hash__(self): return hash(self.position)

def astar(grid, start_pos, end_pos):
    rows, cols = len(grid), len(grid[0])
    start_node = Node(None, start_pos); end_node = Node(None, end_pos)
    open_list = []; closed_set = set(); heapq.heappush(open_list, start_node)
    while open_list:
        current_node = heapq.heappop(open_list)
        if current_node.position in closed_set: continue
        closed_set.add(current_node.position)
        if current_node == end_node:
            path = []; current = current_node
            while current is not None: path.append(current.position); current = current.parent
            return path[::-1] # Return reversed path
        for move_pos, move_cost in [((0,-1),10),((0,1),10),((-1,0),10),((1,0),10),((-1,-1),14),((-1,1),14),((1,-1),14),((1,1),14)]:
            node_position = (current_node.position[0] + move_pos[0], current_node.position[1] + move_pos[1])
            if not (0 <= node_position[0] < rows and 0 <= node_position[1] < cols): continue
            if grid[node_position[0]][node_position[1]] != 0: continue
            if node_position in closed_set: continue
            new_node = Node(current_node, node_position); new_node.g = current_node.g + move_cost
            dx=abs(new_node.position[0]-end_node.position[0]); dy=abs(new_node.position[1]-end_node.position[1])
            new_node.h = 10*(dx+dy)+(14-2*10)*min(dx,dy); new_node.f = new_node.g + new_node.h
            if any(open_node == new_node and new_node.g >= open_node.g for open_node in open_list): continue
            heapq.heappush(open_list, new_node)
    return None

# --- Pygame Simulation Code ---
GRID_ROWS = 15; GRID_COLS = 15; CELL_SIZE = 50
WIDTH = GRID_COLS * CELL_SIZE; HEIGHT = GRID_ROWS * CELL_SIZE; FPS = 10
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(128,128,128); LIGHT_GRAY=(200,200,200)
RED=(255,0,0); GREEN=(0,255,0); BLUE=(0,0,255); YELLOW=(255,255,0); PURPLE=(128,0,128)
CYAN=(0,255,255); MAGENTA=(255,0,255); ORANGE=(255,165,0); PATH_COLOR=(50,200,50); BID_HIGHLIGHT=(255,100,100)
WAYPOINTS = {"ENT":(1,3),"PHA":(4,3),"ICU":(4,1),"R101":(4,5),"EMR":(7,3),"STO":(10,3)}
WAYPOINT_COLORS = {"ENT":WHITE,"PHA":BLUE,"ICU":RED,"R101":GREEN,"EMR":YELLOW,"STO":PURPLE}
ROBOT_COLORS = {"R1":CYAN,"R2":MAGENTA,"R3":ORANGE}; ROBOT_IDS = ["R1","R2","R3"]
PRIORITY_MAP = {"high": 1, "medium": 5, "low": 10} # Map MQTT priority strings
grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
tasks_lock = threading.Lock() # Lock for accessing tasks list from MQTT thread
robots_lock = threading.Lock() # Lock for accessing robots dict

class Task:
    def __init__(self, task_id, target_waypoint, priority_str):
        self.id = task_id
        self.target_waypoint = target_waypoint.upper() # Ensure uppercase
        self.target_pos = WAYPOINTS.get(self.target_waypoint) # Use .get for safety
        self.priority = PRIORITY_MAP.get(priority_str.lower(), PRIORITY_MEDIUM) # Map priority string
        self.status = "ANNOUNCED" # ANNOUNCED, BIDDING, ASSIGNED, COMPLETE
        self.assigned_robot = None
        self.bids = {} # {robot_id: bid_value}
        self.created_at = time.time() # Store creation time

class Robot:
    def __init__(self, robot_id, start_pos, color):
        self.id = robot_id; self.pos = start_pos; self.color = color
        self.offset_x = random.randint(-CELL_SIZE//6, CELL_SIZE//6); self.offset_y = random.randint(-CELL_SIZE//6, CELL_SIZE//6)
        self.path = []; self.path_index = 0; self.status = "IDLE"; self.target_waypoint = None; self.current_task_id = None
        self.energy = 100.0; self.low_energy_threshold = 20.0; self.energy_drain_per_step = 0.5
        self.last_status_publish_time = 0

    def assign_task(self, task):
        if not task.target_pos:
            print(f"!!! {self.id} cannot find waypoint {task.target_waypoint} for Task {task.id}.")
            self.status = "IDLE"; return False
        path = astar(grid, self.pos, task.target_pos)
        if path and len(path) > 1:
            self.path = path; self.path_index = 1; self.status = "MOVING"; self.target_waypoint = task.target_waypoint
            self.current_task_id = task.id; task.status = "ASSIGNED"; task.assigned_robot = self.id
            print(f"{self.id} assigned Task {task.id} ({task.target_waypoint}). Path: {len(self.path)-1} steps."); return True
        else:
            print(f"!!! {self.id} could not find path for Task {task.id} or already at destination.")
            self.status = "IDLE"; return False

    def move(self):
        global tasks # Need access to global tasks list to mark completion
        if self.status == "MOVING":
            if self.path_index < len(self.path):
                next_pos = self.path[self.path_index]; r1,c1=self.pos; r2,c2=next_pos
                move_cost_factor = 1.4 if abs(r1-r2)==1 and abs(c1-c2)==1 else 1.0
                energy_cost = self.energy_drain_per_step * move_cost_factor
                if self.energy >= energy_cost:
                    self.energy -= energy_cost; self.pos = next_pos; self.path_index += 1
                else:
                    print(f"!!! {self.id} ran out of energy at {self.pos}!"); self.status = "IDLE"
            else:
                print(f"{self.id} reached {self.target_waypoint} for Task {self.current_task_id}.")
                self.status = "IDLE"; completed_task_id = self.current_task_id
                # Publish completion BEFORE resetting internal state
                self.publish_task_complete(completed_task_id)
                self.path = []; self.path_index = 0; self.current_task_id = None
                # Mark task as complete in the main list
                with tasks_lock:
                    for task in tasks:
                        if task.id == completed_task_id:
                            task.status = "COMPLETE"
                            print(f"--- Task {task.id} ({task.target_waypoint}) marked COMPLETE ---")
                            break


    def calculate_bid(self, task):
        if self.status != "IDLE" or self.energy < self.low_energy_threshold: return None
        if not task.target_pos: return None # Cannot bid if waypoint unknown

        path = astar(grid, self.pos, task.target_pos)
        distance_cost = float('inf')
        if path and len(path) > 1:
             # Re-calculate path g-cost properly for bidding
             end_node_sim = Node(None, task.target_pos); open_list_sim = []; closed_set_sim = set()
             start_node_sim = Node(None, self.pos); heapq.heappush(open_list_sim, start_node_sim)
             path_g_cost = float('inf')
             while open_list_sim:
                 current_node_sim = heapq.heappop(open_list_sim);
                 if current_node_sim.position in closed_set_sim: continue; closed_set_sim.add(current_node_sim.position)
                 if current_node_sim == end_node_sim: path_g_cost = current_node_sim.g; break
                 for move_pos, move_cost in [((0,-1),10),((0,1),10),((-1,0),10),((1,0),10),((-1,-1),14),((-1,1),14),((1,-1),14),((1,1),14)]:
                     node_pos_sim=(current_node_sim.position[0]+move_pos[0], current_node_sim.position[1]+move_pos[1])
                     if not(0<=node_pos_sim[0]<GRID_ROWS and 0<=node_pos_sim[1]<GRID_COLS): continue
                     if grid[node_pos_sim[0]][node_pos_sim[1]]!=0: continue;
                     if node_pos_sim in closed_set_sim: continue
                     new_node_sim=Node(current_node_sim, node_pos_sim); new_node_sim.g = current_node_sim.g + move_cost
                     if any(on==new_node_sim and new_node_sim.g>=on.g for on in open_list_sim): continue
                     heapq.heappush(open_list_sim, new_node_sim)
             distance_cost = path_g_cost
        elif self.pos == task.target_pos:
            distance_cost = 0 # Already there

        if distance_cost == float('inf'):
            print(f"!!! {self.id} cannot calculate path for bid on Task {task.id}.")
            return None # Cannot bid if no path found

        energy_factor = (100.0 - self.energy) / 10.0 # Cost increases as energy decreases
        priority_factor = task.priority * 5 # Lower priority number = lower cost = higher chance to win
        bid = distance_cost + energy_factor - priority_factor # NOTE: Subtracting priority factor

        print(f"{self.id} calculated bid for Task {task.id} ({task.target_waypoint}): Dist={distance_cost:.1f}, EnergyF={energy_factor:.1f}, PrioF={-priority_factor:.1f} => Bid={bid:.1f}")

        # --- Publish Bid via MQTT ---
        if mqtt_connected:
            bid_payload = {
                "task_id": task.id,
                "robot_id": self.id,
                "bid_value": bid, # Send the calculated cost
                "timestamp": time.time()
            }
            mqtt_client.publish(ROBOTS_BIDS_TOPIC, json.dumps(bid_payload), qos=1)
            # print(f"Published bid for Task {task.id} to {ROBOTS_BIDS_TOPIC}") # Optional log

        return bid

    def publish_status(self):
        """Publishes robot status to MQTT."""
        global mqtt_connected, mqtt_client
        current_time = time.time()
        # Publish status approx every 5 seconds or if status changes
        if mqtt_connected and (current_time - self.last_status_publish_time > 5):
            # Find current location name
            current_location_name = "MOVING"
            min_dist = float('inf')
            for name, pos in WAYPOINTS.items():
                dist = math.sqrt((self.pos[0]-pos[0])**2 + (self.pos[1]-pos[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    current_location_name = name
            # If still far from any waypoint, report approximate grid pos
            if min_dist > 1.5: # Threshold distance to snap to waypoint name
                 current_location_name = f"Grid({self.pos[0]},{self.pos[1]})"


            status_payload = {
                "robot_id": self.id,
                "location": current_location_name, # Report nearest waypoint or grid pos
                "battery": int(self.energy),
                "status": self.status.lower(), # idle, bidding, moving
                "timestamp": current_time
            }
            mqtt_client.publish(ROBOTS_STATUS_TOPIC, json.dumps(status_payload), qos=1)
            self.last_status_publish_time = current_time
            # print(f"Published status for {self.id}") # Optional log

    def publish_task_complete(self, task_id):
        """Publishes task completion to MQTT."""
        global mqtt_connected, mqtt_client
        if mqtt_connected:
            complete_payload = {
                "task_id": task_id,
                "robot_id": self.id,
                "completed_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            mqtt_client.publish(TASKS_COMPLETE_TOPIC, json.dumps(complete_payload), qos=1)
            print(f">>> {self.id} Published completion for Task {task_id}")


    def draw(self, screen, font):
        # (Drawing code is the same as before - keep it here)
        r, c = self.pos
        center_x = c * CELL_SIZE + CELL_SIZE // 2 + self.offset_x
        center_y = r * CELL_SIZE + CELL_SIZE // 2 + self.offset_y
        radius = CELL_SIZE // 3
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
        border_color, border_width = BLACK, 1
        if self.status == "MOVING": border_color, border_width = WHITE, 2
        elif self.status == "BIDDING": border_color, border_width = BID_HIGHLIGHT, 3
        pygame.draw.circle(screen, border_color, (center_x, center_y), radius, border_width)
        id_text = font.render(self.id, True, BLACK); id_rect = id_text.get_rect(center=(center_x, center_y - radius // 4)); screen.blit(id_text, id_rect)
        energy_text = font.render(f"{self.energy:.0f}%", True, BLACK); energy_rect = energy_text.get_rect(center=(center_x, center_y + radius // 4)); screen.blit(energy_text, energy_rect)
        if self.status == "MOVING" and self.path:
            path_points = [(center_x, center_y)]
            for i in range(self.path_index, len(self.path)):
                 pr, pc = self.path[i]; path_points.append((pc * CELL_SIZE + CELL_SIZE // 2, pr * CELL_SIZE + CELL_SIZE // 2))
            if len(path_points) >= 2: pygame.draw.lines(screen, self.color, False, path_points, 3)


# --- Pygame Drawing Functions (Unchanged) ---
def draw_grid(screen):
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE); pygame.draw.rect(screen, GRAY, rect, 1)

def draw_waypoints(screen, font):
     for name, pos in WAYPOINTS.items():
        r, c = pos; rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = WAYPOINT_COLORS.get(name, BLACK); pygame.draw.rect(screen, color, rect); pygame.draw.rect(screen, BLACK, rect, 1)
        text_color = BLACK if sum(color)>384 else WHITE; text = font.render(name, True, text_color); text_rect = text.get_rect(center=rect.center); screen.blit(text, text_rect)

def draw_tasks(screen, font, tasks):
    y_offset = 10; x_offset = 10
    max_width = WIDTH - 2 * x_offset
    for task in tasks:
        prio_map_rev = {v: k for k, v in PRIORITY_MAP.items()} # Reverse map for display
        prio_str = prio_map_rev.get(task.priority, "?").upper()[0] # Get 'H', 'M', 'L'
        robot_str = f"-> {task.assigned_robot}" if task.assigned_robot else ""
        text_str = f"T{task.id}[{prio_str}]: {task.target_waypoint} ({task.status}{robot_str})"
        text_surface = font.render(text_str, True, BLACK, LIGHT_GRAY); text_rect = text_surface.get_rect(topleft=(x_offset, y_offset)); screen.blit(text_surface, text_rect)
        y_offset += font.get_height() + 2 # Dynamic spacing based on font height


# --- MQTT Callback Functions ---
def on_connect(client, userdata, flags, rc, properties=None):
    global mqtt_connected
    if rc == 0:
        print(f"Connected successfully to MQTT Broker: {MQTT_BROKER}")
        mqtt_connected = True
        # Subscribe to the topic where new tasks are announced
        client.subscribe(TASK_NEW_TOPIC, qos=1)
        print(f"Subscribed to {TASK_NEW_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")
        mqtt_connected = False

def on_disconnect(client, userdata, rc, properties=None):
     global mqtt_connected
     print(f"Disconnected from MQTT Broker with result code {rc}")
     mqtt_connected = False
     # Implement reconnection logic if desired

def on_message(client, userdata, msg):
    global tasks, task_counter, robots # Access global lists/dicts
    print(f"Received message on topic {msg.topic}") # Basic log
    if msg.topic == TASK_NEW_TOPIC:
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            print(f"Payload: {payload}")

            task_id = payload.get("task_id", f"mqtt_{task_counter+1}") # Use provided ID or generate one
            destination = payload.get("destination")
            priority = payload.get("priority", "medium") # Default to medium

            if not destination or destination.upper() not in WAYPOINTS:
                 print(f"Invalid or missing destination in task payload: {destination}")
                 return
            if destination.upper() == "ENT":
                 print("Cannot assign task to ENT")
                 return

            # Check if task ID already exists
            with tasks_lock:
                 if any(t.id == task_id for t in tasks):
                      print(f"Task ID {task_id} already exists. Ignoring.")
                      return

                 task_counter += 1 # Increment counter even if using provided ID for uniqueness fallback
                 new_task = Task(task_id, destination, priority)
                 tasks.append(new_task)
                 print(f"--- MQTT Task {new_task.id} ({new_task.target_waypoint}) received with priority {new_task.priority} ---")

                 # Trigger bidding phase for this new task
                 with robots_lock:
                     for robot in robots.values():
                          if robot.status == "IDLE" and robot.energy >= robot.low_energy_threshold:
                              robot.status = "BIDDING" # Visually indicate bidding

        except json.JSONDecodeError:
            print(f"Error decoding JSON payload on {msg.topic}")
        except Exception as e:
            print(f"Error processing message on {msg.topic}: {e}")

# --- MQTT Setup Function ---
def setup_mqtt():
    global mqtt_client
    client_id = f"pygame_sim_{random.randint(0, 1000)}"
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    try:
        print(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEP_ALIVE)
        # Start the MQTT network loop in a separate thread to avoid blocking Pygame
        mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
        mqtt_thread.daemon = True # Allows program to exit even if thread is running
        mqtt_thread.start()
        print("MQTT thread started.")
    except Exception as e:
        print(f"MQTT Connection Error: {e}")
        print("MQTT features will be disabled.")


# --- Main Simulation Loop ---
# --- Main Simulation Loop ---
def main():
    global tasks, task_counter, robots # Allow modification by MQTT callback

    setup_mqtt() # Initialize and connect MQTT

    # --- Initialize Pygame and Font FIRST ---
    pygame.init()
    pygame.font.init() # Ensure font module is ready
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    clock = pygame.time.Clock() # Initialize clock after pygame.init()
    # --- END Pygame Init ---

    # --- Manual Centering Logic (using initialized display info) ---
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    # Calculate desired window position
    window_width = WIDTH
    window_height = HEIGHT + 150 # Includes task list space
    pos_x = (screen_width - window_width) // 2
    pos_y = (screen_height - window_height) // 2

    # Set the environment variable BEFORE setting the display mode
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"
    # --- END Centering Logic ---

    # --- Set Display Mode LAST ---
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Hospital Swarm Simulation - MQTT + CNP Bidding")
    # --- END Display Mode ---


    # --- Robot Initialization (Place robots separately) ---
    start_pos_ent = WAYPOINTS["ENT"] # Center start position (e.g., (1, 3))
    start_positions = {
        "R1": (start_pos_ent[0], start_pos_ent[1] - 1), # Left (e.g., (1, 2))
        "R2": start_pos_ent,                           # Center (e.g., (1, 3))
        "R3": (start_pos_ent[0], start_pos_ent[1] + 1), # Right (e.g., (1, 4))
    }
    with robots_lock:
        robots = {} # Initialize empty dict first
        for robot_id in ROBOT_IDS:
             r, c = start_positions[robot_id]
             if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS and grid[r][c] == 0:
                 robots[robot_id] = Robot(robot_id, start_positions[robot_id], ROBOT_COLORS[robot_id])
             else:
                  print(f"Warning: Invalid start position {(r,c)} for {robot_id}. Placing at ENT {start_pos_ent}.")
                  robots[robot_id] = Robot(robot_id, start_pos_ent, ROBOT_COLORS[robot_id]) # Fallback
    # --- END Robot Initialization ---

    tasks = [] # Task list managed globally
    task_counter = 0

    running = True
    while running:
        # --- Pygame Event Handling ---
        # ... (rest of the event handling loop) ...

        # --- Contract Net Protocol (CNP) Logic ---
        # ... (rest of CNP logic) ...

        # --- Robot Movement & Status Publishing ---
        # ... (rest of movement logic) ...

        # --- Drawing ---
        screen.fill(BLACK)
        draw_grid(screen)
        # --- THIS CALL SHOULD NOW WORK ---
        draw_waypoints(screen, font)
        # ---------------------------------

        with robots_lock:
            for robot in robots.values():
                robot.draw(screen, small_font) # Correctly uses small_font here

        # Draw Task List Area
        # ... (rest of task drawing) ...

        # Draw MQTT Status Indicator
        # ... (rest of MQTT status drawing) ...


        pygame.display.flip()
        clock.tick(FPS)

    # Cleanup
    # ... (rest of cleanup code) ...

if __name__ == "__main__":
    main()
