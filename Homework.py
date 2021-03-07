
class Game:

    def __init__(self, board_filename):
        self.board = [[]]
        self.my_color = 'w'
        self.game_type = "single"

        # read board (this will update the board and other relative properties
        self.read_board(board_filename)
        self.player_w = Player(self.board)
        self.player_b = Player(self.board)

    def read_board(self, filename):
        pass


class Player:

    def __init__(self, board):
        self.tokens = []
        self.board = board

    def assign_tokens(self):
        pass

    def get_available_tokens(self):
        jump_available_tokens = []
        move_available_tokens = []
        for token in self.tokens:
            if token.read_to_jump:
                pass
            else:
                if len(token.available_moves) != 0:
                    move_available_tokens.append(token)
        if len(jump_available_tokens) != 0:
            return jump_available_tokens
        else:
            return move_available_tokens

    def check_jump_availability(self, token):
        """
        Check if a given marked as "ready to jump" can really jump
        :param token: Give a token marked as "ready to jump"
        :return: True if it's can jump, else False.
        """
        # First check if there's any opponent's token in its front.
        for front in token.front:
            pass


class Token:

    def __init__(self, id, color, pos, is_king=False):
        self.id = id
        self.color = color      # "b" or "w"
        self.position = pos     # [0, 0] ~ [7, 7] where x = rows, y = cols
        self.is_king = is_king
        # The front and back of the white pieces
        self.front = [[1, 1], [1, -1]]   # upper-right, upper-left
        self.back = [[-1, 1], [-1, -1]]  # bottom-right, bottom-left
        if color == 'b':
            self.__swap_back_and_front()
        if is_king:
            self.__swap_back_and_front()

        self.read_to_jump = 0           # if there's any opponent's tokes in the attacking area, mark this as 1
        self.available_moves = self.front
        if pos[1] == 0:
            self.available_moves = self.front[0]
        elif pos[1] == 7:
            self.available_moves = self.front[1]

    def __swap_back_and_front(self):
        """
        Simply swap the back and the front of the token.
        """
        temp = self.front
        self.front = self.back
        self.back = temp

    def to_checker_position(self):
        """
        Return the position as human readable format.
        :return: string (checker format e.g., "a1", 'e6", etc.)
        """
        return f"{chr(ord('a')+self.position[1])}{self.position[0] + 1}"





if __name__ == '__main__':
    t1 = Token(0, 'w', [0, 0])
    print(t1.to_checker_position())