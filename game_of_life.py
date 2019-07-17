from tkinter import *
import math
import random

# colors
WHITE = "white"
BLACK = "black"
GREY = "lightgrey"


# TK config
X_CELLS = 200
Y_CELLS = 125
CELL_SIZE = 5
SLEEP_TIME = 50  # time in ms between 2 moves


class Cell:
    def __init__(self, widget, x, y, color=WHITE):
        self.widget = widget
        self.x = x
        self.y = y
        self.color = color


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.cells = dict()
        self.stopped = True    # flag to prevent to click multiple callbacks by Run click
        self.steps = 0
        self.alive = set()

        # Title
        self.title_label = Label(self, text="John Conway's Game of Life", justify=CENTER)
        self.title_label.pack()

        # Frame
        self.frame = Frame(self, padx=1, pady=1, borderwidth=2, relief=GROOVE)
        self.frame.pack()

        # Canvas Grid and squares
        self.canvas = Canvas(self.frame,
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

        # create cells
        # TODO storing a rectangle for each cell is putting heavy pressure on the processor
        # TODO it is fine for small grids but does not scale well
        # TODO instead we could be a bit smarter and create only the rectangles we need
        for i in range(0, X_CELLS):
            for j in range(0, Y_CELLS):
                cell = self.canvas.create_rectangle(
                    5 + i * CELL_SIZE + 1, 5 + j * CELL_SIZE + 1,
                    (i+1) * CELL_SIZE + 5, 5 + (j+1) * CELL_SIZE,
                    fill=WHITE, outline="")
                self.cells[(i, j)] = Cell(cell, i, j)

        # Start / Stop / Reset buttons
        self.bottom_frame = Frame(self)
        self.bottom_frame.pack()
        self.next_button = Button(self, text="Next", command=self.next_button_click)
        self.next_button.pack(side="left")
        self.run_button = Button(self, text="Run", command=self.run_button_click)
        self.run_button.pack(side="left")
        self.stop_button = Button(self, text="Stop", command=self.stop_button_click)
        self.stop_button.pack(side="left")
        self.reset_button = Button(self, text="Reset", command=self.reset_button_click)
        self.reset_button.pack(side="left")

        # steps count
        self.steps_label1 = Label(self, text="Step : ")
        self.steps_label2 = Label(self, text="0")
        self.steps_label2.pack(side="right")
        self.steps_label1.pack(side="right")

    def initial_setup(self):
        random.seed(7)
        # random.seed(222)        # stable in ~ 700 steps
        # random.seed(3006)       # several ships, 1 crash, stable in ~1300 steps
        cells = []

        # fill randomly some pixels in the 40x40 square in the center of the grid
        # TODO make that configurable
        x0 = math.trunc(X_CELLS / 2)
        y0 = math.trunc(Y_CELLS / 2)
        for i in range(x0 - 20, x0 + 20):
            for j in range(y0 - 20, y0 + 20):
                if random.randint(0, 1) > 0:
                    cells.append((i, j))

        for (x, y) in cells:
            self.alive.add((x, y))
            self.set_cell_color(x, y, BLACK)

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

    def set_cell_color(self, x, y, color):
        cell = self.cells[(x, y)]
        cell.color = color                                  # logical color flip
        self.canvas.itemconfigure(cell.widget, fill=color)  # physical color flip

    # only alive cells and their neighbors are likely to change state
    def get_cells_to_check(self):
        to_check = set()
        for (x, y) in self.alive:
            for (xi, yi) in self.get_adjacents(x, y):
                to_check.add((xi, yi))
        return to_check

    def replace_cells(self, cells):
        to_erase = self.alive.difference(cells)
        to_draw = cells.difference(self.alive)
        self.alive = cells
        for (x, y) in to_erase:
            self.set_cell_color(x, y, WHITE)
        for (x, y) in to_draw:
            self.set_cell_color(x, y, BLACK)

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
            for (x, y) in self.alive:
                self.set_cell_color(x, y, WHITE)

            self.alive = set()
            self.initial_setup()

            # reset flags
            self.stopped = True


app = App()
app.initial_setup()
app.mainloop()
