import tttgame
import tttpolicies
import cProfile

if __name__ == "__main__":
     
    """
    # play a game with two random policies
    randompolicy = tttpolicies.RandomPolicy()
    game = tttgame.TicTacToe(policyX=randompolicy,
                             policyO=randompolicy)
    game.play_game(debug=True)
    """
    
                        
    # train a Q policy          
    qpolicy = tttpolicies.QPolicy(input_file=None,
                                  epsilon=0)
    qpolicy.train(N=2*10**5,
                  output_file="qtable.pkl",
                  epsilon=0.5,
                  discount_factor=1,
                  learning_rate=0.5,
                  track_boards=["X-O---X--",
                                "OXX---O-X",
                                "X------O-",
                                "-XO-XO---"])
    
    
    # plot traninging results of tracked boards
    qpolicy.plot_training_results()
    
    
    # play many games with two policies, and see who wins more often
    qpolicy = tttpolicies.QPolicy(input_file="qtable.pkl",
                                  epsilon=0)
    
    game = tttgame.TicTacToe(policyX=qpolicy,
                             policyO=qpolicy)
    
    game.test(N=10**3)
    
    
    
    
    
    
    
    
    
        
