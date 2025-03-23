import tkinter as tk
import random
import os
from collections import deque
import pygame  # For playing sound

class MazeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Maze Game")
        
        # Initial difficulty level
        self.difficulty = 5
        self.rows = 7
        self.cols = 7
        self.level = 1  # Initialize the level counter

        # Create SFX folder if it doesn't exist
        self.sfx_folder = "SFX"
        if not os.path.exists(self.sfx_folder):
            os.makedirs(self.sfx_folder)

        # Initialize pygame mixer for sound
        pygame.mixer.init()

        # Create a frame for the maze canvas
        self.maze_frame = tk.Frame(master)
        self.maze_frame.pack()

        # Create canvas to draw the maze
        self.canvas = tk.Canvas(self.maze_frame, width=500, height=500)
        self.canvas.pack()

        # Create a frame for the level counter
        self.level_frame = tk.Frame(master)
        self.level_frame.pack()

        # Create a label for the level counter
        self.level_label = tk.Label(self.level_frame, text=f"Level: {self.level}", font=("Arial", 14))
        self.level_label.pack()

        # Start the game
        self.new_game()

        # Bind key press events for player movement
        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)
        self.master.bind("<Up>", self.move_up)
        self.master.bind("<Down>", self.move_down)

    def new_game(self):
        self.maze = self.generate_maze(self.rows, self.cols)
        
        # Ensure a path exists
        while not self.is_reachable(self.maze):
            self.maze = self.generate_maze(self.rows, self.cols)
        
        self.player_pos = self.find_point('S')
        self.goal_pos = self.find_point('E')
        
        # Draw the maze
        self.canvas.delete("all")
        self.draw_maze()

        # Display player's current position
        self.player_marker = self.canvas.create_oval(
            self.player_pos[1] * 50 + 10,
            self.player_pos[0] * 50 + 10,
            self.player_pos[1] * 50 + 40,
            self.player_pos[0] * 50 + 40,
            fill="blue"
        )

    def generate_maze(self, rows, cols):
        # Create an empty maze with walls around the edges
        maze = [['#' for _ in range(cols)] for _ in range(rows)]
        
        # Clear inside area (set to empty spaces)
        for row in range(1, rows - 1):
            for col in range(1, cols - 1):
                maze[row][col] = ' '
        
        # Add random obstacles (walls) depending on the difficulty
        obstacle_count = random.randint(self.difficulty, self.difficulty * 2)
        for _ in range(obstacle_count):
            row = random.randint(1, rows - 2)
            col = random.randint(1, cols - 2)
            maze[row][col] = '#'
        
        # Place start ('S') and goal ('E') randomly
        maze[1][1] = 'S'
        maze[rows - 2][cols - 2] = 'E'
        
        return maze

    def find_point(self, point):
        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):
                if self.maze[row][col] == point:
                    return (row, col)
        return None

    def draw_maze(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * 50
                y1 = row * 50
                x2 = (col + 1) * 50
                y2 = (row + 1) * 50
                if self.maze[row][col] == '#':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
                elif self.maze[row][col] == 'S':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="green")
                elif self.maze[row][col] == 'E':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="red")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")

    def move_left(self, event):
        if self.player_pos[1] > 0 and self.maze[self.player_pos[0]][self.player_pos[1] - 1] != '#':
            self.update_position((self.player_pos[0], self.player_pos[1] - 1))

    def move_right(self, event):
        if self.player_pos[1] < self.cols - 1 and self.maze[self.player_pos[0]][self.player_pos[1] + 1] != '#':
            self.update_position((self.player_pos[0], self.player_pos[1] + 1))

    def move_up(self, event):
        if self.player_pos[0] > 0 and self.maze[self.player_pos[0] - 1][self.player_pos[1]] != '#':
            self.update_position((self.player_pos[0] - 1, self.player_pos[1]))

    def move_down(self, event):
        if self.player_pos[0] < self.rows - 1 and self.maze[self.player_pos[0] + 1][self.player_pos[1]] != '#':
            self.update_position((self.player_pos[0] + 1, self.player_pos[1]))

    def update_position(self, new_pos):
        self.canvas.delete(self.player_marker)
        self.player_pos = new_pos
        self.player_marker = self.canvas.create_oval(
            self.player_pos[1] * 50 + 10,
            self.player_pos[0] * 50 + 10,
            self.player_pos[1] * 50 + 40,
            self.player_pos[0] * 50 + 40,
            fill="blue"
        )
        if self.player_pos == self.goal_pos:
            self.canvas.create_text(
                self.cols * 50 / 2, self.rows * 50 / 2,
                text="You Win!", font=("Arial", 24), fill="green"
            )
            # Play "click" sound
            self.play_sound("click.mp3")
            
            # Increase level and difficulty, then generate a new maze
            self.level += 1
            self.difficulty += 1
            self.level_label.config(text=f"Level: {self.level}")
            self.master.after(1000, self.new_game)

    def play_sound(self, filename):
        # Construct the full path to the sound file
        sound_file = os.path.join(self.sfx_folder, filename)
        
        # Play the sound if it exists
        if os.path.exists(sound_file):
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()

    def is_reachable(self, maze):
        start = self.find_point('S')
        goal = self.find_point('E')
        
        # Use BFS to check if there's a path from start to goal
        queue = deque([start])
        visited = set([start])
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while queue:
            row, col = queue.popleft()
            if (row, col) == goal:
                return True
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    if maze[new_row][new_col] != '#' and (new_row, new_col) not in visited:
                        visited.add((new_row, new_col))
                        queue.append((new_row, new_col))
        
        return False

root = tk.Tk()
game = MazeGame(root)
root.mainloop()
