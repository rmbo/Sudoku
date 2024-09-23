from sudoku import Sudoku
from gui import SudokuGUI

def main():
    play_again = True
    while play_again:
        gui = SudokuGUI()
        gui.start_screen()
        if not gui.play_again:
            break
        difficulty = gui.difficulty
        sudoku = Sudoku()
        puzzle, solution = sudoku.generate_puzzle(difficulty=difficulty)
        gui.run(puzzle, solution)
        play_again = gui.play_again

if __name__ == "__main__":
    main()
