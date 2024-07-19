import abc
import numpy as np
import random
import sys
import tttgame
from tqdm import tqdm
import matplotlib.pyplot as plt
import pickle



class tttPolicy:
    @abc.abstractmethod
    def get_move(self):
        raise NotImplementedError("Subclass needs to implement get_move()")
    
    @abc.abstractmethod
    def learn(self):
        raise NotImplementedError("Subclass needs to implement learn()")



class RandomPolicy(tttPolicy):
    @staticmethod
    def random_move(game: tttgame.TicTacToe) -> int:
        empty_indices = [i for i,b in enumerate(game.currentboard.empty_spaces()) if b=="0"]
        return random.choice(empty_indices)
    
    def get_move(self, game: tttgame.TicTacToe) -> int:
        return self.random_move(game)
    
    def learn(self, game=None):
        pass
    
    
    
class BoardQTable:
    def __init__(self, board):
        """
        This initialization will fill an array of random floats
            then mask them with +/-infinity based on whose turn it is
        The attributes qbest and iqbest are the min/max of the qvalues and its index
        """
        init_values = np.random.randn(9)
        empty = board.empty_spaces()
        
        if board.turn == tttgame.Player.X:
            mask = -float("inf")
            ext = np.max
            argext = np.argmax
        if board.turn == tttgame.Player.O:
            mask = float("inf")
            ext = np.min
            argext = np.argmin
            
        self.qvalues = np.asarray([x if empty[i]=="0" else mask for i,x in enumerate(init_values)])
        self.qbest = ext(self.qvalues)
        self.iqbest = argext(self.qvalues)
        
        
        
class QPolicy(tttPolicy):
    def __init__(self, input_file: str=None, epsilon: float=0):
        """
        This class requires two input parameters:
            input_file: (str) optional input pickle file if loading Q dictionary
                              if no input file provided, create an empty dictionary
            epsilon: (float) the value ofo the greedy epsilon 
        """
        self.file = input_file
        self.epsilon = epsilon
        self.learning_rate = 0
        self.discount_factor = 0
        
        # qdict is a dictionary 
        # the keys are integers created with hash(Board) 
        # the values are BoardQTable objects
        self.qdict = self.load_qdict()
        
        
    def load_qdict(self):
        if self.file is None: 
            return dict()       
        try:
            with open(self.file, "rb") as f:
                return pickle.load(f)
        except Exception as error:
            print(error)
            print(f"ERROR! Cannot open {self.file}. Exiting...")
            sys.exit()
    
    
    def save(self, output_file):
        # save Q tabel to a pickle file
        with open(output_file, "wb") as f:
            pickle.dump(self.qdict, f)
        
        
    def get_board_qtable(self, board: tttgame.Board=None) -> BoardQTable:
        """
        This function does more than just access than qtable
        It creates a new BoardQTable object if it doesn't already exist
        """                
        key = hash(board)
        
        # if board has not been accessed before, create BoardQTable for it
        if key not in self.qdict.keys():
            self.qdict[key] = BoardQTable(board)  
    
        # return BoardQTable object
        return self.qdict[key]
        
        
    def get_move(self, game: tttgame.TicTacToe) -> int:
        # epsilon greedy policy
        if np.random.rand() < self.epsilon:
            return RandomPolicy.random_move(game)
        else:
            current_boardqtable = self.get_board_qtable(board=game.currentboard)
            return current_boardqtable.iqbest
        
        
    def learn(self, game: tttgame.TicTacToe) -> None:
        if game.gameover:
            if game.winner == tttgame.Player.X:
                Qext = 0
                R = 1
            if game.winner == tttgame.Player.O:
                Qext = 0
                R = -1
            if game.winner == tttgame.Player.NEITHER:
                Qext = 0
                R = 0
                        
        if not game.gameover:
            next_boardqtable = self.get_board_qtable(board=game.nextboard)
            R = 0
            Qext = next_boardqtable.qbest
        
        # update current BoardQTable object 
        current_boardqtable = self.get_board_qtable(board=game.currentboard)
        new_q_value = (1 - self.learning_rate)*current_boardqtable.qvalues[game.move] + self.learning_rate*(R + self.discount_factor*Qext)
        current_boardqtable.qvalues[game.move] = new_q_value
        
        if game.currentboard.turn == tttgame.Player.X:
            if new_q_value > current_boardqtable.qbest:
                current_boardqtable.qbest = new_q_value
            else:
                current_boardqtable.iqbest = np.argmax(current_boardqtable.qvalues)
                current_boardqtable.qbest = current_boardqtable.qvalues[current_boardqtable.iqbest]
                
        if game.currentboard.turn == tttgame.Player.O:
            if new_q_value < current_boardqtable.qbest:
                current_boardqtable.qbest = new_q_value
            else:
                current_boardqtable.iqbest = np.argmin(current_boardqtable.qvalues)
                current_boardqtable.qbest = current_boardqtable.qvalues[current_boardqtable.iqbest]
        

    def train(self, **kwargs):
        """
        This will train the Q policy by making it play itself in Tic Tac Toe
        Input parameters:
            N: (int) number of games to simulate
            output_file: (str) name of output pickle file to save for later
            epsilon: (float) value of greedy epsilon to use for training
            learning_rate: (float) usually called alpha in my textbook
            dicount_factor: (float) usually called gamma in my textbook
            track_boards: (list) list of strings
                            Each string can be used to define a Board() class
                            Use this if you want to track 2 or more boards
                            After training, plot results with plot_training_results()
        """
        
        N = kwargs["N"]
        output_file = kwargs["output_file"]
        self.epsilon = kwargs["epsilon"]
        self.learning_rate = kwargs["learning_rate"]
        self.discount_factor = kwargs["discount_factor"]
        self.track_boards = kwargs["track_boards"]
        
        # create empty array to keep training data for tracked boards
        data = np.zeros((len(self.track_boards), N, 9)) 
        
        game = tttgame.TicTacToe(policyX=self, 
                                 policyO=self)
        
        # play games
        for i in tqdm(range(N)):
            game.play_game()
            for j,boardstr in enumerate(self.track_boards):
                track = tttgame.Board(boardstr)
                if hash(track) in self.qdict.keys():
                    data[j][i] = self.qdict[hash(track)].qvalues
                else:
                    data[j][i] = None
        print(f"Total number of iterations: {game.iterations}")
        self.save(output_file)
        self.data = data
    
    
    def plot_training_results(self):        
        # plot
        fig, ax = plt.subplots(len(self.track_boards), 2)
        for i,row in enumerate(ax):
            # Q values
            row[0].plot(self.data[i])
            row[0].legend(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"), loc="upper left")
            row[0].set_ylabel("Q values")
            
            # tic tac toe board
            xmin, xmax = (-0.35, 2.65)
            row[1].set_xlim([xmin, xmax])
            row[1].set_ylim([xmin, xmax])
            row[1].set_xticks(np.arange(xmin, xmax, 1))
            row[1].set_yticks(np.arange(xmin, xmax, 1))
            row[1].tick_params(axis='both', which='major', labelsize=0)
            row[1].grid()
                        
            shiftx, shifty = (0.5, -0.3)
            for j in range(9):
                row[1].text(j%3, 2-int(j/3), self.track_boards[i][j], fontsize=30)
                row[1].text(j%3+shiftx, 2-int(j/3)+shifty, str(j), fontsize=10, color="r")
                
        plt.show()