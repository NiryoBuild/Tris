# This is a variant of the Tic Tac Toe recipe given in the easyAI library

from ctypes.wintypes import HINSTANCE
from easyAI import TwoPlayersGame, AI_Player, Negamax
from easyAI.Player import Human_Player
from copy import deepcopy

class GameController(TwoPlayersGame):
    def __init__(self, players, nplayer):
        # Define the players
        self.players = players

        # Define who starts the game
        self.nplayer = nplayer 

        # Define the board
        self.board = [0] * 9
        self.history = []

    def inizio_mossa_robot(self):
        if self.nplayer == 2: 
            move = self.player.ask_move(self)
  
            self.history.append((deepcopy(self), move))
            self.make_move(move)
            
            print( "\nMossa plays %s :"%(str(move)) )
            self.show()
                
            self.switch_player()

            return self.history[0][1]
        else: return None
    
    def play(self, mossa):
        n_mosse = len(self.history)

        for _ in range(2):
            isover, vincitore = self.is_over()
            if isover:
                return vincitore
            
            move = mossa
            if self.player.name == 'AI':
                move = self.player.ask_move(self)
            
            self.history.append((deepcopy(self), move))
            self.make_move(move)
            
            print( "\nMossa plays %s :"%(str(move)) )
            self.show()
                
            self.switch_player()

        return self.history[n_mosse+1][1]
    
    # Define possible moves
    def possible_moves(self):
        return [a + 1 for a, b in enumerate(self.board) if b == 0]
    
    # Make a move
    def make_move(self, move):
        self.board[int(move) - 1] = self.nplayer

    # Does the opponent have three in a line?
    def loss_condition(self):
        possible_combinations = [[1,2,3], [4,5,6], [7,8,9],
            [1,4,7], [2,5,8], [3,6,9], [1,5,9], [3,5,7]]

        return any([all([(self.board[i-1] == self.nopponent)
                for i in combination]) for combination in possible_combinations]) 
        
    # Check if the game is over
    def is_over(self):
        if  (self.possible_moves() == []): return True, "Partita finita\nAbbiamo pareggiato! Bella partita!"
        if self.loss_condition(): 
            if self.player.name == 'AI': return True, "Partita finita\nComplimenti hai vinto!"
            return True, "Partita finita\n Ho vinto!"
        return False, ""

    # Show current position
    def show(self):
        print('\n'+'\n'.join([' '.join([['.', 'O', 'X'][self.board[3*j + i]]
                for i in range(3)]) for j in range(3)]))
                 
    # Compute the score
    def scoring(self):
        return -100 if self.loss_condition() else 0

if __name__ == "__main__":
    # Define the algorithm
    algorithm = Negamax(7)

    # Start the game
    GameController([Human_Player(), AI_Player(algorithm)]).play()

