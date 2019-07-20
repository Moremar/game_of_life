import tkinter as tk
import math
import random

# colors
WHITE = "white"
BLACK = "black"
GREY  = "lightgrey"
RED   = "red"

# TK config
X_CELLS    = 350
Y_CELLS    = 200
CELL_SIZE  = 4
SLEEP_TIME = 10  # time in ms between 2 moves
SEED_INIT  = 7


class Cell:
    def __init__(self, widget, x, y):
        self.widget = widget
        self.x = x
        self.y = y


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.cells = dict()
        self.stopped = True    # flag to prevent to click multiple callbacks by Run click
        self.steps = 0
        self.alive = set()

        # Title
        self.title_label = tk.Label(self, text="John Conway's Game of Life", justify=tk.CENTER)
        self.title_label.pack()

        # Frame
        self.frame = tk.Frame(self, padx=1, pady=1, borderwidth=2, relief=tk.GROOVE)
        self.frame.pack()

        # Canvas Grid and squares
        self.canvas = tk.Canvas(self.frame,
                                width=10 + X_CELLS * CELL_SIZE,
                                height=10 + Y_CELLS * CELL_SIZE,
                                bd=0, background=WHITE)
        for i in range(0, 1 + X_CELLS):
            self.canvas.create_line(5 + CELL_SIZE * i, 5,
                                    5 + CELL_SIZE * i, 5 + Y_CELLS * CELL_SIZE,
                                    fill=GREY)
        for j in range(0, 1 + Y_CELLS):
            self.canvas.create_line(5, 5 + CELL_SIZE * j,
                                    5 + X_CELLS * CELL_SIZE, 5 + CELL_SIZE * j,
                                    fill=GREY)
        self.canvas.pack()

        # Start / Stop / Reset buttons
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack()
        self.next_button = tk.Button(self, text="Next", command=self.next_button_click)
        self.next_button.pack(side=tk.LEFT, padx=(10, 1), pady=3)
        self.run_button = tk.Button(self, text="Run", command=self.run_button_click)
        self.run_button.pack(side=tk.LEFT, padx=1, pady=3)
        self.stop_button = tk.Button(self, text="Stop", command=self.stop_button_click)
        self.stop_button.pack(side=tk.LEFT, padx=1, pady=3)
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_button_click)
        self.reset_button.pack(side=tk.LEFT, padx=1, pady=3)

        # Seed for reset
        self.seed_label = tk.Label(self, text="Seed : ")
        self.seed_label.pack(side=tk.LEFT, padx=(20, 1), pady=3)
        self.seed_textbox = tk.Entry(self, width=10)
        self.seed_textbox.pack(side=tk.LEFT, padx=1, pady=3)
        self.seed_textbox.insert(0, str(SEED_INIT))
        self.seed_error_label = tk.Label(self, text="", fg=RED)
        self.seed_error_label.pack(side=tk.LEFT, padx=1, pady=3)

        # steps count
        self.steps_label1 = tk.Label(self, text="Step : ")
        self.steps_label2 = tk.Label(self, text="0")
        self.steps_label2.pack(side=tk.RIGHT)
        self.steps_label1.pack(side=tk.RIGHT)

    def reset_seed(self):
        seed = self.seed_textbox.get()
        try:
            seed = int(seed)
            random.seed(seed)
            self.seed_error_label.config(text=str(""))
            return True
        except ValueError:
            self.seed_error_label.config(text=str("The seed must be an integer."))
            return False

    def initial_setup(self):
        # fill randomly some pixels in the 40x40 square in the center of the grid
        cells = set()
        x0 = math.trunc(X_CELLS / 2)
        y0 = math.trunc(Y_CELLS / 2)
        for i in range(x0 - 20, x0 + 20):
            for j in range(y0 - 20, y0 + 20):
                if random.randint(0, 1) > 0:
                    cells.add((i, j))
        self.replace_cells(cells)

    def is_alive(self, x, y):
        return (x, y) in self.alive

    def should_live(self, x, y):
        adj = self.get_adjacents(x, y)
        alives = [(xi, yi) for (xi, yi) in adj if self.is_alive(xi, yi)]
        return len(alives) == 3 or (len(alives) == 2 and self.is_alive(x, y))

    @staticmethod
    def get_adjacents(x, y):
        cells = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                 (x, y - 1), (x, y + 1),
                 (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]
        return [(xi, yi) for (xi, yi) in cells if 0 <= xi < X_CELLS and 0 <= yi < Y_CELLS]

    def kill_cell(self, x, y):
        # delete the black rectangle on the cell
        cell = self.cells[(x, y)]
        self.canvas.delete(cell.widget)
        del self.cells[(x, y)]

    def create_cell(self, x, y):
        # create a black rectangle on the cell
        cell = self.canvas.create_rectangle(
            5 + x * CELL_SIZE + 1, 5 + y * CELL_SIZE + 1,
            (x + 1) * CELL_SIZE + 5, 5 + (y + 1) * CELL_SIZE,
            fill=BLACK, outline="")
        self.cells[(x, y)] = Cell(cell, x, y)

    # only alive cells and their neighbors are likely to change state
    def get_cells_to_check(self):
        to_check = set()
        for (x, y) in self.alive:
            for (xi, yi) in self.get_adjacents(x, y):
                to_check.add((xi, yi))
        return to_check

    def replace_cells(self, cells):
        to_kill = self.alive.difference(cells)
        to_create = cells.difference(self.alive)
        self.alive = cells
        for (x, y) in to_kill:
            self.kill_cell(x, y)
        for (x, y) in to_create:
            self.create_cell(x, y)

    def next_turn(self):
        to_check = self.get_cells_to_check()
        next_alive = set()
        for (x, y) in to_check:
            if self.should_live(x, y):
                next_alive.add((x, y))

        self.replace_cells(next_alive)
        self.steps += 1
        self.steps_label2.config(text=str(self.steps))

    def start_play_loop(self):
        if self.stopped:
            return
        self.next_turn()
        self.after(SLEEP_TIME, self.start_play_loop)

    def next_button_click(self):
        if not self.stopped:
            return
        self.next_turn()

    def run_button_click(self):
        if not self.stopped:    # already running
            return
        self.stopped = False
        self.start_play_loop()

    def stop_button_click(self):
        self.stopped = True

    def reset_button_click(self):
        if not self.stopped:
            self.stopped = True
            # waits 2 turn to ensure the main loop stopped
            self.after(2 * SLEEP_TIME, self.reset_button_click)
        else:
            if not self.reset_seed():
                # invalid seed, let the user fix it and click again on Reset
                return

            for (x, y) in self.alive:
                self.kill_cell(x, y)

            self.alive = set()
            self.initial_setup()

            # reset flags
            self.stopped = True


app = App()
app.reset_seed()
app.initial_setup()
app.mainloop()
