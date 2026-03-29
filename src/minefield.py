
import numpy as np
from colorama import init as init_colorama
from colorama import Back, Fore, Style


class Minefield():
    """
    A class representing a minefield, with a given width and height.
    """

    def __init__(self, width: int=10, height: int=10):
        """
        Initialize a minefield class.

        Args:
            width (int): The width of the minefield.
            height (int): The height of the minefield.
        """

        self.width = width
        self.height = height
        self.flags = np.zeros(shape=(width, height), dtype=np.bool)
        self.opens = np.zeros(shape=(width, height), dtype=np.bool)
        self.mines = np.zeros(shape=(width, height), dtype=np.bool)
        self.infos = np.zeros(shape=(width, height), dtype=np.uint8)


    def set_num_mines(self, flat: bool, val: int=None, mean: float=None, var: float=None):
        """
        Sets the number of mines for the field.

        Args:
            flat (bool): Whether a flat value is selected or sampling from a normal distribution.
            val (int, optional): If `flat` is enabled, this value is set to be the number of mines. 
            mean (float, optional): If `flat` is disabled, this value represents the mean of the normal distribution to sample from.
            var (float, optional): If `flat` is disabled, this value represents the variance of the normal distribution to sample from.
        """

        if flat:
            if not val or self.width * self.height < val or val < 0:
                raise ValueError(f"Invalid number of mines, must be greater than 0 and smaller than {self.width * self.height + 1}.")
            else:
                self.num_mines = val
        else:
            if not mean or not var:
                raise ValueError("If random sampling is enabled, mean and variance must be passed as values.")
            else:
                self.num_mines = int(np.clip(np.random.normal(loc=mean, scale=var), 0, self.width * self.height))


    def get_neighbors(self, pos: tuple[int, int]) -> list:
        """
        Returns a list of indices containing the neighbors of the selected cell.

        Args:
            pos (tuple[int, int]): The position of the cell to extract the neighbors from.
        """

        r, c = pos

        if r < 0 or self.height <= r or c < 0 or self.width <= c:
            raise ValueError(f"Invalid position. Received {pos}")
        
        offsets = [(-1, -1), (-1, 0), (-1, 1), 
                   ( 0, -1),          ( 0, 1), 
                   ( 1, -1), ( 1, 0), ( 1, 1)]
        
        indices = []
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.width and 0 <= nc < self.height:
                indices.append((nr, nc))

        return indices
    
    
    def check_mines(self, positions: list) -> list:
        """
        Returns a list of booleans of whether the given positions are mines or not.

        Args:
            positions (np.ndarray): The position of the cell to extract the neighbors from.
        """

        mines = []
        for pos in positions:
            r, c = pos
            mines.append(self.mines[r][c] == 1)

        return mines

    
    def calc_infos(self):
        """
        Calculates board information, i.e. how many mines are adjacent to each cell.
        """

        for r in range(self.width):
            for c in range(self.height):
                self.infos[r][c] = self.check_mines(self.get_neighbors((r, c))).count(True)

    
    def sample_mines(self):
        """
        Places mines randomly on to the field and calculates board information.
        """

        grid = np.zeros(shape=(self.width * self.height))
        grid[:self.num_mines] = 1
        np.random.shuffle(grid)
        self.mines = grid.reshape((self.width, self.height)).astype(dtype=np.bool)
        self.calc_infos()


    def open_cell(self, pos: tuple[int, int]) -> bool:
        """
        Opens the cell at the given position. Returns None if cell is already open, True if cell was safe and False if not.
        If cell was safe and has 0 neighboring mines, automatically opens all cells in proximity that also have 0 neighboring mines.

        Args:
            pos (tuple[int, int]): The position of the cell to open.
        """

        r, c = pos
        if self.opens[r][c]:
            return None

        # Reveal the clicked cell
        self.opens[r][c] = True
        self.flags[r][c] = False

        # If mine at that position, return False
        if self.mines[r][c]:
            return False

        # Stop if cell has at least one neighboring mine
        if self.infos[r][c] != 0:
            return True

        # Flood fill logic
        candidates = list()
        candidates.append(pos)
        visited = set()
        visited.add(pos)

        while candidates:
            curr_pos = candidates.pop(0)

            # Get all neighbors
            for neighbor_pos in self.get_neighbors(curr_pos):
                n_r, n_c = neighbor_pos
                if neighbor_pos in visited:
                    continue
                
                # Open the cell of the neighbor
                self.opens[n_r][n_c] = True
                self.flags[n_r][n_c] = False
                visited.add(neighbor_pos)

                # If the neighbor has 0 neighboring mines, add to candidates
                if self.infos[n_r][n_c] == 0:
                    candidates.append(neighbor_pos)

        return True
            
    
    def set_flag(self, pos: tuple[int, int]) -> bool:
        """
        Toggles a flag at the given position. Returns None if cell is already open, True if flag was set and False if flag was removed.

        Args:
            pos (tuple[int, int]): The position of the cell to toggle flag.
        """

        r, c = pos
        if self.opens[r][c]:
            return None
        else:
            self.flags[r][c] = not self.flags[r][c]
            return self.flags[r][c]


    def check_win(self):
        """
        Examines the current state of the board and determines if the game has been won. The game has been won if all non-mine cells have been opened.
        For that, all mine cells must not necessarily be flagged.
        """

        return np.all(np.logical_xor(self.opens, self.mines))


    def print_field(self, show_truth: bool=False):
        """
        Prints the field.

        Args:
            show_truth (bool): Whether mines should be printed or not, and if current flags are correct or not.
        """

        init_colorama()
        for row in range(self.width+1):
            for col in range(self.height+1):
                if row == 0 and col == 0:
                    print(Fore.LIGHTBLACK_EX + "+", end=" ")
                elif row == 0:
                    print(Fore.LIGHTBLACK_EX + str(col), end=" ")
                elif col == 0:
                    print(Fore.LIGHTBLACK_EX + str(row), end=" ")
                else:
                    r, c = row-1, col-1

                    text = " "
                    color = Style.RESET_ALL

                    # Text selection
                    if self.flags[r][c]:
                        text = "F"
                    else:
                        if self.mines[r][c]:
                            if self.opens[r][c]:
                                text = "D"
                            else:
                                if show_truth:
                                    text = "M"
                        else:
                            if self.opens[r][c]:
                                val = self.infos[r][c]
                                if val != 0:
                                    text = str(val)

                    # Background color selection
                    if not self.opens[r][c]:
                        if show_truth:
                            if self.flags[r][c] and not self.mines[r][c]:
                                color = Back.RED
                            else:
                                color = Back.GREEN
                        else:
                            color = Back.WHITE

                    print(color + text, end=" ")
            
            print(Style.RESET_ALL)


