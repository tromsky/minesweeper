import itertools
import random


class Minesweeper:
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


class Sentence:
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

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def __repr__(self):
        return str(self)

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if len(self.cells) == self.count:
            return self.cells

        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.count == 0:
            return self.cells

        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def get_all_cells(self):
        """
        Returns all possible cells on the board
        """

        cells = set()

        for row in range(0, self.height - 1):
            for col in range(0, self.width - 1):
                cells.add((row, col))

        return cells

    def get_neighbours(self, cell):
        """
        Get a set of all neighbouring cells regardless of their determinations,
        but sets exclude the current cell
        """

        neighbouring_rows = set()
        neighbouring_cols = set()
        neighbouring_cells = set()

        # rows
        current_row = cell[0]
        neighbouring_rows.add(current_row)
        if current_row > 0:
            neighbouring_rows.add(current_row - 1)
        if current_row < self.height - 1:
            neighbouring_rows.add(current_row + 1)

        # cols
        current_col = cell[1]
        neighbouring_cols.add(current_col)
        if current_col > 0:
            neighbouring_cols.add(current_col - 1)
        if current_col < self.width - 1:
            neighbouring_cols.add(current_col + 1)

        # neighbouring cells
        for row in neighbouring_rows:
            for col in neighbouring_cols:
                if (row, col) == cell:
                    continue
                neighbouring_cells.add((row, col))

        return neighbouring_cells

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def generate_inferences(self):
        """
        Compare all sentences in knowledge in pairs
        If set2 is a subset of set1, then take a delta of the set and count
        and add it to the knowledge base
        """

        # get's rid of any empty sentences that contain no insight
        self.perform_cleanup()

        for sentence_one, sentence_two in itertools.combinations(self.knowledge, 2):
            if sentence_one != sentence_two:

                if sentence_one.cells.issubset(sentence_two.cells):
                    subset = sentence_two.cells - sentence_one.cells
                    count = sentence_two.count - sentence_one.count
                    sentence = Sentence(cells=subset, count=count)

                    if sentence not in self.knowledge and len(subset) > 0:
                        self.knowledge.append(sentence)

    def perform_cleanup(self):
        """
        Remove empty sentences from the knowledge base just to keep it clean
        """

        empty_sentence = Sentence(cells=set(), count=0)

        try:
            while True:
                self.knowledge.remove(empty_sentence)
        except ValueError:
            pass

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

        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbours = self.get_neighbours(cell)
        sentence = Sentence(cells=neighbours, count=count)
        self.knowledge.append(sentence)

        for sentence in self.knowledge:
            for safe_cell in self.safes:
                sentence.mark_safe(safe_cell)
            for mine_cell in self.mines:
                sentence.mark_mine(mine_cell)

        self.generate_inferences()

        for sentence in self.knowledge:
            self.safes = self.safes | sentence.known_safes()
            self.mines = self.mines | sentence.known_mines()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        unplayed_safes = self.safes - self.moves_made

        if unplayed_safes:
            return unplayed_safes.pop()

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        all_cells = self.get_all_cells()
        unplayed = all_cells - self.moves_made
        unplayed_not_mines = unplayed - self.mines

        if unplayed_not_mines:
            return random.choice(list(unplayed_not_mines))

        return None
