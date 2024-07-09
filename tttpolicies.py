import abc
import numpy as np
from bitarray import bitarray 
import random
import sys
import tttgame
from tqdm import tqdm
import matplotlib.pyplot as plt
import pickle



class tttPolicy():
    @abc.abstractmethod
    def get_move(self):
        raise NotImplementedError("Subclass needs to implement get_move()")
    
    @abc.abstractmethod
    def learn(self):
        raise NotImplementedError("Subclass needs to implement learn()")


class RandomPolicy(tttPolicy):
    @staticmethod
    def random_move(game):
        empty_indices = [i for i in game.current_board.empty_spaces().itersearch(bitarray("0"))]
        return random.choice(empty_indices)
    
    def get_move(self, game):
        return self.random_move(game)
    
    def learn(self, **kwargs):
        pass
    

class BoardQTable:
    def __init__(self, board):
        init_values = np.random.randn(9)
        
        # put np.nan values where spaces are taken
        empty = board.empty_spaces()
        self.qvalues = np.asarray([x if empty[i]==0 else np.nan for i,x in enumerate(init_values)])
     
  
class QPolicy(tttPolicy):
    def __init__(self, **kwargs):
        # option to input a pickle file with the Q table
        # if no input file provided, create an empty dictionary
        self.file = kwargs["input_file"]
        
        # qdict is a dictionary 
        # the keys are integers created with hash(BoardState) 
        # the values are BoardQTable objects
        self.qdict = self.load_qdict()
        
        # epsilon value for epsilon-greedy policy
        self.epsilon = kwargs["epsilon"]
        
        # learning rate, usually called alpha
        self.learning_rate = 0
        
        # discoutn factor, usually called gamma
        self.discount_factor = 0
        
        
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
        # saves Q tabel to a pickle file
        with open(output_file, "wb") as f:
            pickle.dump(self.qdict, f)
        
        
    def get_board_qtable(self, game=None, board=None):                
        key = hash(board)
        
        # if board has not been accessed before, create BoardQTable for it
        if key not in self.qdict.keys():
            self.qdict[key] = BoardQTable(board)  
    
        # return BoardQTable object
        return self.qdict[key]
         
         
    def get_move(self, game):
        # epsilon greedy
        if np.random.rand() < self.epsilon:
            return RandomPolicy.random_move(game)
        
        current_boardqtable = self.get_board_qtable(game=game, board=game.current_board)
        if game.Xturn:
            return np.nanargmax(current_boardqtable.qvalues)
        else:
            return np.nanargmin(current_boardqtable.qvalues)
        
        
    def learn(self, **kwargs):
        game = kwargs["game"]
        
        if game.game_over:
            if game.Xwon:
                Qext = 0
                R = 1
            elif not game.Xwon:
                Qext = 0
                R = -1
            else:
                Qext = 0
                R = 0
        
        if not game.game_over:
            next_boardqtable = self.get_board_qtable(game=game, board=game.next_board)    
            R = 0
            if game.Xturn:
                Qext = np.nanmin(next_boardqtable.qvalues)
            else:
                Qext = np.nanmax(next_boardqtable.qvalues)
        
        # update Q value 
        current_boardqtable = self.get_board_qtable(game=game, board=game.current_board)
        new_q_value = (1 - self.learning_rate)*current_boardqtable.qvalues[game.move] + self.learning_rate*(R + self.discount_factor*Qext)
        current_boardqtable.qvalues[game.move] = new_q_value
    

    def train(self, **kwargs):
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
        
        for i in tqdm(range(N)):
            game.play_game()
            for j,boardstr in enumerate(self.track_boards):
                game.current_board = tttgame.BoardState(boardstr)
                data[j][i] = self.get_board_qtable(game=game, board=game.current_board).qvalues
            game.clear_game()
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
        
    