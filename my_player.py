from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import math
import time

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)
        self.time_used = 0  # Initialize time_used to track total time spent
        self.total_time_budget = 900  # Set a 15-minute (900 seconds) time budget


    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """
        remaining_game_time = self.total_time_budget - self.time_used
        depth = self.get_dynamic_depth(remaining_game_time)

        # Start timing for this move
        start_time = time.time()

        # Call minimax with alpha-beta pruning
        _, action = self.minimax(current_state, depth, -math.inf, math.inf, True)
        
        # End timing and update time used
        self.time_used += time.time() - start_time
        
        # Verify action validity
        if action in current_state.generate_possible_light_actions():
            return action
        raise MethodNotImplementedError("No valid action found.")
    
    def get_opponent_id(self, game_state: GameStateDivercite):
        """
        Returns the opponent's ID based on the current game state.
        """
        # Retrieve the current player's ID
        current_player_id = self.get_id()
    
        # Check the players list in game_state and return the ID of the opponent
        for player in game_state.players:
            if player.get_id() != current_player_id:
                return player.get_id()
    
    def get_dynamic_depth(self, remaining_time):
        """
        Determine the depth based on remaining time.
        """
        if remaining_time > 600:  #If we got more than 10 minutes left
            return 3  # Maximum depth for early game: encourages exploration
        elif remaining_time > 300:  #If we have between 5 and 10 minutes left
            return 2  #Moderate depth for mid-game
        else:  # Less than 5 minutes left
            return 1  #Little depth for late game: focus on immediate outcomes
    
    def minimax(self, state, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning
        """
        if depth == 0 or state.is_done():
            return self.evaluate_state(state), None
        
        best_action = None
        if maximizing_player:
            max_value = -math.inf
            for action in state.generate_possible_light_actions():
                new_state = state.apply_action(action)
                value, _ = self.minimax(new_state, depth - 1, alpha, beta, False) #Double recursion
                if value > max_value:
                    max_value = value
                    best_action = action
                    alpha = max_value
                if max_value >= beta:
                    break
            return max_value, best_action
        else:
            min_value = math.inf
            for action in state.generate_possible_light_actions():
                new_state = state.apply_action(action)
                value, _ = self.minimax(new_state, depth - 1, alpha, beta, True) #Double recursion
                if value < min_value:
                    min_value = value
                    best_action = action
                    beta = min_value
                if min_value <= alpha:
                    break
            return min_value, best_action
    
    def evaluate_state(self, state: GameStateDivercite) -> float:
        """
        Custom heuristic to evaluate the game state. This heuristic considers:
        - Score differences between players.
        - The number of Divercité formations possible (4 different resources around a city).
        - The proximity of resources that might benefit the opponent.
        """
        player_score = state.scores[self.get_id()]
        opponent_score = state.scores[self.get_opponent_id(state)]
        
        divercite_bonus = 5  # Points for a Divercité formation
        score_diff = player_score - opponent_score
        
        # Additional heuristic: Count potential Divercité formations
        # This allows to strategically position the agent to encourage Divercité formations (high scoring)
        divercite_potential = self.count_divercite_potential(state, self.get_id()) - self.count_divercite_potential(state, self.get_opponent_id(state))
        
        return score_diff + divercite_potential * divercite_bonus
    
    def count_divercite_potential(self, state, player_id) -> int:
        """
        Count potential Divercité formations for a given player.
        """
        count = 0
        for i in range(state.get_rep().get_dimensions()[0]):
            for j in range(state.get_rep().get_dimensions()[1]):
                if state.in_board((i, j)) and state.get_rep().get_env().get((i, j)):
                    piece = state.get_rep().get_env()[(i, j)]
                    if piece.get_owner_id() == player_id and state.check_divercite((i, j)):
                        count += 1
        return count
    

