import pprint
import random

class Sudoku:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, row, col, num):
        # Check row
        if num in self.grid[row]:
            return False
        # Check column
        for r in range(9):
            if self.grid[r][col] == num:
                return False
        # Check box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.grid[r][c] == num:
                    return False
        return True

    def find_empty_location(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return (i, j)
        return (-1, -1)

    def backtracking(self):
        row, col = self.find_empty_location()
        if (row, col) == (-1, -1):
            return True
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                if self.backtracking():
                    return True
                self.grid[row][col] = 0
        return False

    def solve_all(self, solutions):
        row, col = self.find_empty_location()
        if (row, col) == (-1, -1):
            solutions.append([row[:] for row in self.grid])
            return
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                self.solve_all(solutions)
                self.grid[row][col] = 0

    def solve(self):
        if self.backtracking():
            return self.grid
        return None

    def generate_complete(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.backtracking()
        return self.grid

    def get_candidates(self, row, col):
        if self.grid[row][col] != 0:
            return set()
        candidates = set(range(1, 10))
        candidates -= set(self.grid[row])
        candidates -= set(self.grid[i][col] for i in range(9))
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                candidates.discard(self.grid[r][c])
        return candidates

    def find_single_candidates(self):
        made_progress = False
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    candidates = self.get_candidates(row, col)
                    if len(candidates) == 1:
                        self.grid[row][col] = candidates.pop()
                        made_progress = True
        return made_progress

    def is_human_solvable(self):
        temp_sudoku = Sudoku()
        temp_sudoku.grid = [row[:] for row in self.grid]
        while True:
            if all(0 not in row for row in temp_sudoku.grid):
                return True
            if not temp_sudoku.find_single_candidates():
                return False

    def remove_numbers_human_solvable(self, count):
        cells = [(i, j) for i in range(9) for j in range(9)]
        removed = 0
        while removed < count and cells:
            idx = random.randrange(len(cells))
            row, col = cells.pop(idx)
            if self.grid[row][col] == 0:
                continue
            
            backup = self.grid[row][col]
            self.grid[row][col] = 0
            
            if not self.is_human_solvable():
                self.grid[row][col] = backup
            else:
                removed += 1
        return self.grid

    def generate_grid_Easy(self, difficulty):
        self.generate_complete()
        self.remove_numbers_human_solvable(40)
        return self.grid
    
    def generate_grid_Medium(self, difficulty):
        self.generate_complete()
        self.remove_numbers_human_solvable(50)
        return self.grid
    
    def generate_grid_Hard(self, difficulty):
        self.generate_complete()
        self.remove_numbers_human_solvable(60)
        return self.grid
    
    def generate_grid_Very_Hard(self, difficulty):
        self.generate_complete()
        self.remove_numbers_human_solvable(70)
        return self.grid

    def generate_puzzle(self, difficulty):
        if difficulty == 'easy':
            return self.generate_grid_Easy(difficulty)
        elif difficulty == 'medium':
            return self.generate_grid_Medium(difficulty)
        elif difficulty == 'hard':
            return self.generate_grid_Hard(difficulty)
        elif difficulty == 'very_hard':
            return self.generate_grid_Very_Hard(difficulty)
        else:
            raise ValueError("Invalid difficulty level")
    
    
def main():
    sudoku = Sudoku()
    print("Welcome to Sudoku!")
    print("1. Choose the difficulty level:")
    print("2. Find all the number of solutions:")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Very Hard")
        difficulty_choice = int(input("Enter your choice: "))
        difficulties = ['easy', 'medium', 'hard', 'very_hard']
        if 1 <= difficulty_choice <= 4:
            sudoku.generate_puzzle(difficulties[difficulty_choice-1])
        else:
            print("Invalid choice. Exiting...")
            return
    
    elif choice == 2:
        print("Enter the Sudoku puzzle (use 0 for empty cells):")
        for i in range(81):
            row, col = divmod(i, 9)
            while True:
                try:
                    val = int(input(f"Enter the number at position ({row + 1}, {col + 1}): "))
                    if 0 <= val <= 9:
                        sudoku.grid[row][col] = val
                        break
                    raise ValueError
                except ValueError:
                    print("Invalid input. Please enter a number between 0 and 9.")
        print("Here is your Sudoku puzzle:")
        pprint.pprint(sudoku.grid)
        print(f"Number of solutions: {sudoku.count_solutions()}")
        return

    print("Here is your Sudoku puzzle:")
    pprint.pprint(sudoku.grid)
    if sudoku.solve():
        print("Here is the solution:")
        pprint.pprint(sudoku.grid)
    else:
        print("No solution exists")

if __name__ == "__main__":
    main()
    while input("Do you want to play again? (y/n): ").strip().lower() == "y":
        main()
