"""
A* Pathfinding Algorithm Implementation for Snake Game

This module implements the A* pathfinding algorithm to find the optimal path
from the snake's head to the food while avoiding obstacles (walls and snake body).

Key Components:
1. Node class: Represents each cell in the grid
2. AStar class: Implements the A* algorithm
3. Heuristic function: Manhattan distance
4. Path reconstruction and safety checks
"""

import heapq
import math
from typing import List, Tuple, Optional, Set


class Node:
    """
    Represents a single cell/position in the game grid for pathfinding.
    
    Attributes:
        x, y: Grid coordinates
        g_cost: Distance from start node
        h_cost: Heuristic distance to goal (Manhattan distance)
        f_cost: Total cost (g_cost + h_cost)
        parent: Previous node in the optimal path
    """
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.g_cost = 0  # Distance from start
        self.h_cost = 0  # Heuristic distance to goal
        self.f_cost = 0  # Total cost
        self.parent = None
    
    def __lt__(self, other):
        """For heapq comparison - prioritize lower f_cost"""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """Two nodes are equal if they have the same coordinates"""
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """Make Node hashable for use in sets"""
        return hash((self.x, self.y))


class AStarPathfinder:
    """
    A* Pathfinding Algorithm implementation for Snake Game
    
    The algorithm finds the shortest path from snake head to food while
    avoiding obstacles (walls and snake body segments).
    """
    
    def __init__(self, grid_width: int, grid_height: int, cell_size: int = 10):
        """
        Initialize the pathfinder with game grid dimensions.
        
        Args:
            grid_width: Width of game window in pixels
            grid_height: Height of game window in pixels
            cell_size: Size of each cell in pixels (default 10)
        """
        self.cell_size = cell_size
        self.grid_cols = grid_width // cell_size
        self.grid_rows = grid_height // cell_size
    
    def pixel_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        """Convert pixel coordinates to grid coordinates"""
        return x // self.cell_size, y // self.cell_size
    
    def grid_to_pixel(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to pixel coordinates"""
        return grid_x * self.cell_size, grid_y * self.cell_size
    
    def manhattan_distance(self, node1: Node, node2: Node) -> int:
        """
        Calculate Manhattan distance between two nodes.
        
        Manhattan distance is used as the heuristic function because:
        1. It never overestimates the actual distance (admissible)
        2. It's computationally efficient
        3. It works well for grid-based movement
        """
        return abs(node1.x - node2.x) + abs(node1.y - node2.y)
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """
        Get valid neighboring nodes (up, down, left, right).
        Only returns neighbors that are within grid boundaries.
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down
        
        for dx, dy in directions:
            new_x, new_y = node.x + dx, node.y + dy
            
            # Check if neighbor is within grid boundaries
            if 0 <= new_x < self.grid_cols and 0 <= new_y < self.grid_rows:
                neighbors.append(Node(new_x, new_y))
        
        return neighbors
    
    def is_safe_position(self, x: int, y: int, snake_body: List[List[int]], 
                        ignore_tail: bool = True) -> bool:
        """
        Check if a position is safe (not occupied by snake body).
        
        Args:
            x, y: Grid coordinates to check
            snake_body: List of snake body segments in pixel coordinates
            ignore_tail: If True, ignore the tail segment (it will move away)
        """
        # Convert pixel coordinates to grid coordinates for comparison
        snake_grid_positions = []
        for segment in snake_body:
            grid_x, grid_y = self.pixel_to_grid(segment[0], segment[1])
            snake_grid_positions.append((grid_x, grid_y))
        
        # Remove tail if we're ignoring it (it will move when snake moves)
        if ignore_tail and len(snake_grid_positions) > 1:
            snake_grid_positions = snake_grid_positions[:-1]
        
        return (x, y) not in snake_grid_positions
    
    def find_path(self, start_pos: List[int], goal_pos: List[int], 
                  snake_body: List[List[int]]) -> Optional[List[Tuple[int, int]]]:
        """
        Find the optimal path from start to goal using A* algorithm.
        
        Args:
            start_pos: Snake head position [x, y] in pixels
            goal_pos: Food position [x, y] in pixels  
            snake_body: List of snake body segments in pixels
            
        Returns:
            List of (x, y) coordinates in pixels representing the path,
            or None if no path exists
        """
        # Convert pixel coordinates to grid coordinates
        start_grid = self.pixel_to_grid(start_pos[0], start_pos[1])
        goal_grid = self.pixel_to_grid(goal_pos[0], goal_pos[1])
        
        start_node = Node(start_grid[0], start_grid[1])
        goal_node = Node(goal_grid[0], goal_grid[1])
        
        # Initialize open and closed sets
        open_set = []  # Priority queue (heap)
        closed_set: Set[Node] = set()
        
        # Add start node to open set
        heapq.heappush(open_set, start_node)
        
        while open_set:
            # Get node with lowest f_cost
            current_node = heapq.heappop(open_set)
            closed_set.add(current_node)
            
            # Check if we reached the goal
            if current_node == goal_node:
                return self._reconstruct_path(current_node)
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current_node):
                # Skip if neighbor is in closed set
                if neighbor in closed_set:
                    continue
                
                # Skip if neighbor is not safe (occupied by snake body)
                if not self.is_safe_position(neighbor.x, neighbor.y, snake_body):
                    continue
                
                # Calculate costs
                tentative_g_cost = current_node.g_cost + 1
                
                # Check if this neighbor is already in open set with better path
                existing_neighbor = None
                for node in open_set:
                    if node == neighbor:
                        existing_neighbor = node
                        break
                
                # If neighbor is not in open set or we found a better path
                if existing_neighbor is None or tentative_g_cost < existing_neighbor.g_cost:
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self.manhattan_distance(neighbor, goal_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current_node
                    
                    if existing_neighbor is None:
                        heapq.heappush(open_set, neighbor)
        
        # No path found
        return None
    
    def _reconstruct_path(self, goal_node: Node) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from goal to start by following parent nodes.
        Returns path in pixel coordinates.
        """
        path = []
        current = goal_node
        
        while current is not None:
            pixel_coords = self.grid_to_pixel(current.x, current.y)
            path.append(pixel_coords)
            current = current.parent
        
        # Reverse to get path from start to goal
        path.reverse()
        return path
    
    def get_next_direction(self, current_pos: List[int], target_pos: List[int]) -> str:
        """
        Determine the direction to move from current position to target position.
        
        Args:
            current_pos: Current position [x, y] in pixels
            target_pos: Target position [x, y] in pixels
            
        Returns:
            Direction string: 'UP', 'DOWN', 'LEFT', or 'RIGHT'
        """
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        if dx > 0:
            return 'RIGHT'
        elif dx < 0:
            return 'LEFT'
        elif dy > 0:
            return 'DOWN'
        elif dy < 0:
            return 'UP'
        
        return 'RIGHT'  # Default fallback
    
    def find_safe_path_to_tail(self, snake_head: List[int], 
                              snake_body: List[List[int]]) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path from head to near the tail position.
        This is useful when no direct path to food exists - 
        the snake can follow its tail to buy time.
        """
        if len(snake_body) < 2:
            return None
        
        # Target a position near the tail
        tail_pos = snake_body[-1]
        return self.find_path(snake_head, tail_pos, snake_body[:-1])  # Exclude tail from obstacles


class SnakeAI:
    """
    AI controller for the Snake game using A* pathfinding.
    
    This class integrates the A* pathfinder with game logic to make
    intelligent decisions about snake movement.
    """
    
    def __init__(self, grid_width: int, grid_height: int):
        self.pathfinder = AStarPathfinder(grid_width, grid_height)
        self.current_path = []
        self.path_index = 0
    
    def get_next_move(self, snake_head: List[int], food_pos: List[int], 
                     snake_body: List[List[int]]) -> str:
        """
        Get the next move for the snake using A* pathfinding.
        
        Strategy:
        1. Try to find direct path to food
        2. If no path to food, try to follow tail (survival mode)
        3. If all else fails, make a safe move
        """
        # Try to find path to food
        path = self.pathfinder.find_path(snake_head, food_pos, snake_body)
        
        if path and len(path) > 1:
            # Found path to food
            next_pos = path[1]  # First step in path (skip current position)
            return self.pathfinder.get_next_direction(snake_head, next_pos)
        
        # No path to food - try survival mode (follow tail)
        tail_path = self.pathfinder.find_safe_path_to_tail(snake_head, snake_body)
        if tail_path and len(tail_path) > 1:
            next_pos = tail_path[1]
            return self.pathfinder.get_next_direction(snake_head, next_pos)
        
        # Last resort: make any safe move
        return self._make_safe_move(snake_head, snake_body)
    
    def _make_safe_move(self, snake_head: List[int], snake_body: List[List[int]]) -> str:
        """
        Make a safe move when no optimal path is found.
        Tries each direction and picks the first safe one.
        """
        directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        
        for direction in directions:
            next_pos = snake_head.copy()
            
            if direction == 'UP':
                next_pos[1] -= 10
            elif direction == 'DOWN':
                next_pos[1] += 10
            elif direction == 'LEFT':
                next_pos[0] -= 10
            elif direction == 'RIGHT':
                next_pos[0] += 10
            
            # Check if this move is safe
            grid_pos = self.pathfinder.pixel_to_grid(next_pos[0], next_pos[1])
            
            # Check boundaries
            if (0 <= grid_pos[0] < self.pathfinder.grid_cols and 
                0 <= grid_pos[1] < self.pathfinder.grid_rows):
                
                # Check collision with snake body
                if self.pathfinder.is_safe_position(grid_pos[0], grid_pos[1], snake_body):
                    return direction
        
        # No safe move found - return any direction as last resort
        return 'RIGHT'