import tttpolicies 
import tttgame
        

if __name__ == "__main__":

    # train Q-learning policy
    Qpolicy = tttpolicies.QTablePolicy(input_file=None,
                                       epsilon=0.7)
    
    Qpolicy.train(output_file="qtable.hkl",
                  N=10**6,
                  learning_rate=0.5,
                  discount_factor=1,
                  track_boards=["210111211"
                                ,"022111012"
                                #,"210111210"
                                #,"210111111"
                                ,"211111101"
                                ,"120120111"
                                ])
    
    Qpolicy.plot_training_results()
    
    
    # test
    """Qpolicy = tttpolicies.QTablePolicy(input_file="qtable.hkl", epsilon=0.0)
    
    #game = tttgame.TicTacToe(policyA=Qpolicy, policyB=tttpolicies.RandomPolicy())
    game = tttgame.TicTacToe(policyA=Qpolicy, policyB=Qpolicy)              

    game.test(N=10**3)"""
 
    
    # play
    """Qpolicy = tttpolicies.QTablePolicy(input_file="qtable.hkl",
                                       epsilon=0.0)
    
    game = tttgame.TicTacToe(policyA=Qpolicy, 
                             policyB=tttpolicies.ManualPolicy())
    
    game.play_game(visualize=True)"""
    
    
    
    
