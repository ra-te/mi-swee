
import numpy as np
from minefield import Minefield


class MinesweeperSolver():
    """
    A class that can solve the minesweeper game.
    """

    def __init__(self, minefield: Minefield):
        """
        Initialize the solver by inputting the minefield to solve.

        Args:
            minefield (Minefield): The minefield to solve.
        """

        self.minefield = minefield
        self.relevant_closed = np.ones(shape=(minefield.height, minefield.width))
        self.relevant_opened = np.ones(shape=(minefield.height, minefield.width))


    def calculate_relevants_closed(self):
        """Calculates relevant positions to be opened or flagged on the minefield, ie. positions that are not open nor flagged."""

        self.relevant_closed = np.logical_and(~self.minefield.opens, ~self.minefield.flags)

    
    def calculate_relevants_opened(self):
        """Calculates relevant positions to checked for certain flags and opens, ie. open positions where the neighboring cells have not been flagged or opened yet."""

        self.relevant_opened = np.logical_and(self.minefield.open_info < 9, self.minefield.open_info > 0)


    def flag_certain(self):
        """Flags the first-found relevant position that can certainly be flagged. Returns True if a cell was flagged, False if not."""

        relevant_info_indices = np.argwhere(self.relevant_opened)

        for index in relevant_info_indices:
            r, c = index

            neighbors = self.minefield.get_neighbors(index)
            rows, cols = zip(*neighbors)
            num_relevant_neighs = np.sum(self.relevant_closed[rows, cols])
            num_mine_delta = self.minefield.open_info[r][c] - np.sum(self.minefield.flags[rows, cols])
            
            if num_relevant_neighs == num_mine_delta and num_relevant_neighs > 0:
                neighbors = np.array(neighbors, dtype=object)
                flag_indices = neighbors[np.logical_and(~self.minefield.flags[rows, cols], self.relevant_closed[rows, cols])]
                
                for to_flag_index in flag_indices:
                    to_open_tuple = (to_flag_index[0], to_flag_index[1])
                    self.minefield.set_flag(to_open_tuple)

                # Recalculate relevants
                self.calculate_relevants_closed()
                self.calculate_relevants_opened()
                
                return True
        return False


    def open_certain(self):
        """Opens the first-found position that can certainly be opened. Returns True if a cell was opened, False if not."""

        relevant_info_indices = np.argwhere(self.relevant_opened)

        for index in relevant_info_indices:
            r, c = index

            neighbors = self.minefield.get_neighbors(index)
            rows, cols = zip(*neighbors)
            num_mine_delta = self.minefield.open_info[r][c] - np.sum(self.minefield.flags[rows, cols])
            num_relevants = np.sum(self.relevant_closed[rows, cols])

            if num_mine_delta == 0 and num_relevants > 0:
                neighbors = np.array(neighbors, dtype=object)
                open_indices = neighbors[np.logical_and(~self.minefield.flags[rows, cols], self.relevant_closed[rows, cols])]

                for to_open_index in open_indices:
                    to_open_tuple = (to_open_index[0], to_open_index[1])
                    self.minefield.open_cell(to_open_tuple)

                # Recalculate relevants
                self.calculate_relevants_closed()
                self.calculate_relevants_opened()

                return True
        return False


    def open_random(self):
        """Opens a random relevant cell."""

        relevant_indices = np.argwhere(self.relevant_closed)
        r, c = relevant_indices[np.random.choice(len(relevant_indices))]

        # Recalculate relevants
        self.calculate_relevants_closed()
        self.calculate_relevants_opened()

        return self.minefield.open_cell((r, c))

    
    def solve_loop(self):
        """Main solving loop."""
        while True:

            # Recalculate relevants
            self.calculate_relevants_closed()
            self.calculate_relevants_opened()

            # Perform safe actions first, ie. flagging and opening cells that certainly can be flagged or opened
            safe_actions = True
            while safe_actions:

                # First, flag all cells that can certainly be flagged
                flag_certains = True
                while flag_certains:
                    flag_certains = self.flag_certain()

                # Second, open all cells that can certainly be opened
                open_certains = True
                certains_opened = 0
                while open_certains:
                    open_certains = self.open_certain()
                    if open_certains:
                        certains_opened += 1
                
                # Stop performing safe actions, if nothing has changed
                if certains_opened == 0:
                    safe_actions = False
            
            # Open a cell
            success = self.open_random()

            # Win and Lose checks
            if not success:
                self.minefield.print_field()
                print("Game Over!")
                break
            elif success and self.minefield.check_win():
                self.minefield.print_field()
                print("You've Won!")
                break


if __name__=="__main__":
    minefield = Minefield(20, 20)
    minefield.set_num_mines(True, val=80)
    minefield.sample_mines()

    solver = MinesweeperSolver(minefield)
    
    solver.solve_loop()