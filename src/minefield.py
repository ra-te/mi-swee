
import numpy as np
from colorama import Back


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
        self.board = np.zeros(shape=(width, height), dtype=np.uint8)
        self.mines = np.zeros(shape=(width, height), dtype=np.uint8)
        self.infos = np.zeros(shape=(width, height), dtype=np.uint8)


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


    def set_mines(self, mine_grid: np.ndarray):
        """
        Place the mines on to the field.

        Args:
            mine_grid (np.ndarray): An array of booleans representing the positions of the mines to place.
        """

        if mine_grid.shape != self.board.shape:
            raise ValueError(f"Width and height do not match the minefield. Expected: ({self.board.shape}) but received: {mine_grid.shape}.")
        
        if not np.isin(mine_grid, [0, 1]).all():
            raise ValueError(f"Given grid contains invalid values: {np.unique(mine_grid)}.")
        
        self.mines = mine_grid.astype(dtype=np.uint8)
        self.calc_infos()

    
    def calc_infos(self):
        """
        Calculates board information, i.e. how many mines are adjacent to each cell.
        """

        for r in range(self.width):
            for c in range(self.height):
                self.infos[r][c] = self.check_mines(self.get_neighbors((r, c))).count(True)


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
            if not mean and not var:
                raise ValueError("If random sampling is enabled, mean and variance must be passed as values.")
            else:
                self.num_mines = int(np.clip(np.random.normal(loc=mean, scale=var), 0, self.width * self.height))


    def sample_mines(self):
        """
        Places mines randomly on to the field.
        """

        grid = np.zeros(shape=(self.width * self.height))
        grid[:self.num_mines] = 1
        np.random.shuffle(grid)
        self.set_mines(grid.reshape((self.width, self.height)))


    def print_field(self, show_mines: bool=False):
        """
        Prints the field.

        Args:
            show_mines (bool): Whether mines should be printed or not.
        """

        raise NotImplementedError()

        for r in range(self.width):
            for c in range(self.height):
                cell = "X"
                print(cell, end=" ")
            print()
        

if __name__ == "__main__":
    field = Minefield(3, 3)
    field.set_num_mines(flat=False, val=1, mean=5, var=3)
    field.sample_mines()
    field.print_field()
