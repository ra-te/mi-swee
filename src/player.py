

from minefield import Minefield


class MineSweeperPlayer():
    """
    A class that is used to play Minesweeper.
    """

    def _parse_uinteger(self, input):
        try:
            value = int(input)
            if value < 1 or value > 99:
                raise ValueError()
            return value
            
        except ValueError:
            return None

    
    def _parse_ufloat(self, input):
        try:
            value = float(input)
            if value < 0 or value > 99:
                raise ValueError()
            return value
            
        except ValueError:
            return None


    def _parse_str_in_valids(self, input, valids: list):
        try:
            text = str(input)
            if text not in valids:
                raise Exception()
            return text
            
        except Exception:
            return None

    
    def initialize(self):
        print("Welcome to Minesweeper!")

        width = None
        while not width:
            line = input("Please input the width of the minefield: ")
            width = self._parse_uinteger(line)
            if not width: print("Value invalid!")

        height = None
        while not height:
            line = input("Please input the height of the minefield: ")
            height = self._parse_uinteger(line)
            if not height: print("Value invalid!")

        self.minefield = Minefield(width, height)

        sample_type = None
        while not sample_type:
            line = input("Do you want to set a fixed (f) or random (r) number of mines: ")
            sample_type = self._parse_str_in_valids(line, ["f", "r"])
            if not sample_type: print("Action invalid!")

        if sample_type == "f":
            num_mines = None
            while not num_mines:
                line = input("How many mines should be placed: ")
                num_mines = self._parse_uinteger(line)
                if not num_mines:
                    print("Value invalid!")
                    continue
            
                try:
                    self.minefield.set_num_mines(True, val=num_mines)
                except ValueError:
                    print(f"Number must be smaller than the total number of cells ({self.minefield.height*self.minefield.width})")
                    num_mines = None
        else:
            mean = None
            while not mean:
                line = input("Mean value for normal distribution to sample from: ")
                mean = self._parse_ufloat(line)
                if not mean: print("Value invalid!")

            var = None
            while not var:
                line = input("Variance for normal distribution to sample from: ")
                var = self._parse_ufloat(line)
                if not var: print("Value invalid!")

            self.minefield.set_num_mines(False, mean=mean, var=var)
        
        self.minefield.sample_mines()


    def _parse_action(self, input: str):
        elements = input.split()
        if len(elements) != 3:
            print("Action invalid!")
            return None
            
        action = self._parse_str_in_valids(elements[0], ["f", "o"])
        if not action:
            print("Action invalid!")
            return None

        pos_x = self._parse_uinteger(elements[1])
        if not pos_x or pos_x > self.minefield.width:
            print("Action invalid!")
            return None

        pos_y = self._parse_uinteger(elements[2])
        if not pos_y or pos_y > self.minefield.height:
            print("Action invalid!")
            return None

        return action, pos_x, pos_y

        
    def action(self):
        output = None
        while output == None:
            line = input("Input an action (<f|o> posX posY): ")
            output = self._parse_action(line)
        
        action, pos_x, pos_y = output
        if action == "f":
            self.minefield.set_flag((pos_y-1, pos_x-1))
            return True
        else:
            success = self.minefield.open_cell((pos_y-1, pos_x-1))
            if success == None:
                print("Cell already opened. Nothing happens.")
                return True
            else:
                return success
        

    def game_loop(self):
        cont = True
        while cont:
            print("")
            self.minefield.print_field()
            print("")

            cont = self.action()

            if cont:
                win = self.minefield.check_win()
                if win:
                    print("You've won!")
                    print("")
                    self.minefield.print_field(True)
                    cont = False
            else:
                print("You've lost!")
                print("")
                self.minefield.print_field(True)


if __name__ == "__main__":
    player = MineSweeperPlayer()
    player.initialize()
    player.game_loop()