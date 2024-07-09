import tttpolicies
import tttgame


if __name__ == "__main__":
    
    # policy for random player
    #randompolicy = tttpolicies.RandomPolicy()

    
    # Q policy
    qpolicy = tttpolicies.QPolicy(input_file=None,
                                  epsilon=0)
                       
    # train Q policy          
    qpolicy.train(N=2*10**5,
                    output_file="qtable.pkl",
                    epsilon=0.5,
                    discount_factor=1,
                    learning_rate=0.5,
                    track_boards=["X-O---X--",
                                  "OXX---O-X",
                                  "X------O-",
                                  "-XO-XO---"])
    
    # plot the tracked boards
    qpolicy.plot_training_results()
    
    
    
    """
    # test the results
    # two perfect players will always end in a draw
    qpolicy = tttpolicies.QPolicy(input_file="qtable.pkl",
                                  epsilon=0)
    
    # define game players
    game = tttgame.TicTacToe(policyX=qpolicy,
                             policyO=qpolicy)
    
    game.test(N=10**2)
    """
    