from operator import sub, add


class Game:

    def __init__(self, board_filename):
        self.board = {}
        self.my_color = 'w'
        self.game_type = "SINGLE"
        self.time_left = 0.0
        self.__setup(board_filename)

    def __setup(self, board_filename):
        """
        Set up the board, players and other properties for the game.
        """
        white_tokens, black_tokens = self.__read_board(board_filename)
        self.player_w = Player(self.board, white_tokens)
        self.player_b = Player(self.board, black_tokens)

    def __read_board(self, filename):
        """
        Read the board from the given filename
        :param filename: The file that contains given format.
        :return: white and black tokens
        """
        white_tokens = []
        black_tokens = []
        with open(filename, 'r') as f:
            self.game_type = f.readline()
            self.my_color = f.readline()
            self.time_left = float(f.readline())
            for r, line in enumerate(f.readlines()):
                for c, item in enumerate(line.strip()):
                    if item != ".":
                        color = 'w' if item == "w" or item == "W" else 'b'
                        position = (r, c)
                        is_king = item == "W" or item == "B"
                        token = Token(color, position, is_king)
                        self.board[position] = token
                        if color == 'w':
                            white_tokens.append(token)
                        else:
                            black_tokens.append(token)
        return white_tokens, black_tokens


class Player:

    def __init__(self, board, tokens, jump_available_tokens=None, move_available_tokens=None):
        self.board = board
        self.tokens = tokens
        if move_available_tokens is None or jump_available_tokens is None:
            self.move_available_tokens = []
            self.jump_available_tokens = []
            self.check_all_tokens()
        else:
            self.move_available_tokens = move_available_tokens
            self.jump_available_tokens = jump_available_tokens

    def check_all_tokens(self):
        for pos, token in self.board.items():
            self.arc_check(token)
        self.get_available_tokens()

    def arc_check(self, token):
        """
        For each token, check the available moves and its affecting tokens (arcs), so that when the state
        of this token changed (captured, move, or jump), it can notify its affecting tokens to update their
        availabilities.
        """
        # append all arcs for the token
        for corner in token.four_corners:
            if corner in self.board:
                token.arc_set.add(self.board[corner])
        # check for available moves and jump
        for move in token.available_moves:
            if move in self.board:
                tkn = self.board[move]
                if tkn.color == token.color:
                    # remove from available moves if it get blocked
                    token.available_moves.remove(move)
                else:
                    # if there is no other pieces blocking its jump...
                    if not tuple(map(add, move, move)) in self.board:
                        token.read_to_jump = 1

    def get_available_tokens(self):
        self.jump_available_tokens = []
        self.move_available_tokens = []
        for token in self.tokens:
            if token.read_to_jump:
                self.jump_available_tokens.append(token)
            else:
                if len(token.available_moves) != 0:
                    self.move_available_tokens.append(token)
        if len(self.jump_available_tokens) != 0:
            return self.jump_available_tokens
        else:
            return self.move_available_tokens


class Token:

    def __init__(self, color, pos, is_king=False):
        self.color = color      # "b" or "w"
        self.position = pos     # (0, 0) ~ (7, 7) where x = rows, y = cols
        self.is_king = is_king
        # The front and back of the white pieces
        self.front = [(1, 1), (1, -1)]   # upper-right, upper-left
        self.back = [(-1, 1), (-1, -1)]  # bottom-right, bottom-left
        self.four_corners = self.front.extend(self.back)
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

        self.arc_set = {}      # The set of tokens that is blocked by this token

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

    def __str__(self):
        return f"Position: {self.position}\nColor: {self.color}\nKing: {self.is_king}\n" \
               f"Available Moves: {self.available_moves}"


if __name__ == '__main__':
    game = Game("input1.txt")


