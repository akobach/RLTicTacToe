from tqdm import tqdm
from collections import Counter



class Player:
    X = 1
    O = 2
    NEITHER = 3
    


class Moves:
    SQ0 = int("100000000", 2)
    SQ1 = int("010000000", 2)
    SQ2 = int("001000000", 2)
    SQ3 = int("000100000", 2)
    SQ4 = int("000010000", 2)
    SQ5 = int("000001000", 2)
    SQ6 = int("000000100", 2)
    SQ7 = int("000000010", 2)
    SQ8 = int("000000001", 2)
    ALL = (SQ0, SQ1, SQ2, SQ3, SQ4, SQ5, SQ6, SQ7, SQ8)
    


class EndGameConfigs:
    ROW1 = int("111000000", 2)
    ROW2 = int("000111000", 2)
    ROW3 = int("000000111", 2)
    COL1 = int("100100100", 2)
    COL2 = int("010010010", 2)
    COL3 = int("001001001", 2)
    DGN1 = int("100010001", 2)
    DGN2 = int("001010100", 2)
    ALL = (ROW1, ROW2, ROW3, COL1, COL2, COL3, DGN1, DGN2)
    DRAW = int("111111111", 2)
    


class Board:
    """
    - This class contains information regarding the state of the Tic Tac Toe board
    - self.turn is the player who is to move next, given the board configuration
        WLOG, X always goes first in a new game
    - self.x and self.o are attributes that encode the locations of X's and O's, respectively
        The encoding follows big endian format, where the location in the bit string
        corresponds to the following board positions:
       |   |
     0 | 1 | 2
    ___|___|___ 
       |   |
     3 | 4 | 5
    ___|___|___ 
       |   |
     6 | 7 | 8
       |   | 
    """
    
    def __init__(self, boardstring: str=None):
        self.x = int("000000000", 2)
        self.o = int("000000000", 2)
        
        # always start with player X
        self.turn = Player.X
        
        # can make a board state by specifying string for board
        # ex: "X--O--X--X"
        if boardstring:
            xs = ["0" for _ in range(9)]
            os = ["0" for _ in range(9)]
            for i,s in enumerate(boardstring):
                if s == "X":
                    xs[i] = "1"
                if s == "O":
                    os[i] = "1"
            self.x = int("".join(xs), 2)
            self.o = int("".join(os), 2)
            
            
    def update_board(self, move: int) -> None:
        """
        Inputs an integer associated with the square selected in the move (0-8)
        Updates the board based on whose turn it is
        Then updates the turn
        """
        movebin = Moves.ALL[move]
        if self.turn == Player.X:
            self.x = self.x | movebin
            self.turn = Player.O
        else:
            self.o = self.o | movebin
            self.turn = Player.X
                
                
    def empty_spaces(self) -> str:
        """
        Returns a string of 0's and 1's corresponding to the taken positions on the board
        "1" means the space is taken, "0" means the space is empty
        """
        return "{0:09b}".format(self.x | self.o)
    
    
    def print_board(self) -> None:
        """
        For debugging
        """
        print(f"x: {"{0:09b}".format(self.x)}")
        print(f"o: {"{0:09b}".format(self.o)}")
        print(f"turn: {self.turn}")
        print(f"empty: {self.empty_spaces()}")
        
        
    def key(self) -> int:
        """
        Returns an unique integer associated with the board 
        """
        return (self.x << 9) | self.o
    
    def __hash__(self) -> int:
        return self.key()
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.o == other.o
    
    
    
class TicTacToe():
    def __init__(self, policyX, policyO):
        # policies for players X and O
        # these have to be policies that inherent from the tttPolicy base class
        self.policyX = policyX 
        self.policyO = policyO 
        
        # current board before the move
        # next board after the move
        self.currentboard = Board()
        self.nextboard = Board()
        
        # index (0-8) of the board position changes during a move
        self.move = None
        
        # Boolean whether the game is over
        self.gameover = False
        
        # True if X won, False is O won, None otherwise (eg a draw or if the same is not over yet)
        self.winner = Player.NEITHER 
        
        # interation count, just for testing
        self.iterations = 0
        
        
    def clear_game(self) -> None:
        """
        resets all board data back to initial configuration (without expliclitly reitializing)
        """
        self.currentboard.x = int("000000000", 2) 
        self.currentboard.o = int("000000000", 2)
        self.currentboard.turn = Player.X
        self.nextboard.x = int("000000000", 2)
        self.nextboard.o = int("000000000", 2)
        self.nextboard.turn = Player.X
        self.move = None
        self.gameover = False
        self.winner = Player.NEITHER
        
        
    def play_game(self, clearwhenover: bool=True, debug: bool=False) -> None:
        """
        Play a game of Tic Tac Toe until there is a winner
        optional arguments: 
            - cleanwhenover: clear the game once game is over 
            - debug: print the board state at every step
        """
        
        # loop until the game is over
        while not self.gameover:     
            self.iterations += 1
            
            # get the policy
            if self.currentboard.turn == Player.X:
                policy = self.policyX
            else: 
                policy = self.policyO
                
            # get the move
            self.move = policy.get_move(game=self)
                
            # update next board
            self.nextboard.update_board(move=self.move)    
            
            # check for winner
            self.check_for_winner()
            
            # print game state for debugging
            if debug:
                self.print_game_state()
            
            # learn
            policy.learn(game=self)
                
            # update current board to match next board
            self.currentboard.update_board(move=self.move)
                        
        if clearwhenover:
            self.clear_game()
        
        
    def check_for_winner(self) -> None:
        # get the next board
        # remember: turns are what lead from the board, not what leads to it
        board = self.nextboard
        
        for endconfig in EndGameConfigs.ALL:
            if board.turn == Player.X and (board.o & endconfig) == endconfig:
                self.gameover = True
                self.winner = Player.O
                
            if board.turn == Player.O and (board.x & endconfig) == endconfig:
                self.gameover = True
                self.winner = Player.X
        
        if (board.x | board.o) == EndGameConfigs.DRAW: 
            self.gameover = True
            self.winner = Player.NEITHER
            
            
    def test(self, N):
        results = []
        for _ in tqdm(range(N)):
            self.play_game(clearwhenover=False)
            results.append(self.winner)
            self.clear_game()
            
        counter = Counter(results)
        print()
        print("Dictionary of testing results:")
        print("1: number of times player X wins")
        print("2: number of times player O wins")
        print("3: number of times the game ends in a draw")
        print(f"Results: {counter}")
            
            
    def print_game_state(self):
        """
        For debugging
        """
        print()
        print(f"current x: {"{0:09b}".format(self.currentboard.x)}")
        print(f"curernt o: {"{0:09b}".format(self.currentboard.o)}")
        print(f"curernt turn: {self.currentboard.turn}")
        print(f"current empty: {self.currentboard.empty_spaces()}")
        print(f"move: {self.move}")
        print(f"next x: {"{0:09b}".format(self.nextboard.x)}")
        print(f"next o: {"{0:09b}".format(self.nextboard.o)}")
        print(f"next turn: {self.nextboard.turn}")
        print(f"next empty: {self.nextboard.empty_spaces()}")
        print(f"winner: {self.winner}")
        print(f"game over: {self.gameover}")