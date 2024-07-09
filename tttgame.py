from bitarray import bitarray, frozenbitarray
from bitarray.util import ba2int
from collections import Counter
from tqdm import tqdm

  
class TicTacToe():
    def __init__(self, policyX, policyO):
        # policies for players X and O
        self.policyX = policyX 
        self.policyO = policyO 
        
        # current board before the move
        # next board after the move
        self.current_board = BoardState()
        self.next_board = BoardState()
        
        # index of the boards' bitarrays that changes during a move
        self.move = None
        
        # Boolean whether it is X's turn
        self.Xturn = True
        
        # Boolean whether the game is over
        self.game_over = False
        
        # True if X won, False is O won, None otherwise (eg a draw or if the same is not over yet)
        self.Xwon = None 
        
        
    def clear_game(self):
        # resets all board data back to initial configuration
        self.current_board.x.setall(0) 
        self.current_board.o.setall(0)
        self.next_board.x.setall(0) 
        self.next_board.o.setall(0)
        self.move = None
        self.Xturn = True
        self.game_over = False
        self.Xwon = None
     
     
    def play_game(self, clearwhenover=True, debug=False):
        """
        Play a game of Tic Tac Toe until there is a winner
        optional arguments: 
            - cleanwhenover (Boolean)
                clear the game once game is over 
                default: True 
            - debug (Boolean)
                print the board state at every step
                default: False
        """
        
        # loop until the game is over
        while not self.game_over:     
            if self.Xturn:
                policy = self.policyX
                self.move = policy.get_move(self)
                self.next_board.x[self.move] = 1
            else: 
                policy = self.policyO
                self.move = policy.get_move(self)
                self.next_board.o[self.move] = 1
            
            # check for winner
            self.check_for_winner(self.next_board)
            
            # print game state for debugging
            if debug:
                self.print_game_state()
            
            # learn
            policy.learn(game=self)
                
            # update current board to match next board
            if self.Xturn:
                self.current_board.x[self.move] = 1
            else:
                self.current_board.o[self.move] = 1
            
            # switch players
            self.Xturn = not self.Xturn
                        
        if clearwhenover:
            self.clear_game()
    
    
    def check_for_winner(self, board):
        for win_config in EndGameConfigs.ALL:
            if (board.x & win_config)==win_config or (board.o & win_config)==win_config:
                self.game_over = True
                self.Xwon = self.Xturn
                return
        
        if board.empty_spaces()==EndGameConfigs.DRAW:
            self.game_over = True
            self.Xwon = None
        
            
    def print_game_state(self):
        print()
        print(f"current x: {self.current_board.x}")
        print(f"curernt o: {self.current_board.o}")
        print(f"current empty: {self.current_board.empty_spaces()}")
        print(f"next x: {self.next_board.x}")
        print(f"next o: {self.next_board.o}")
        print(f"next empty: {self.next_board.empty_spaces()}")
        print(f"Xturn: {self.Xturn}")
        print(f"X won: {self.Xwon}")
        print(f"game over: {self.game_over}")
        
        
    def test(self, N):
        results = []
        for _ in tqdm(range(N)):
            self.play_game(clearwhenover=False)
            results.append(self.Xwon)
            self.clear_game()
            
        counter = Counter(results)
        print(counter)
        
        

class BoardState:
    def __init__(self, boardstr=None):
        # one hot encoding for locations of X's and O's
        # both initilized to all 0's
        self.x = bitarray(9) 
        self.o = bitarray(9)
                
        # can make a board state by specifying string for board
        # ex: "X--O--X--X"
        if boardstr:
            for i,s in enumerate(boardstr):
                if s == "X":
                    self.x[i] = 1
                if s == "O":
                    self.o[i] = 1
   
    def empty_spaces(self):
        # return bitarray of empty spaces
        # 1 is taken space, 0 is empty space
        return self.x | self.o
    
    def __hash__(self):
        tmp = (ba2int(self.x), ba2int(self.o))
        return hash(tmp)
    
    def __eq__(self, other):
        return self.x == other.x and self.o == other.o



class EndGameConfigs:
    # winning configurations
    ROW1 = frozenbitarray("111000000")
    ROW2 = frozenbitarray("000111000")
    ROW3 = frozenbitarray("000000111")
    COL1 = frozenbitarray("100100100")
    COL2 = frozenbitarray("010010010")
    COL3 = frozenbitarray("001001001")
    DGN1 = frozenbitarray("100010001")
    DGN2 = frozenbitarray("001010100")
    ALL = (ROW1, ROW2, ROW3, COL1, COL2, COL3, DGN1, DGN2)
    
    # all spaces taken is a draw
    DRAW = frozenbitarray("111111111")
  