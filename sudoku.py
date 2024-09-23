import random

class Sudoku:
    def __init__(self):
        self.base = 3
        self.side = self.base * self.base
        self.solutions_count = 0

    def pattern(self, r, c):
        # Pattern for a baseline valid solution
        return (self.base * (r % self.base) + r // self.base + c) % self.side

    def shuffle(self, s):
        # Randomize the entries of an array
        return random.sample(s, len(s))

    def generate_board(self):
        # Generate a fully solved Sudoku board
        r_base = range(self.base)
        rows = [g * self.base + r for g in self.shuffle(r_base) for r in self.shuffle(r_base)]
        cols = [g * self.base + c for g in self.shuffle(r_base) for c in self.shuffle(r_base)]
        nums = self.shuffle(range(1, self.side + 1))

        board = [[nums[self.pattern(r, c)] for c in cols] for r in rows]
        return board

    def generate_puzzle(self, difficulty='medium'):
        board = self.generate_board()
        solution = [row[:] for row in board]
        squares = self.side * self.side
        empties = self.get_empties_count(difficulty)
        attempts = 5  # Number of attempts to remove numbers while ensuring uniqueness

        while attempts > 0 and empties > 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] != 0:
                removed_num = board[row][col]
                board[row][col] = 0

                board_copy = [row[:] for row in board]
                self.solutions_count = 0
                self.count_solutions(board_copy)
                if self.solutions_count != 1:
                    board[row][col] = removed_num  # Put it back if not unique
                    attempts -= 1
                else:
                    empties -= 1
        return board, solution

    def get_empties_count(self, difficulty):
        # Determine the number of empty cells based on difficulty
        levels = {'easy': 36, 'medium': 45, 'hard': 54}
        return levels.get(difficulty, 45)

    def count_solutions(self, board):
        empty = self.find_empty(board)
        if not empty:
            self.solutions_count += 1
            return
        if self.solutions_count > 1:
            return
        row, col = empty
        for num in range(1, 10):
            if self.is_valid(board, num, row, col):
                board[row][col] = num
                self.count_solutions(board)
                board[row][col] = 0

    def is_valid(self, board, num, row, col):
        # Check row
        if num in board[row]:
            return False
        # Check column
        if num in [board[r][col] for r in range(9)]:
            return False
        # Check box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(3):
            for c in range(3):
                if board[start_row + r][start_col + c] == num:
                    return False
        return True

    def find_empty(self, board):
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return (r, c)
        return None

    def print_puzzle(self, board):
        # Print the Sudoku puzzle in a readable format
        num_size = len(str(self.side))
        for r in range(self.side):
            line = ""
            if r % self.base == 0 and r != 0:
                print("-" * (self.side * (num_size + 1) + self.base - 1))
            for c in range(self.side):
                if c % self.base == 0 and c != 0:
                    line += "| "
                num = board[r][c]
                line += f"{'.' if num == 0 else num} ".rjust(num_size + 1)
            print(line)
