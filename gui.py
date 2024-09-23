import pygame
import sys
import time
import pickle
import json

class SudokuGUI:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.window_size = 600  # Default window size
        self.cell_size = self.window_size // 9
        self.window = pygame.display.set_mode((self.window_size, self.window_size + 80), pygame.RESIZABLE)
        pygame.display.set_caption("Sudoku")
        self.font = pygame.font.SysFont("arial", 40)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.running = True
        self.play_again = True
        self.clock = pygame.time.Clock()
        self.message = ""
        self.moves = []
        self.start_time = None
        self.hints_available = 3
        self.selected_cell = None
        self.board = None
        self.solution = None
        self.original_puzzle = None
        self.difficulty = 'medium'
        self.paused = False
        self.pause_start_time = None
        self.themes = {
            'default': {'bg_color': (255, 255, 255), 'grid_color': (0, 0, 0)},
            'dark': {'bg_color': (30, 30, 30), 'grid_color': (200, 200, 200)},
        }
        self.current_theme = 'default'
        # Load sounds
        self.select_sound = pygame.mixer.Sound('select.wav')
        self.error_sound = pygame.mixer.Sound('error.wav')
        self.success_sound = pygame.mixer.Sound('success.wav')
        # High scores
        self.high_scores = {'easy': [], 'medium': [], 'hard': []}
        self.load_high_scores()

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                self.high_scores = json.load(f)
        except FileNotFoundError:
            pass

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def start_screen(self):
        # Display start screen with difficulty selection
        self.window.fill(self.themes[self.current_theme]['bg_color'])
        title_text = self.font.render("Welcome to Sudoku!", True, (0, 0, 0))
        start_text = self.small_font.render("Press E for Easy, M for Medium, H for Hard", True, (0, 0, 0))
        theme_text = self.small_font.render("Press T to Change Theme", True, (0, 0, 0))
        quit_text = self.small_font.render("Press Q to Quit", True, (0, 0, 0))

        self.window.blit(title_text, (self.window_size // 2 - title_text.get_width() // 2, self.window_size // 2 - 150))
        self.window.blit(start_text, (self.window_size // 2 - start_text.get_width() // 2, self.window_size // 2 - 50))
        self.window.blit(theme_text, (self.window_size // 2 - theme_text.get_width() // 2, self.window_size // 2))
        self.window.blit(quit_text, (self.window_size // 2 - quit_text.get_width() // 2, self.window_size // 2 + 50))

        pygame.display.flip()

        waiting = True
        while waiting:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.play_again = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.difficulty = 'easy'
                        waiting = False
                    elif event.key == pygame.K_m:
                        self.difficulty = 'medium'
                        waiting = False
                    elif event.key == pygame.K_h:
                        self.difficulty = 'hard'
                        waiting = False
                    elif event.key == pygame.K_t:
                        self.change_theme()
                        self.start_screen()
                        return
                    elif event.key == pygame.K_q:
                        self.running = False
                        self.play_again = False
                        waiting = False

    def change_theme(self):
        themes_list = list(self.themes.keys())
        current_index = themes_list.index(self.current_theme)
        self.current_theme = themes_list[(current_index + 1) % len(themes_list)]

    def initialize_game(self, puzzle, solution):
        self.board = puzzle
        self.solution = solution
        self.original_puzzle = [row[:] for row in puzzle]
        self.start_time = time.time()
        self.hints_available = 3
        self.moves = []
        self.selected_cell = None
        self.message = ""
        self.running = True
        self.paused = False
        self.pause_start_time = None

    def run(self, puzzle, solution):
        self.initialize_game(puzzle, solution)
        while self.running:
            self.clock.tick(30)
            self.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.play_again = False

                elif event.type == pygame.VIDEORESIZE:
                    self.window_size = min(event.w, event.h - 80)
                    self.cell_size = self.window_size // 9
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.paused:
                        self.select_cell(pygame.mouse.get_pos())

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            self.pause_start_time = time.time()
                        else:
                            self.start_time += time.time() - self.pause_start_time
                    if self.paused:
                        continue  # Skip other events when paused
                    if event.key == pygame.K_u:
                        self.undo_move()
                    elif event.key == pygame.K_h:
                        self.give_hint()
                    elif event.key == pygame.K_r:
                        self.reset_puzzle()
                    elif event.key == pygame.K_n:
                        self.running = False  # Exit to generate a new puzzle
                        self.play_again = True
                    elif event.key == pygame.K_q:
                        self.running = False
                        self.play_again = False
                    elif event.key == pygame.K_s:
                        self.solve_puzzle()
                    elif event.key == pygame.K_k:
                        self.save_game()
                    elif event.key == pygame.K_l:
                        self.load_game()
                    elif event.key == pygame.K_t:
                        self.change_theme()
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                        self.navigate(event.key)
                    elif self.selected_cell and self.original_puzzle[self.selected_cell[0]][self.selected_cell[1]] == 0:
                        if event.unicode and event.unicode in '123456789':
                            num = int(event.unicode)
                            row, col = self.selected_cell
                            self.moves.append((self.selected_cell, self.board[row][col]))  # Save move for undo
                            self.board[row][col] = num
                            self.message = ""
                            if self.is_puzzle_complete():
                                if self.board == self.solution:
                                    self.message = "Congratulations! You've solved the puzzle."
                                    self.save_completion_time()
                                    self.success_sound.play()
                                else:
                                    self.message = "Puzzle completed, but with errors."
                        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                            self.clear_cell()
                            self.message = ""
                        elif event.key == pygame.K_ESCAPE:
                            self.selected_cell = None
                            self.message = ""
                        else:
                            # Ignore other keys
                            pass

    def navigate(self, key):
        if self.selected_cell:
            row, col = self.selected_cell
            if key == pygame.K_LEFT:
                col = (col - 1) % 9
            elif key == pygame.K_RIGHT:
                col = (col + 1) % 9
            elif key == pygame.K_UP:
                row = (row - 1) % 9
            elif key == pygame.K_DOWN:
                row = (row + 1) % 9
            self.selected_cell = (row, col)
            self.select_sound.play()

    def update(self):
        if self.paused:
            self.draw_pause_screen()
        else:
            self.draw_grid()
            self.draw_numbers()
            self.draw_selection()
            self.draw_message()
            pygame.display.flip()

    def draw_grid(self):
        bg_color = self.themes[self.current_theme]['bg_color']
        grid_color = self.themes[self.current_theme]['grid_color']
        self.window.fill(bg_color)
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.window, grid_color, (0, i * self.cell_size), (self.window_size, i * self.cell_size), thickness)
            pygame.draw.line(self.window, grid_color, (i * self.cell_size, 0), (i * self.cell_size, self.window_size), thickness)

    def draw_numbers(self):
        for row in range(9):
            for col in range(9):
                num = self.board[row][col]
                if num != 0:
                    if self.original_puzzle[row][col] != 0:
                        color = (0, 0, 0)  # Original numbers in black
                    else:
                        if num != self.solution[row][col]:
                            color = (255, 0, 0)  # Incorrect entries in red
                        else:
                            color = (0, 0, 255)  # Correct user input in blue
                    text = self.font.render(str(num), True, color)
                    x = col * self.cell_size + (self.cell_size - text.get_width()) // 2
                    y = row * self.cell_size + (self.cell_size - text.get_height()) // 2
                    self.window.blit(text, (x, y))

    def draw_selection(self):
        if self.selected_cell:
            row, col = self.selected_cell
            pygame.draw.rect(
                self.window,
                (255, 0, 0),
                (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size),
                3,
            )

    def draw_message(self):
        # Display messages
        if self.message:
            text = self.small_font.render(self.message, True, (255, 0, 0))
            self.window.blit(text, (10, self.window_size + 10))
        # Display timer
        if self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            timer_text = self.small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (0, 0, 0))
            self.window.blit(timer_text, (self.window_size - 150, self.window_size + 10))
        # Display hints left
        hints_text = self.small_font.render(f"Hints Left: {self.hints_available}", True, (0, 0, 0))
        self.window.blit(hints_text, (10, self.window_size + 30))

    def draw_pause_screen(self):
        self.window.fill((100, 100, 100))
        pause_text = self.font.render("Paused", True, (255, 255, 255))
        self.window.blit(pause_text, (self.window_size // 2 - pause_text.get_width() // 2, self.window_size // 2))
        pygame.display.flip()

    def select_cell(self, pos):
        x, y = pos
        if x < self.window_size and y < self.window_size:
            col = x // self.cell_size
            row = y // self.cell_size
            self.selected_cell = (row, col)
            self.message = ""
            self.select_sound.play()
        else:
            self.selected_cell = None

    def clear_cell(self):
        if self.selected_cell:
            row, col = self.selected_cell
            if self.original_puzzle[row][col] == 0 and self.board[row][col] != 0:
                self.moves.append((self.selected_cell, self.board[row][col]))  # Save move for undo
                self.board[row][col] = 0

    def undo_move(self):
        if self.moves:
            last_move = self.moves.pop()
            row, col = last_move[0]
            self.board[row][col] = last_move[1]  # Restore the last value
            self.message = "Move undone."

    def give_hint(self):
        if self.hints_available > 0 and self.selected_cell:
            row, col = self.selected_cell
            if self.board[row][col] == 0:
                correct_num = self.solution[row][col]
                self.board[row][col] = correct_num
                self.hints_available -= 1
                self.message = f"Hint used. Hints left: {self.hints_available}"
            else:
                self.message = "Cell already filled"
        else:
            self.message = "No hints available or no cell selected"

    def is_valid_move(self, num, row, col):
        return num == self.solution[row][col]

    def is_puzzle_complete(self):
        for row in self.board:
            if 0 in row:
                return False
        return True

    def reset_puzzle(self):
        self.board = [row[:] for row in self.original_puzzle]
        self.moves.clear()
        self.selected_cell = None
        self.message = "Puzzle reset"
        self.start_time = time.time()
        self.hints_available = 3

    def solve_puzzle(self):
        self.board = [row[:] for row in self.solution]
        self.message = "Puzzle solved!"
        self.success_sound.play()

    def save_game(self):
        with open('savegame.pkl', 'wb') as f:
            pickle.dump({
                'board': self.board,
                'moves': self.moves,
                'start_time': self.start_time,
                'hints_available': self.hints_available,
                'selected_cell': self.selected_cell,
                'difficulty': self.difficulty,
                'original_puzzle': self.original_puzzle,
                'solution': self.solution,
                'current_theme': self.current_theme
            }, f)
        self.message = "Game saved."

    def load_game(self):
        try:
            with open('savegame.pkl', 'rb') as f:
                data = pickle.load(f)
                self.board = data['board']
                self.moves = data['moves']
                self.start_time = data['start_time']
                self.hints_available = data['hints_available']
                self.selected_cell = data['selected_cell']
                self.difficulty = data['difficulty']
                self.original_puzzle = data['original_puzzle']
                self.solution = data['solution']
                self.current_theme = data.get('current_theme', 'default')
            self.message = "Game loaded."
        except FileNotFoundError:
            self.message = "No saved game found."

    def save_completion_time(self):
        elapsed_time = int(time.time() - self.start_time)
        self.high_scores.setdefault(self.difficulty, []).append(elapsed_time)
        self.high_scores[self.difficulty] = sorted(self.high_scores[self.difficulty])[:5]  # Keep top 5
        self.save_high_scores()

    def display_leaderboard(self):
        # Implement a method to display the leaderboard
        pass  # For brevity, the code for this method is not included
