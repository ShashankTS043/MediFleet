import heapq
import pygame
import sys
import math
import time
import random
import os

# --- A* Pathfinding Code (Optimized) ---
# ... (Node class and astar function remain the same) ...
class Node:
    def __init__(self, parent=None, position=None): self.parent=parent; self.position=position; self.g=0; self.h=0; self.f=0
    def __eq__(self, other): return self.position == other.position
    def __lt__(self, other): return self.f < other.f
    def __hash__(self): return hash(self.position)

def astar(grid, start_pos, end_pos):
    rows, cols = len(grid), len(grid[0]); start_node=Node(None, start_pos); end_node=Node(None, end_pos)
    open_list_heap = []; heapq.heappush(open_list_heap, start_node)
    open_list_dict = {start_node.position: start_node}
    closed_set = set()
    path_calculation_start_time = time.time(); nodes_processed = 0
    while open_list_heap:
        if time.time() - path_calculation_start_time > 0.25: return None
        current_node = heapq.heappop(open_list_heap); nodes_processed += 1
        if current_node.position in open_list_dict: del open_list_dict[current_node.position]
        if current_node.position in closed_set: continue
        closed_set.add(current_node.position)
        if current_node == end_node:
            path=[]; current=current_node
            while current is not None: path.append(current.position); current=current.parent
            return path[::-1]
        for move_pos, move_cost in [((0,-1),10),((0,1),10),((-1,0),10),((1,0),10),((-1,-1),14),((-1,1),14),((1,-1),14),((1,1),14)]:
            node_position = (current_node.position[0]+move_pos[0], current_node.position[1]+move_pos[1])
            if not (0<=node_position[0]<rows and 0<=node_position[1]<cols): continue
            if grid[node_position[0]][node_position[1]] == 1: continue
            if node_position in closed_set: continue
            new_node=Node(current_node, node_position); new_node.g=current_node.g+move_cost
            dx=abs(new_node.position[0]-end_node.position[0]); dy=abs(new_node.position[1]-end_node.position[1])
            new_node.h=10*(dx+dy)+(14-2*10)*min(dx,dy); new_node.f=new_node.g+new_node.h
            if node_position in open_list_dict and new_node.g >= open_list_dict[node_position].g: continue
            heapq.heappush(open_list_heap, new_node)
            open_list_dict[node_position] = new_node
    return None

# --- Pygame Simulation Constants ---
# ... (Constants unchanged) ...
GRID_ROWS=12; GRID_COLS=7; CELL_SIZE=75
WIDTH=GRID_COLS*CELL_SIZE; HEIGHT=GRID_ROWS*CELL_SIZE; FPS=5
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(128,128,128); LIGHT_GRAY=(200,200,200)
RED=(255,0,0); GREEN=(0,255,0); BLUE=(0,0,255); YELLOW=(255,255,0); PURPLE=(128,0,128)
CYAN=(0,255,255); MAGENTA=(255,0,255); ORANGE=(255,165,0); PATH_COLOR=(50,200,50); BID_HIGHLIGHT=(255,100,100)
OBSTACLE_COLOR = (100, 100, 100); REPLAN_HIGHLIGHT = (255, 255, 100)
WINNER_HIGHLIGHT_COLOR = (255, 215, 0); MOVING_OBSTACLE_COLOR = (50, 50, 50)
WAYPOINTS = {"ENT":(1,3),"PHA":(4,3),"ICU":(4,1),"R101":(4,5),"EMR":(7,3),"STO":(10,3)}
WAYPOINT_COLORS = {"ENT":WHITE,"PHA":BLUE,"ICU":RED,"R101":GREEN,"EMR":YELLOW,"STO":PURPLE}
ROBOT_COLORS = {"R1":CYAN,"R2":MAGENTA,"R3":ORANGE}; ROBOT_IDS = ["R1","R2","R3"]
WAYPOINT_PRIORITIES = {"ICU": 1, "PHA": 2, "R101": 3, "EMR": 4, "STO": 5, "ENT": 99}
grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

# --- Moving Obstacle Class (MODIFIED: Handles vertical too) ---
class MovingObstacle:
    def __init__(self, start_pos, end_pos, speed=1, axis='x'): # Added axis ('x' or 'y')
        self.pos = start_pos; self.start_pos = start_pos; self.end_pos = end_pos
        self.direction = 1; self.speed = speed; self.move_timer = 0
        self.move_delay = max(1, FPS // speed); self.axis = axis # Store movement axis

    def update(self):
        self.move_timer += 1
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            current_r, current_c = self.pos
            target_pos = self.end_pos if self.direction == 1 else self.start_pos
            target_r, target_c = target_pos

            if self.axis == 'x': # Horizontal movement
                if current_c != target_c:
                    new_c = current_c + self.direction
                    if 0 <= new_c < GRID_COLS: self.pos = (current_r, new_c)
                    else: self.direction *= -1 # Hit boundary
                    if self.pos == target_pos: self.direction *= -1 # Hit target
                else: self.direction *= -1 # Already at target
            elif self.axis == 'y': # Vertical movement
                 if current_r != target_r:
                      new_r = current_r + self.direction
                      if 0 <= new_r < GRID_ROWS: self.pos = (new_r, current_c)
                      else: self.direction *= -1 # Hit boundary
                      if self.pos == target_pos: self.direction *= -1 # Hit target
                 else: self.direction *= -1 # Already at target

    def draw(self, screen):
        r, c = self.pos
        rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, MOVING_OBSTACLE_COLOR, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
# --- END Moving Obstacle Update ---

class Task:
    # ... (Task class unchanged) ...
    def __init__(self, task_id, target_waypoint, priority=None):
        self.id = task_id; self.target_waypoint = target_waypoint.upper()
        self.target_pos = WAYPOINTS.get(self.target_waypoint)
        self.priority = WAYPOINT_PRIORITIES.get(self.target_waypoint, 5)
        self.status = "ANNOUNCED"; self.assigned_robot = None
        self.created_at = time.time(); self.bids = {}; self.potential_bidders = set()
        self.completed_at = None; self.completion_time = None

class Robot:
    # ... (Robot __init__, assign_task unchanged) ...
    def __init__(self, robot_id, start_pos, color):
        self.id = robot_id; self.pos = start_pos; self.color = color
        self.offset_x = random.randint(-CELL_SIZE//8, CELL_SIZE//8)
        self.offset_y = random.randint(-CELL_SIZE//8, CELL_SIZE//8)
        self.path = []; self.path_index = 0; self.status = "IDLE"
        self.target_waypoint = None; self.current_task_id = None
        self.energy = 100.0; self.low_energy_threshold = 20.0; self.energy_drain_per_step = 0.5
        self.pending_bid_task = None; self.highlight_timer = 0

    def assign_task(self, task):
        global grid
        # print(f"  DEBUG: {self.id} attempting assign_task Task {task.id}")
        if not task.target_pos: print(f"!!! {self.id} no waypoint {task.target_waypoint}."); self.status = "IDLE"; return False
        if grid[self.pos[0]][self.pos[1]] == 1: print(f"!!! {self.id} inside obstacle."); self.status = "FAILED"; return False
        if grid[task.target_pos[0]][task.target_pos[1]] == 1: print(f"!!! Target {task.target_waypoint} blocked."); self.status = "IDLE"; return False
        # --- NEW: Check if target blocked by ANY moving obstacle ---
        global moving_obstacles # Need access
        if any(task.target_pos == obs.pos for obs in moving_obstacles):
            print(f"!!! Target {task.target_waypoint} blocked by MOVING obstacle!"); self.status = "IDLE"; return False
        # --------------------------------------------------------
        path = astar(grid, self.pos, task.target_pos)
        if path and len(path) > 1:
            self.path = path; self.path_index = 1; self.status = "MOVING"; self.target_waypoint = task.target_waypoint
            self.current_task_id = task.id; task.status = "ASSIGNED"; task.assigned_robot = self.id
            self.highlight_timer = FPS * 1.5
            print(f"{self.id} assigned Task {task.id}. Path: {len(self.path)-1} steps."); return True
        else: print(f"!!! {self.id} no path in assign_task. Path: {path}"); self.status = "IDLE"; return False

    # --- move MODIFIED: Check against list of dynamic obstacles ---
    def move(self, other_robots, dynamic_obstacles_list): # Pass list now
        global tasks, grid
        if self.status == "MOVING":
            if self.path_index < len(self.path):
                next_pos = self.path[self.path_index]; next_r, next_c = next_pos

                if grid[next_r][next_c] == 1: print(f"!!! {self.id} STATIC obstacle at {next_pos}!"); self.status = "REPLANNING"; self.path = []; return

                # Check against ALL dynamic obstacles
                for dyn_obs in dynamic_obstacles_list:
                    if next_pos == dyn_obs.pos:
                         print(f"  DYNAMIC AVOID: {self.id} waiting for moving obstacle at {next_pos}"); return

                occupied = False
                for other_id, other_robot in other_robots.items():
                     if self.id != other_id and other_robot.pos == next_pos:
                         occupied = True; print(f"  COLLISION AVOID: {self.id} waiting for {other_id}"); break
                if occupied: return

                r1,c1=self.pos; r2,c2=next_pos
                move_cost_factor=1.4 if abs(r1-r2)==1 and abs(c1-c2)==1 else 1.0; energy_cost=self.energy_drain_per_step*move_cost_factor
                if self.energy >= energy_cost: self.energy-=energy_cost; self.pos=next_pos; self.path_index+=1
                else: print(f"!!! {self.id} out of energy!"); self.status="IDLE"; self.path = []
            elif self.path_index >= len(self.path) and len(self.path) > 0 :
                 # ...(Arrival logic unchanged)...
                 wp_color = WAYPOINT_COLORS.get(self.target_waypoint, (0,0,0)); qr_code = f"QR_{self.target_waypoint}"
                 # print(f"  SIM_SENSOR: {self.id} Reached {self.target_waypoint}. Color: [{wp_color}], QR: [{qr_code}]")
                 print(f"{self.id} reached {self.target_waypoint}."); self.status="IDLE"; completed_task_id=self.current_task_id; self.path=[]; self.path_index=0; self.current_task_id=None
                 completion_timestamp = time.time()
                 for task in tasks:
                    if task.id == completed_task_id:
                         task.status="COMPLETE"; task.completed_at = completion_timestamp; task.completion_time = task.completed_at - task.created_at
                         print(f"--- Task {task.id} COMPLETE (Took {task.completion_time:.1f}s) ---"); break
    # --- END move modification ---

    # ... (calculate_bid and draw methods unchanged) ...
    def calculate_bid(self, task):
        global grid, moving_obstacles # Need moving obstacles to check target
        # print(f"  DEBUG: {self.id} calculating bid Task {task.id} Prio:{task.priority}")
        self.pending_bid_task = None
        if self.status != "BIDDING": self.status = "IDLE"; return None
        if self.energy < self.low_energy_threshold: self.status = "IDLE"; return None
        if not task.target_pos: self.status = "IDLE"; return None
        if grid[task.target_pos[0]][task.target_pos[1]] == 1: self.status = "IDLE"; return None
        # Check if target blocked by moving obstacle
        if any(task.target_pos == obs.pos for obs in moving_obstacles):
            print(f"  DEBUG: {self.id} cannot bid, target {task.target_waypoint} blocked by MOVING obstacle."); self.status = "IDLE"; return None

        start_pos = self.pos; end_pos = task.target_pos
        start_node_sim = Node(None, start_pos); end_node_sim = Node(None, end_pos)
        open_list_heap = []; heapq.heappush(open_list_heap, start_node_sim)
        open_list_dict = {start_node_sim.position: start_node_sim}
        closed_set_sim = set(); path_g_cost = float('inf'); calc_start_time = time.time()
        distance_cost = float('inf'); path_found_for_cost = False
        while open_list_heap:
             if time.time() - calc_start_time > 0.25: print(f"!!! [A* Bid Calc] Timeout {self.id}"); self.status = "IDLE"; return None
             current_node_sim = heapq.heappop(open_list_heap);
             if current_node_sim.position in open_list_dict: del open_list_dict[current_node_sim.position]
             if current_node_sim.position in closed_set_sim: continue;
             closed_set_sim.add(current_node_sim.position)
             if current_node_sim == end_node_sim: path_g_cost = current_node_sim.g; path_found_for_cost = True; break
             for move_pos, move_cost in [((0,-1),10),((0,1),10),((-1,0),10),((1,0),10),((-1,-1),14),((-1,1),14),((1,-1),14),((1,1),14)]:
                 node_pos_sim=(current_node_sim.position[0]+move_pos[0], current_node_sim.position[1]+move_pos[1])
                 if not(0<=node_pos_sim[0]<GRID_ROWS and 0<=node_pos_sim[1]<GRID_COLS): continue
                 if grid[node_pos_sim[0]][node_pos_sim[1]]==1: continue;
                 if node_pos_sim in closed_set_sim: continue
                 new_node_sim=Node(current_node_sim, node_pos_sim); new_node_sim.g = current_node_sim.g + move_cost
                 dx=abs(new_node_sim.position[0]-end_node_sim.position[0]); dy=abs(new_node_sim.position[1]-end_node_sim.position[1])
                 new_node_sim.h=10*(dx+dy)+(14-2*10)*min(dx,dy); new_node_sim.f=new_node_sim.g+new_node_sim.h
                 if node_pos_sim in open_list_dict and new_node_sim.g >= open_list_dict[node_pos_sim].g: continue
                 heapq.heappush(open_list_heap, new_node_sim)
                 open_list_dict[node_pos_sim] = new_node_sim
        if path_found_for_cost: distance_cost = path_g_cost
        elif self.pos == task.target_pos: distance_cost = 0
        else: print(f"!!! {self.id} cannot calc path cost"); self.status = "IDLE"; return None
        energy_factor = (100.0 - self.energy) / 10.0; priority_factor = task.priority * 5
        bid = distance_cost + energy_factor + priority_factor
        print(f"{self.id} bid Task {task.id}: D={distance_cost:.1f}, E={energy_factor:.1f}, P={priority_factor:.1f} => Bid={bid:.1f}")
        task.bids[self.id] = bid; self.status = "IDLE"; return bid

    def draw(self, screen, font, tiny_font):
        r,c=self.pos; center_x=c*CELL_SIZE+CELL_SIZE//2+self.offset_x; center_y=r*CELL_SIZE+CELL_SIZE//2+self.offset_y; radius=CELL_SIZE//3
        if self.highlight_timer > 0:
             highlight_radius = radius + 5; pygame.draw.circle(screen, WINNER_HIGHLIGHT_COLOR, (center_x, center_y), highlight_radius, 5); self.highlight_timer -= 1
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
        border_color,border_width=BLACK,1
        if self.status == "MOVING": border_color,border_width=WHITE,2
        elif self.status == "BIDDING": border_color,border_width=BID_HIGHLIGHT,3
        elif self.status == "REPLANNING": border_color, border_width = REPLAN_HIGHLIGHT, 4
        elif self.status == "FAILED": border_color, border_width = RED, 4
        pygame.draw.circle(screen, border_color, (center_x, center_y), radius, border_width)
        id_text=font.render(self.id, True, BLACK); id_rect=id_text.get_rect(center=(center_x, center_y-radius//4)); screen.blit(id_text, id_rect)
        energy_text=font.render(f"{self.energy:.0f}%", True, BLACK); energy_rect=energy_text.get_rect(center=(center_x, center_y+radius//4)); screen.blit(energy_text, energy_rect)
        status_text = tiny_font.render(self.status, True, WHITE); status_rect = status_text.get_rect(center=(center_x, center_y + radius + 8)); screen.blit(status_text, status_rect)
        if self.status == "MOVING" and self.path:
            path_points=[(center_x, center_y)]
            for i in range(self.path_index, len(self.path)): pr,pc=self.path[i]; path_points.append((pc*CELL_SIZE+CELL_SIZE//2, pr*CELL_SIZE+CELL_SIZE//2))
            if len(path_points)>=2: pygame.draw.lines(screen, PATH_COLOR, False, path_points, 3)

# --- Pygame Drawing Functions ---
# ... (draw_grid_and_obstacles, draw_waypoints, draw_dashboard_metrics, get_clicked_cell remain the same) ...
def draw_grid_and_obstacles(screen):
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            rect=pygame.Rect(c*CELL_SIZE,r*CELL_SIZE,CELL_SIZE,CELL_SIZE)
            if grid[r][c] == 1: pygame.draw.rect(screen, OBSTACLE_COLOR, rect)
            pygame.draw.rect(screen,GRAY,rect,1)

def draw_waypoints(screen, font):
     for name, pos in WAYPOINTS.items():
        r,c=pos; rect=pygame.Rect(c*CELL_SIZE,r*CELL_SIZE,CELL_SIZE,CELL_SIZE); color=WAYPOINT_COLORS.get(name,BLACK)
        pygame.draw.rect(screen, color, rect); pygame.draw.rect(screen, BLACK, rect, 1)
        text_color=BLACK if sum(color)>384 else WHITE; text=font.render(name,True,text_color); text_rect=text.get_rect(center=rect.center); screen.blit(text,text_rect)

def get_clicked_cell(pos):
    x, y = pos;
    if y < HEIGHT:
        col = x // CELL_SIZE; row = y // CELL_SIZE
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS: return (row, col)
    return None

def draw_dashboard_metrics(screen, font, robots, tasks):
    y_offset = HEIGHT + 10; x_offset = 10; line_height = font.get_height() + 4
    col_width = WIDTH // 2 - 15
    idle_count=sum(1 for r in robots.values() if r.status=="IDLE"); moving_count=sum(1 for r in robots.values() if r.status=="MOVING")
    bidding_count=sum(1 for r in robots.values() if r.status=="BIDDING"); failed_count=sum(1 for r in robots.values() if r.status=="FAILED")
    replan_count=sum(1 for r in robots.values() if r.status=="REPLANNING")
    robot_text = f"Robots: I:{idle_count} M:{moving_count} B:{bidding_count} R:{replan_count} F:{failed_count}"
    robot_surf = font.render(robot_text, True, BLACK); screen.blit(robot_surf, (x_offset, y_offset)); y_offset += line_height
    pending_statuses = ["ANNOUNCED", "BIDDING"]; pending_count = sum(1 for t in tasks if t.status in pending_statuses)
    assigned_count = sum(1 for t in tasks if t.status == "ASSIGNED"); complete_count = sum(1 for t in tasks if t.status == "COMPLETE")
    failed_task_count = sum(1 for t in tasks if t.status == "FAILED")
    task_text = f"Tasks: Pend:{pending_count} Assign:{assigned_count} Comp:{complete_count} Fail:{failed_task_count}"
    task_surf = font.render(task_text, True, BLACK); screen.blit(task_surf, (x_offset, y_offset)); y_offset += line_height
    completed_tasks = [t for t in tasks if t.status == "COMPLETE" and t.completion_time is not None]; avg_time_text = "Avg Time: N/A"
    if completed_tasks: avg_time = sum(t.completion_time for t in completed_tasks)/len(completed_tasks); avg_time_text = f"Avg Time: {avg_time:.1f}s"
    avg_time_surf = font.render(avg_time_text, True, BLACK); screen.blit(avg_time_surf, (x_offset, y_offset)); y_offset += line_height
    if last_clicked_waypoint_name: feedback_text = f"Last Click: {last_clicked_waypoint_name}"; feedback_surf = font.render(feedback_text, True, GRAY); screen.blit(feedback_surf, (x_offset, y_offset)); y_offset += line_height
    y_offset = HEIGHT + 10; x_offset = WIDTH // 2
    pending_title_surf = font.render("Pending Tasks (by Prio):", True, BLACK); screen.blit(pending_title_surf, (x_offset, y_offset)); y_offset += line_height
    pending_tasks = [t for t in tasks if t.status in ["ANNOUNCED", "BIDDING"]]; pending_tasks.sort(key=lambda t: (t.priority, t.created_at))
    max_tasks_to_show = 5
    for i, task in enumerate(pending_tasks):
         if i >= max_tasks_to_show: more_text = f"... ({len(pending_tasks) - max_tasks_to_show} more)"; more_surf = font.render(more_text, True, GRAY); screen.blit(more_surf, (x_offset, y_offset)); break
         prio_str = str(task.priority); bid_str = ""
         if task.status == "BIDDING" and task.bids: bid_str = " B:" + ",".join([f"{rid[1:]}:{b:.0f}" for rid, b in task.bids.items()]) # Shorter ID
         text_str = f" T{task.id}[P{prio_str}]:{task.target_waypoint} ({task.status}{bid_str})"
         text_color = RED if task.status == "ANNOUNCED" else ORANGE; text_surface = font.render(text_str, True, text_color);
         text_rect = text_surface.get_rect(topleft=(x_offset, y_offset)); screen.blit(text_surface, text_rect); y_offset += line_height

# --- Main Simulation Loop ---
def main():
    global tasks, task_counter, robots, grid, last_clicked_waypoint_name, moving_obstacles # Make obstacles global

    # ... (Initialization unchanged) ...
    pygame.init(); pygame.font.init(); font=pygame.font.Font(None, 24); small_font=pygame.font.Font(None, 20); tiny_font=pygame.font.Font(None, 16); clock=pygame.time.Clock()
    info=pygame.display.Info(); screen_width=info.current_w; screen_height=info.current_h
    window_width=WIDTH; window_height=HEIGHT+150; pos_x=(screen_width-window_width)//2; pos_y=(screen_height-window_height)//2
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"
    screen=pygame.display.set_mode((window_width, window_height)); pygame.display.set_caption("Hospital Swarm Simulation - Multi Obstacle") # Updated Caption
    start_pos_ent = WAYPOINTS["ENT"]; start_positions = {"R1":(start_pos_ent[0], start_pos_ent[1]-1), "R2":start_pos_ent, "R3":(start_pos_ent[0], start_pos_ent[1]+1)}
    robots = {}
    for robot_id in ROBOT_IDS:
         r,c=start_positions[robot_id]
         if 0<=r<GRID_ROWS and 0<=c<GRID_COLS and grid[r][c]==0: robots[robot_id]=Robot(robot_id, start_positions[robot_id], ROBOT_COLORS[robot_id])
         else: print(f"Warn: Invalid start pos {robot_id}."); robots[robot_id]=Robot(robot_id, start_pos_ent, ROBOT_COLORS[robot_id])
    
    # --- Initialize MULTIPLE Moving Obstacles ---
    moving_obstacles = [
        MovingObstacle(start_pos=(6, 1), end_pos=(6, 5), speed=1, axis='x'), # Horizontal row 6
        MovingObstacle(start_pos=(3, 1), end_pos=(3, 5), speed=2, axis='x'), # Horizontal row 3 (faster)
        MovingObstacle(start_pos=(5, 4), end_pos=(9, 4), speed=1, axis='y')  # Vertical col 4
    ]
    # ---------------------------------------------

    tasks = []; task_counter = 0; last_clicked_waypoint_name = None
    running = True; computation_done_this_frame = False

    while running:
        pygame.event.pump()
        computation_done_this_frame = False

        # --- Pygame Event Handling (Update obstacle checks) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; break
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_cell = get_clicked_cell(event.pos); mods = pygame.key.get_mods()
                if event.button == 1: # Left Click
                    if mods & pygame.KMOD_SHIFT and clicked_cell: # Obstacle
                        r, c = clicked_cell; is_waypoint = any(pos == clicked_cell for pos in WAYPOINTS.values())
                        # Check against ALL moving obstacles
                        is_moving_obstacle = any(obs.pos == clicked_cell for obs in moving_obstacles)
                        if not is_waypoint and not is_moving_obstacle:
                             grid[r][c] = 1 - grid[r][c]; print(f"Toggled obstacle at {clicked_cell} to {grid[r][c]}")
                    elif not (mods & pygame.KMOD_SHIFT) and clicked_cell: # Task
                        target_waypoint_name = next((name for name, pos in WAYPOINTS.items() if pos == clicked_cell), None)
                        last_clicked_waypoint_name = target_waypoint_name
                        if target_waypoint_name and target_waypoint_name != "ENT":
                            target_r, target_c = WAYPOINTS[target_waypoint_name]
                            target_pos = (target_r, target_c)
                            if grid[target_r][target_c] == 1: print(f"!!! Target {target_waypoint_name} blocked!")
                            # Check against ALL moving obstacles
                            elif any(target_pos == obs.pos for obs in moving_obstacles): print(f"!!! Target {target_waypoint_name} blocked by MOVING obstacle!")
                            else:
                                task_counter += 1; new_task = Task(task_counter, target_waypoint_name)
                                tasks.append(new_task); print(f"--- Task {new_task.id} ({new_task.target_waypoint}) created Prio:{new_task.priority} ---")
                                bidders_set = False; new_task.potential_bidders = set()
                                for robot_id, robot in robots.items():
                                     if robot.status == "IDLE" and robot.energy >= robot.low_energy_threshold:
                                         robot.pending_bid_task = new_task; robot.status = "BIDDING"; bidders_set = True
                                         new_task.potential_bidders.add(robot_id); # print(f"  DEBUG: {robot_id} set BIDDING Task {new_task.id}")
                                if not bidders_set: print("  DEBUG: No eligible robots.")
        if not running: break


        # --- Update ALL Moving Obstacles ---
        for obs in moving_obstacles:
            obs.update()
        # -----------------------------------


        # --- Process ONE Computation (Replan OR Bid Calculation) (Unchanged) ---
        robot_to_replan = next((r for r in robots.values() if r.status == "REPLANNING" and r.current_task_id), None)
        if robot_to_replan and not computation_done_this_frame:
             current_task = next((t for t in tasks if t.id == robot_to_replan.current_task_id), None)
             if current_task:
                  new_path = astar(grid, robot_to_replan.pos, current_task.target_pos); computation_done_this_frame = True
                  if new_path and len(new_path) > 1: print(f"  Replan OK!"); robot_to_replan.path=new_path; robot_to_replan.path_index=1; robot_to_replan.status="MOVING"
                  else: print(f"!!! Replan FAIL!"); robot_to_replan.status="FAILED"; current_task.status="FAILED"; robot_to_replan.current_task_id=None
             else: print(f"!!! {robot_to_replan.id} REPLAN Task not found"); robot_to_replan.status="FAILED"
        if not computation_done_this_frame:
            robot_to_calculate_bid = next((r for r in robots.values() if r.status == "BIDDING" and r.pending_bid_task), None)
            if robot_to_calculate_bid:
                bid_value = robot_to_calculate_bid.calculate_bid(robot_to_calculate_bid.pending_bid_task); computation_done_this_frame = True


        # --- Task Assignment (Unchanged) ---
        tasks_ready_for_assignment = []; all_bids_collected_for = {}
        for task in tasks:
             if task.status in ["ANNOUNCED", "BIDDING"]:
                  bidders_finished = True
                  if task.potential_bidders:
                       for bidder_id in task.potential_bidders:
                            if bidder_id in robots and robots[bidder_id].status not in ["IDLE", "FAILED"]: bidders_finished = False; break
                  if bidders_finished and task.bids: task.status = "BIDDING"; tasks_ready_for_assignment.append(task); all_bids_collected_for[task.id] = True
                  elif bidders_finished and not task.bids and task.status == "ANNOUNCED": task.status = "FAILED"; print(f"!!! Task {task.id} failed - no bids."); task.potential_bidders = set()
        assigned_robots_this_cycle = set()
        tasks_ready_for_assignment.sort(key=lambda t: (t.priority, t.created_at))
        if not computation_done_this_frame:
            for task in tasks_ready_for_assignment:
                 if task.status == "BIDDING" and task.bids:
                     eligible_bidders = {rid: bid for rid, bid in task.bids.items() if rid in robots and robots[rid].status == "IDLE"}
                     if not eligible_bidders: continue
                     lowest_bidder_id = min(eligible_bidders, key=eligible_bidders.get)
                     if lowest_bidder_id not in assigned_robots_this_cycle:
                         winner_robot = robots[lowest_bidder_id]
                         # print(f"  DEBUG: *** Assigning Task {task.id} (P{task.priority}) to {lowest_bidder_id} ***")
                         if winner_robot.assign_task(task): assigned_robots_this_cycle.add(lowest_bidder_id)
                         else: print(f"!!! Assign FAIL..."); winner_robot.status = "IDLE"; task.status = "ANNOUNCED"; task.bids = {}; task.potential_bidders = set()
                 elif task.status == "BIDDING" and not task.bids: task.status = "ANNOUNCED"; task.potential_bidders = set()


        # --- Robot Movement (Pass list of dynamic obstacles) ---
        if not computation_done_this_frame:
            for robot_id, robot in robots.items():
                if robot.status == "MOVING":
                    other_bots = {rid: r for rid, r in robots.items() if rid != robot_id}
                    robot.move(other_bots, moving_obstacles) # Pass list


        # --- Drawing (Draw all moving obstacles) ---
        screen.fill(BLACK)
        draw_grid_and_obstacles(screen) # Draws static obstacles
        # Draw ALL moving obstacles
        for obs in moving_obstacles:
            obs.draw(screen)
        # ---------------------------
        draw_waypoints(screen, font)
        for robot in robots.values(): robot.draw(screen, small_font, tiny_font)
        dash_area_rect=pygame.Rect(0, HEIGHT, window_width, 150); pygame.draw.rect(screen, LIGHT_GRAY, dash_area_rect)
        draw_dashboard_metrics(screen, small_font, robots, tasks)

        pygame.display.flip()
        clock.tick(FPS)
    # --- END Drawing Update ---

    # Cleanup
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()

