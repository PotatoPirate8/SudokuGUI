from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QLabel, QMenuBar, QMenu, QMessageBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QBoxLayout)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QFont, QResizeEvent
import sys
from Sudoku import Sudoku

class AspectRatioWidget(QWidget):
    def __init__(self, widget, aspect_ratio):
        super().__init__()
        self.aspect_ratio = aspect_ratio
        layout = QBoxLayout(QBoxLayout.Direction.Down)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)

    def resizeEvent(self, e):
        w = e.size().width()
        h = e.size().height()
        if h * self.aspect_ratio > w:
            h = int(w / self.aspect_ratio)
        else:
            w = int(h * self.aspect_ratio)
        self.layout().setGeometry(QRect(0, 0, int(w), int(h)))

class SudokuCell(QPushButton):
    # Color constants
    ORIGINAL_CELL_COLOR = "#000000"  # Black for original numbers
    NORMAL_CELL_COLOR = "#000000"    # Black for regular cells
    BORDER_COLOR = "#ffffff"         # White for borders
    INNER_BORDER_COLOR = "#404040"   # Dark gray for inner borders
    TEXT_COLOR = "#ffffff"           # White for numbers
    HIGHLIGHT_COLOR = "#303030"      # Slightly lighter black for highlighting

    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.value = 0
        self.original = False
        self.selected = False
        self.setMinimumSize(30, 30)  # Smaller minimum size
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFont(QFont('Arial', 14))
        self.updateDisplay()

    def updateDisplay(self):
        self.setText(str(self.value) if self.value != 0 else "")
        style_parts = []
        
        if self.original:
            style_parts.append("font-weight: bold")
        
        if self.selected:
            style_parts.append(f"background-color: {self.HIGHLIGHT_COLOR}")
        else:
            style_parts.append(f"background-color: {self.ORIGINAL_CELL_COLOR if self.original else self.NORMAL_CELL_COLOR}")
        
        style_parts.append(f"color: {self.TEXT_COLOR}")
        self.setStyleSheet("; ".join(style_parts))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # Dynamic font sizing
        size = min(self.width(), self.height()) // 2
        self.setFont(QFont('Arial', size))

class SudokuGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku")
        self.setMinimumSize(300, 400)  # Smaller minimum size
        self.cells = []
        self.selected_cell = None
        self.sudoku = Sudoku()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable keyboard focus
        self.initUI()
        # Show welcome dialog on startup
        self.show_welcome_dialog()

    def resizeEvent(self, event):
        # Maintain aspect ratio during resize
        super().resizeEvent(event)
        size = event.size()
        min_dim = min(size.width(), size.height())
        self.resize(int(min_dim), int(min_dim * 1.2))  # Convert float to int

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the main layout

        # Create menu bar
        menubar = self.menuBar()
        game_menu = menubar.addMenu("Game")
        
        new_game_menu = QMenu("New Game", self)
        difficulties = {
            "Easy": "Easy",
            "Medium": "Medium",
            "Hard": "Hard",
            "Very Hard": "Very_Hard"
        }
        
        for diff_name, diff_value in difficulties.items():
            action = new_game_menu.addAction(diff_name)
            action.triggered.connect(lambda checked, d=diff_value: self.start_new_game(d))
        
        game_menu.addMenu(new_game_menu)
        solve_action = game_menu.addAction("Solve")
        solve_action.triggered.connect(self.solve_puzzle)

        # Create game grid in aspect ratio container
        grid_widget = QWidget()
        grid_widget.setStyleSheet(f"background-color: {SudokuCell.BORDER_COLOR};")  # White background
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(1)  # Small spacing between cells
        grid_layout.setContentsMargins(2, 2, 2, 2)  # Small margins around grid
        
        # Force the grid to maintain square cells
        for i in range(9):
            grid_layout.setRowMinimumHeight(i, 50)
            grid_layout.setColumnMinimumWidth(i, 50)
            grid_layout.setRowStretch(i, 1)
            grid_layout.setColumnStretch(i, 1)

        # Create cells
        for row in range(9):
            cell_row = []
            for col in range(9):
                cell = SudokuCell(row, col)
                cell.clicked.connect(lambda checked, r=row, c=col: self.cell_clicked(r, c))
                grid_layout.addWidget(cell, row, col)
                cell_row.append(cell)
            self.cells.append(cell_row)

        # Add borders for 3x3 boxes
        for i in range(9):
            for j in range(9):
                cell = self.cells[i][j]
                style_parts = []
                
                # Base styles
                style_parts.append(f"color: {SudokuCell.TEXT_COLOR}")
                style_parts.append(f"background-color: {SudokuCell.ORIGINAL_CELL_COLOR if cell.original else SudokuCell.NORMAL_CELL_COLOR}")
                
                # All cells get borders
                style_parts.append("border: none")  # Reset borders
                
                # Only add borders - no margin needed
                borders = []
                
                # Thick white borders only between 3x3 boxes and outer edges
                if i % 3 == 0: borders.append(f"border-top: 3px solid {SudokuCell.BORDER_COLOR}")
                if i == 8: borders.append(f"border-bottom: 3px solid {SudokuCell.BORDER_COLOR}")
                if j % 3 == 0: borders.append(f"border-left: 3px solid {SudokuCell.BORDER_COLOR}")
                if j == 8: borders.append(f"border-right: 3px solid {SudokuCell.BORDER_COLOR}")
                
                # Thin dark borders for all other cells
                if i % 3 != 0: borders.append(f"border-top: 1px solid {SudokuCell.INNER_BORDER_COLOR}")
                if j % 3 != 0: borders.append(f"border-left: 1px solid {SudokuCell.INNER_BORDER_COLOR}")
                if i == 8: borders.append(f"border-bottom: 1px solid {SudokuCell.INNER_BORDER_COLOR}")
                if j == 8: borders.append(f"border-right: 1px solid {SudokuCell.INNER_BORDER_COLOR}")
                
                style_parts.extend(borders)
                cell.setStyleSheet("; ".join(style_parts))

        # Wrap grid in aspect ratio container
        grid_container = AspectRatioWidget(grid_widget, 1.0)  # 1.0 for square
        main_layout.addWidget(grid_container, 8)

        # Create number buttons
        numbers_widget = QWidget()
        numbers_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        numbers_layout = QHBoxLayout(numbers_widget)
        numbers_layout.setSpacing(1)  # Reduce spacing between buttons
        
        for i in range(9):
            btn = QPushButton(str(i + 1))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumSize(30, 30)
            btn.clicked.connect(lambda checked, num=i+1: self.number_clicked(num))
            numbers_layout.addWidget(btn)
        clear_btn = QPushButton("Clear")
        clear_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        clear_btn.setMinimumSize(40, 30)
        clear_btn.clicked.connect(lambda: self.number_clicked(0))
        numbers_layout.addWidget(clear_btn)
        
        # Wrap buttons in aspect ratio container with different ratio
        buttons_container = AspectRatioWidget(numbers_widget, 10.0)  # Wide aspect ratio for buttons
        main_layout.addWidget(buttons_container, 1)

        # Set spacing between grid and number buttons
        main_layout.setSpacing(10)

    def start_new_game(self, difficulty):
        if difficulty == "Easy":
            self.sudoku.generate_grid_Easy(difficulty)
        elif difficulty == "Medium":
            self.sudoku.generate_grid_Medium(difficulty)
        elif difficulty == "Hard":
            self.sudoku.generate_grid_Hard(difficulty)
        elif difficulty == "Very_Hard":
            self.sudoku.generate_grid_Very_Hard(difficulty)

        for i in range(9):
            for j in range(9):
                self.cells[i][j].value = self.sudoku.grid[i][j]
                self.cells[i][j].original = self.sudoku.grid[i][j] != 0
                self.cells[i][j].updateDisplay()

    def cell_clicked(self, row, col):
        # Deselect previous cell if exists
        if self.selected_cell:
            self.selected_cell.selected = False
            self.selected_cell.updateDisplay()
        
        self.selected_cell = self.cells[row][col]
        self.selected_cell.selected = True
        self.selected_cell.updateDisplay()
        self.setFocus()  # Ensure window keeps keyboard focus after clicking

    def number_clicked(self, number):
        if self.selected_cell and not self.selected_cell.original:
            self.selected_cell.value = number
            self.selected_cell.updateDisplay()

    def solve_puzzle(self):
        self.sudoku.grid = [[self.cells[i][j].value for j in range(9)] for i in range(9)]
        if self.sudoku.solve():
            for i in range(9):
                for j in range(9):
                    self.cells[i][j].value = self.sudoku.grid[i][j]
                    self.cells[i][j].updateDisplay()
        else:
            QMessageBox.warning(self, "Error", "No solution exists!")

    def show_welcome_dialog(self):
        welcome_msg = QMessageBox()
        welcome_msg.setWindowTitle("Welcome to Sudoku!")
        welcome_msg.setText("Please select a difficulty level to start:")
        welcome_msg.setIcon(QMessageBox.Icon.Question)
        
        # Add difficulty buttons
        easy_button = welcome_msg.addButton("Easy", QMessageBox.ButtonRole.ActionRole)
        medium_button = welcome_msg.addButton("Medium", QMessageBox.ButtonRole.ActionRole)
        hard_button = welcome_msg.addButton("Hard", QMessageBox.ButtonRole.ActionRole)
        very_hard_button = welcome_msg.addButton("Very Hard", QMessageBox.ButtonRole.ActionRole)
        
        welcome_msg.exec()
        
        # Check which button was clicked
        clicked_button = welcome_msg.clickedButton()
        if clicked_button == easy_button:
            self.start_new_game("Easy")
        elif clicked_button == medium_button:
            self.start_new_game("Medium")
        elif clicked_button == hard_button:
            self.start_new_game("Hard")
        elif clicked_button == very_hard_button:
            self.start_new_game("Very_Hard")

    def keyPressEvent(self, event):
        if not self.selected_cell:
            # If no cell is selected, start from top-left
            self.cell_clicked(0, 0)
            return

        current_row = self.selected_cell.row
        current_col = self.selected_cell.col

        if event.key() == Qt.Key.Key_Left:
            new_col = (current_col - 1) if current_col > 0 else 8
            self.cell_clicked(current_row, new_col)
        elif event.key() == Qt.Key.Key_Right:
            new_col = (current_col + 1) if current_col < 8 else 0
            self.cell_clicked(current_row, new_col)
        elif event.key() == Qt.Key.Key_Up:
            new_row = (current_row - 1) if current_row > 0 else 8
            self.cell_clicked(new_row, current_col)
        elif event.key() == Qt.Key.Key_Down:
            new_row = (current_row + 1) if current_row < 8 else 0
            self.cell_clicked(new_row, current_col)
        elif event.key() >= Qt.Key.Key_0 and event.key() <= Qt.Key.Key_9:
            # Allow number input via keyboard
            number = event.key() - Qt.Key.Key_0
            self.number_clicked(number)

def main():
    app = QApplication(sys.argv)
    window = SudokuGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
