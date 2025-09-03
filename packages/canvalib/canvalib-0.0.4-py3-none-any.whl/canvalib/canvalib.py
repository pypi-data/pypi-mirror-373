"""Warning

    If canva is more big than it's terminal size, it will not work correctly.
    If you don't know size of your terminal and want to have the bigest canva
    then leave width and height size blank and it will automaticaly scan size
    of your terminal. Don't resize your terminal too much small that the canva
    will be more bigger if it's rendering.

"""

import os
import colorama
from colorama import init, Fore, Back
import sys
from time import sleep, time

init(autoreset=True)

sys.stdout.write("\033[?25l")  # hide curzor
sys.stdout.flush()

class Canvas:
    def __init__(self, width: int = os.get_terminal_size()[0] - 1, 
                 height: int = os.get_terminal_size()[1] - 1, background = Back.BLACK, color = Fore.GREEN):
        """Initializing and generating Canvas object. Notice that it is not scalable.

        Args:
            width (int, optional): Optional width of window. Defaults to os.get_terminal_size()[0].

            height (int, optional): Optional height of window. Defaults to os.get_terminal_size()[1].

            background (_type_, optional): _description_. Defaults to Back.BLACK. If you want to add other
            colors in any text position add Back.color to text. Notice that if you want it you must import Back from colorama.

            color (_type_, optional): _description_. Defaults to Fore.GREEN. If you want to add other backround colors in
            any text position add Fore.color to text. Notice that if you want it you must import Fore from colorama.
        """
        self.width = width
        self.height = height
        self.background = background
        self.color = color
        self.rows: list[list[str]]
        self.generate_rows()
        self.first = True

    def generate_rows(self):
        #self.rows = [[" " for _ in range(self.width)] for _ in range(self.height)]
        rows = []
        for i in range(self.height):
            row = []
            for z in range(self.width):
                row.append(self.background + self.color + " ")
            rows.append(row)
        self.rows = rows
    
    def add_remaining(self, text):
        if len(text) < self.width:
            text = text + (" " * (self.width - len(text)))
        return text

    def add_text(self, x, y, text):
        for i, char in enumerate(text):
            if 0 <= x < self.height and 0 <= y+i < self.width:
                if len(char) == 1:
                    self.rows[x][y+i] = self.color + self.background + char
                else:
                    self.rows[x][y+i] = char

    def render(self):
        if self.first:
            self.first = False
        else:
            print("\033[A" * (len(self.rows)), end="")
        for row in self.rows:
            for char in row:
                print(char, sep="", end="")
            print()

    

def _test():
    before = time()
    t = 0.5
    c = Canvas(50, 10)
    print("Height: ", c.height)
    print("Width: ", c.width, "\n")
    c.add_text(4,22,"I");c.render();sleep(t)
    c.add_text(4,23,"t");c.render();sleep(t)
    c.add_text(4,24,"'");c.render();sleep(t)
    c.add_text(4,25,"s");c.render();sleep(t)
    c.add_text(5,20,"w");c.render();sleep(t)
    c.add_text(5,21,"o");c.render();sleep(t)
    c.add_text(5,22,"r");c.render();sleep(t)
    c.add_text(5,23,"k");c.render();sleep(t)
    c.add_text(5,24,"i");c.render();sleep(t)
    c.add_text(5,25,"n");c.render();sleep(t)
    c.add_text(5,26,"g");c.render();sleep(t)
    after = time()
    usage_of_sleep = 11
    exec_time = after - before - (t * usage_of_sleep)
    print(f"""Executing time including initialization of canvas of 50x10 size without time for sleep({t}) that 
          is there {usage_of_sleep} times (total {(t * usage_of_sleep)}s) is {exec_time}s.""")
    before = time()
    t = 0.5
    c = Canvas(50, 10)
    print("Height: ", c.height)
    print("Width: ", c.width, "\n")
    c.add_text(4,22,"I");c.render()
    c.add_text(4,23,"t");c.render()
    c.add_text(4,24,"'");c.render()
    c.add_text(4,25,"s");c.render()
    c.add_text(5,20,"w");c.render()
    c.add_text(5,21,"o");c.render()
    c.add_text(5,22,"r");c.render()
    c.add_text(5,23,"k");c.render()
    c.add_text(5,24,"i");c.render()
    c.add_text(5,25,"n");c.render()
    c.add_text(5,26,"g");c.render()
    after = time()
    exec_time = after - before
    print(f"""Executing time including initialization of canvas of 50x10 size withou sleep() function (for better accurancy) is {exec_time}s.""")


if __name__ == "__main__":
    _test()