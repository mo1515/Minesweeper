import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count
    def __hash__(self):
        return hash((frozenset(self.cells), self.count))
    def __str__(self):
        return f"{self.cells} = {self.count}"
    def __repr__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if self.count == len(self.cells):
            return self.cells
        else:
            return []

    def known_safes(self):
        if self.count == 0:
            return self.cells
        else:
            return []

    def mark_mine(self, cell):
        try:
            self.cells.remove(cell)
            self.count-=1
        except :
            pass

    def mark_safe(self, cell):
        try:
            self.cells.remove(cell)
        except :
            pass
    def empty(self):
        if(len(self.cells)<self.count):
            raise ValueError("Count is greater than number of cells")
        
        return len(self.cells)==0 and self.count==0
    


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        self.cells = {(i, j) for i in range(height) for j in range(width)}
        
        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        self.cells.discard(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

        
    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        self.cells.discard(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def combine(self):
        print("Combining knowledge")
        changed=True
        while changed:
            print(self.knowledge)
            print(self.safes)
            print(self.mines)
            changed=False
            for  sen in self.knowledge:
                safe=sen.known_safes()
                mine=sen.known_mines()
                
                if safe or mine:
                    print("new safe or mine found")
                    changed=True
                    for i in safe.copy():
                        self.mark_safe(i)
                    for i in mine.copy():
                        self.mark_mine(i)
                    self.knowledge.remove(sen)
                
            self.knowledge[:] = [x for x in self.knowledge if not x.empty()]                
            for  sen1 in self.knowledge:
                for sen2 in self.knowledge:
                    if sen1 == sen2: continue
                    if sen1.cells.issubset(sen2.cells):
                        new_cells=sen2.cells-sen1.cells
                        new_count=sen2.count-sen1.count
                            
                        new_sentence = Sentence(new_cells, new_count)
                        if new_sentence not in self.knowledge :
                            print("new sentence found")
                            print(new_sentence)
                            changed=True
                            self.knowledge.append(new_sentence)
                        
        
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.mark_safe(cell)
        x,y= cell
        surrouning=set()
        for i in [x-1,x,x+1]:
            if not (-1<i<self.height): continue
            for j in [y-1,y,y+1]:
                cur=(i,j)
                if not (-1<j<self.width) or cur is cell : continue
                if cur not in self.safes and cur not in self.mines and cur not in self.moves_made:
                    surrouning.add(cur)
                elif cur in self.mines: 
                    count-=1


        self.safes.discard(cell)

        if count:
            if count== len(surrouning):
                for i in surrouning:
                    self.mark_mine(i)
            else:
                self.knowledge.append(Sentence(surrouning,count))
        else:
            for i in surrouning:
                self.mark_safe(i)
        
        self.combine()
                





    def make_safe_move(self):
        if len(self.safes):
            cell=self.safes.pop()
            self.moves_made.add(cell)
            return cell
        else: 
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.cells)==0:
            return None
        cell = random.choice(list(self.cells))
        self.cells.discard(cell)
        self.moves_made.add(cell)
        return cell
