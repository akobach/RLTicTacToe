import numpy as np
from tqdm import tqdm

class TicTacToe():
    def __init__(self, policyA, policyB):
        self.policyA = policyA # playerA policy
        self.policyB = policyB # playerB policy
        self.clear_board() # create a fresh game
        
    def clear_board(self):
        self.board = np.zeros((3, 3), dtype=int)
        self.turn = 1 # player A = 1, player B = -1
        self.game_is_over = False # Boolean
        self.winner = None # 1 for player A, -1 for player B, None if draw or game isn't over
        self.game_ledger = []

    def print_board(self):
        print()
        print(self.board)
        
    def print_boards(self):
        print()
        for board in self.game_ledger:
            print(board)
            print()

    def make_move(self, marker, position):
        i = position // 3
        j = position % 3
        self.board[i][j] = marker

    def play_game(self, visualize=False, clear_board_when_over=True):
        if visualize:
            self.print_board()
                
        # loop until game is over
        while not self.game_is_over:
            # use policy for the turn
            if self.turn == 1:
                policy = self.policyA 
            else:
                policy = self.policyB
                
            # decide move
            current_board = self.board.copy()
            self.game_ledger.append(self.board.copy()) # record of moves
            move = policy.get_move(current_board, self.turn)
            self.make_move(self.turn, move)
            next_board = self.board.copy()
            self.check_for_winner()
            
            # learn
            policy.learn(current_board, move, next_board, self.turn, self.winner, self.game_is_over)
            
            # switch players
            if self.turn == 1:
                self.turn = -1
            else:
                self.turn = 1
                
            # print board 
            if visualize:
                self.print_board()
                print(f"Winner so far: {self.winner}")
                
        self.game_ledger.append(self.board.copy())
        
        if visualize:
            print(f"Final Winner: {self.winner}")     
            
        # clear game data and start anew
        if clear_board_when_over:
            self.clear_board()                     
        
        
    def check_for_winner(self):
        # check to see if board is full
        if len([x for x in self.board.flatten() if x==0]) == 0:
            self.game_is_over = True
            self.winner = None 
        
        # 8 checks to see if there is a winning configuration
        checks = []
        checks.append(self.board[0][0] + self.board[0][1] + self.board[0][2])
        checks.append(self.board[1][0] + self.board[1][1] + self.board[1][2])
        checks.append(self.board[2][0] + self.board[2][1] + self.board[2][2])
        checks.append(self.board[0][0] + self.board[1][0] + self.board[2][0])
        checks.append(self.board[0][1] + self.board[1][1] + self.board[2][1])
        checks.append(self.board[0][2] + self.board[1][2] + self.board[2][2])
        checks.append(self.board[0][0] + self.board[1][1] + self.board[2][2])
        checks.append(self.board[0][2] + self.board[1][1] + self.board[2][0])

        # see if any checks correspond to wins
        checks = [int(check/3) for check in checks if int(check/3) != 0]

        if len(checks) != 0:
            self.game_is_over = True
            self.winner = checks[0]
        
    def test(self, N=100):
        winners = np.full(N, np.nan)
        for i in tqdm(range(N)):
            self.play_game(clear_board_when_over=False)
            winners[i] = self.winner
            self.clear_board()
            
        # print stats
        n_playerA_wins = (winners==1).sum()
        n_playerB_wins = (winners==-1).sum()
        n_draws = N - n_playerA_wins - n_playerB_wins
        print(f"Player A won {n_playerA_wins}/{N} games ({100*n_playerA_wins/N}%)")
        print(f"Player B won {n_playerB_wins}/{N} games ({100*n_playerB_wins/N}%)")
        print(f"Number of draws: {n_draws}/{N}")
            