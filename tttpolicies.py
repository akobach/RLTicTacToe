import numpy as np
import random
import hickle as hkl
import sys
import tttgame
import matplotlib.pyplot as plt
from tqdm import tqdm


class RandomPolicy():
    def get_move(self, board, turn):
        empty_indices = [i for i,x in enumerate(board.flatten()) if x == 0]
        return random.choice(empty_indices)
    
    def learn(self, current_state, move, next_state, turn, winner, is_over):
        pass
    

class ManualPolicy():
    def get_move(self, board, turn):
        while True:
            move = int(input("Choose space (0-8): "))
            empty_indices = [i for i,x in enumerate(board.flatten()) if x == 0]
            if move in empty_indices:
                return move
            else:
                print("Space already taken! Try again.")
    
    def learn(self, current_state, move, next_state, turn, winner, is_over):
        pass
                

class QTablePolicy():
    def __init__(self, **kwargs):
        self.file = kwargs["input_file"]
        self.qtable = self.load()
        self.epsilon = kwargs["epsilon"]
        self.learning_rate = 0
        self.discount_factor = 0
        
    def train(self, **kwargs):
        N = kwargs["N"]
        output_file = kwargs["output_file"]
        self.learning_rate = kwargs["learning_rate"]
        self.discount_factor = kwargs["discount_factor"]
        
        game = tttgame.TicTacToe(policyA=self, 
                                 policyB=self) 
        
        # train and track boards
        self.track_keys = kwargs["track_boards"]
        data = np.zeros((len(self.track_keys), N, 9)) 
        
        for i in tqdm(range(N)):
            game.play_game()
            for j,key in enumerate(self.track_keys):
                data[j][i] = self.qtable[int(key, base=3)].copy()
        self.save(output_file)
        self.data = data
        
    
    def plot_training_results(self):        
        # plot
        fig, ax = plt.subplots(len(self.track_keys), 2)
        for i,row in enumerate(ax):
            # Q values
            row[0].plot(self.data[i])
            row[0].legend(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"), loc="upper left")
            row[0].set_ylabel("Q")
            
            # tic tac toe board
            xmin, xmax = (-0.35, 2.65)
            row[1].set_xlim([xmin, xmax])
            row[1].set_ylim([xmin, xmax])
            row[1].set_xticks(np.arange(xmin, xmax, 1))
            row[1].set_yticks(np.arange(xmin, xmax, 1))
            row[1].tick_params(axis='both', which='major', labelsize=0)
            row[1].grid()
            
            get_symbol = lambda x: ["O", None, "X"][int(x)]
            
            shiftx, shifty = (0.5, -0.3)
            for j in range(9):
                row[1].text(j%3, 2-int(j/3), get_symbol(self.track_keys[i][j]), fontsize=30)
                row[1].text(j%3+shiftx, 2-int(j/3)+shifty, str(j), fontsize=10, color="r")
                
        plt.show()
        
    def play_parameters(self, **kwargs):
        self.file = kwargs["input_file"]
        self.qtable = self.load()
        self.epsilon = kwargs["epsilon"]
        self.learning_rate = 0
        self.discount_factor = 0
    
    def load(self):
        if self.file is None: # make a random qtable
            return self.initialize_qtable()            
        else:
            try:
                return hkl.load(self.file)
            except:
                print(f"ERROR! Cannot open {self.file}. Exiting...")
                sys.exit()
                
    def initialize_qtable(self):
        # create # 3^9 arrays, each 9 elements long, filled with normal Gaussian samples
        init_table = np.random.randn(3**9, 9) 
        
        # turn occupied squares into np.nan types
        for i,qboard in enumerate(init_table):
            res = np.base_repr(i, base=3)
            key = "0" * (9-len(res)) + res
            qboard = [q if key[i] == "1" else np.nan for i,q in enumerate(qboard)]
            init_table[i] = qboard    
        
        return init_table
        
            
    def save(self, file):
        hkl.dump(self.qtable, file)
        
    def find_qboard(self, board):
        key = "".join([str(int(x+1)) for x in board.flatten()])
        qboard_index = int(key, 3) # convert from base 3 to base 10
        return qboard_index, self.qtable[qboard_index].copy()
        
    def get_move(self, board, turn):
        qboard_index, qboard = self.find_qboard(board)
        
        # epsilon greedy
        if np.random.rand() < self.epsilon:
            return RandomPolicy().get_move(board, turn)
        
        # return index for highest Q value for player A and lowest for player B
        if turn == 1:
            return np.nanargmax(qboard)
        else:
            return np.nanargmin(qboard)
        
    def learn(self, current_board, move, next_board, turn, winner, is_over):
        current_qboard_index, current_qboard = self.find_qboard(current_board)
        next_qboard_index, next_qboard = self.find_qboard(next_board)
        
        if is_over and winner == 1:
            R = 1
            Qext = 0
        
        if is_over and winner == -1:
            R = -1
            Qext = 0
            
        if is_over and winner is None:
            return
        
        if not is_over:
            R = 0
            if turn == 1:
                Qext = np.nanmax(next_qboard)
            if turn == -1:
                Qext = np.nanmin(next_qboard)
                
        """if not is_over:
            R = 0
            if turn == 1:
                Qext = max([np.nanmax(next_qboard), np.nanmin(next_qboard)], key=abs)
            if turn == -1:
                Qext = max([np.nanmin(next_qboard), np.nanmax(next_qboard)], key=abs)"""
                
        current_qboard[move] += self.learning_rate*(R + self.discount_factor*Qext - current_qboard[move])
        self.qtable[current_qboard_index] = current_qboard  
        
                