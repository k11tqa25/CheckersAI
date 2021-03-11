import json
from json import JSONEncoder
import numpy as np # just for diplaying the board

def tuple_operation(a, b, operation='a'):
    if operation == 'a':
        return a[0] + b[0], a[1] + b[1]
    elif operation == 's':
        return a[0] - b[0], a[1] - b[1]
    elif operation == 'm':
        return a[0] * b, a[1] * b
    elif operation == 'avg':
        return int((a[0] + b[0])/2), int((a[1] + b[1])/2)
    else:
        return a


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
        self.player_w = Player(self.board, 'w', white_tokens)
        self.player_b = Player(self.board, 'b', black_tokens)
        self.player_w.opponent = self.player_b
        self.player_b.opponent = self.player_w

    def __read_board(self, filename):
        """
        Read the board from the given filename
        :param filename: The file that contains given format.
        :return: white and black tokens
        """
        white_tokens = set()
        black_tokens = set()
        with open(filename, 'r') as f:
            self.game_type = f.readline()
            self.my_color = f.readline()
            self.time_left = float(f.readline())
            for r, line in enumerate(f.readlines()):
                for c, item in enumerate(line.strip()):
                    if item != ".":
                        color = 'w' if item == "w" or item == "W" else 'b'
                        position = (7 - r, c)
                        is_king = item == "W" or item == "B"
                        token = Token(color, position, is_king)
                        self.board[position] = token
                        if color == 'w':
                            white_tokens.add(token)
                        else:
                            black_tokens.add(token)
        return white_tokens, black_tokens


class Player:

    def __init__(self, board, color, tokens, jump_available_tokens=None, move_available_tokens=None):
        self.board = board
        self.tokens = tokens
        self.color = color
        if move_available_tokens is None or jump_available_tokens is None:
            self.check_all_tokens()
        else:
            self.move_available_tokens = move_available_tokens
            self.jump_available_tokens = jump_available_tokens
        self.opponent = None # set up in the Game class

    def get_available_tokens(self):
        self.move_available_tokens = set()
        self.jump_available_tokens = set()
        for token in self.tokens:
            if token.read_to_jump:
                self.jump_available_tokens.add(token)
            else:
                if len(token.available_moves) != 0:
                    self.move_available_tokens.add(token)
        if len(self.jump_available_tokens) != 0:
            return self.jump_available_tokens
        else:
            return self.move_available_tokens

    def check_all_tokens(self):
        for token in self.tokens:
            self.arc_check(token)
        self.get_available_tokens()

    def check_all_jump_tokens(self):
        # Check all the tokens in the board that is read for jumps.
        for token in self.board.values():
            if token.read_to_jump:
                self.arc_check(token)

    def arc_check(self, token):
        """
        For each token, check the available moves and its affecting tokens (arcs), so that when the state
        of this token changed (captured, move, or jump), it can notify its affecting tokens to update their
        availabilities.
        """
        # append all arcs for the token
        token.reset()
        for corner in map(token.get_landing, token.front + token.back):
            if corner in self.board:
                token.arc_set.append(corner)
        # check for available moves and jump
        jump_path = self.__find_all_jump_path(token.position, token.front, token.color)
        token.jump_path.extend(jump_path)
        if len(jump_path) != 0:
            token.read_to_jump = 1
        for move in [m for m in token.available_moves]:
            landing = token.get_landing(move)
            if landing in token.arc_set:
                # TODO: should I remove the move no matter which color is in the way?
                # tkn = self.board[landing]
                # if tkn.color == self.color:
                #     # remove from available moves if it get blocked
                #     token.available_moves.remove(move)
                token.available_moves.remove(move)

    def __find_all_jump_path(self, token_pos, front, color, pre_path=None):
        if pre_path is None:
            pre_path = []
        result = []
        for next_move in front:
            next_front = tuple_operation(token_pos, next_move)
            if next_front in self.board:
                if self.board[next_front].color != color:
                    next_landing = tuple_operation(next_front, next_move)
                    if next_landing not in self.board \
                            and 0 <= next_landing[0] <= 7 \
                            and 0 <= next_landing[1] <= 7:
                        ret = self.__find_all_jump_path(next_landing, front, color, pre_path + [next_landing])
                        if len(ret) > 0:
                            result.extend(ret)

        if len(result) == 0:
            if len(pre_path) > 0:
                result.extend([pre_path])
        return result

    def remove_a_token(self, token):
        """
        Remove a token from its position and notify all affected tokens.
        :param token: The token to remove.
        """
        # 1. Remove the token
        del self.board[token.position]

        # 2. Notify the affected tokens
        for arc in token.arc_set:
            self.arc_check(self.board[arc])

    def place_a_token(self, token, landing):
        """
        Place a token.
        :param token: The token to place
        :param landing: The landing position of the token.
        """
        # Place a token in its place and do the arc check
        token.position = landing
        self.board[landing] = token
        self.arc_check(token)

        # notify all other tokens in the arc
        for arc in token.arc_set:
            notified = self.board[arc]
            self.arc_check(notified)

    def single_move(self, token, move):
        """
        The player will play a move and inform all other tokens that will be affected.
        :param token: The token to move.
        :param move: The move.
        """
        self.remove_a_token(token)
        landing = token.get_landing(move)
        self.place_a_token(token, landing)
        self.check_all_jump_tokens()

    def jump(self, token, path):
        """
        Perform a jump.
        :param token: The token to move.
        :param path: The path of jumps.
        """
        self.remove_a_token(token)
        for i, p in enumerate(path):
            if i == 0:
                tkn = self.board[tuple_operation(token.position, p, 'avg')]
            else:
                tkn = self.board[tuple_operation(p, path[i-1], 'avg')]
            # also really need to remove from the player token list
            self.opponent.tokens.remove(tkn)
            self.remove_a_token(tkn)

        landing = path[-1]
        self.place_a_token(token, landing)
        self.check_all_jump_tokens()


class Token:

    def __init__(self, color, pos, is_king=False):
        self.color = color  # "b" or "w"
        self.position = pos  # (0, 0) ~ (7, 7) where x = rows, y = cols
        self.readable_position = self.to_checker_position()
        self.is_king = is_king
        # The front and back of the white pieces
        self.front = [(1, 1), (1, -1)]  # upper-right, upper-left
        self.back = [(-1, 1), (-1, -1)]  # bottom-right, bottom-left
        if color == 'b':
            self.__swap_back_and_front()
        if is_king:
            self.__swap_back_and_front()

        self.read_to_jump = 0  # if there's any opponent's tokes in the attacking area, mark this as 1
        self.available_moves = [i for i in self.front]
        if pos[1] == 0:
            self.available_moves = [self.front[0]]
        elif pos[1] == 7:
            self.available_moves = [self.front[1]]

        self.arc_set = []  # Tokens that is blocked by this token
        self.jump_path = []

    def __swap_back_and_front(self):
        """
        Simply swap the back and the front of the token.
        """
        temp = self.front
        self.front = self.back
        self.back = temp

    def get_landing(self, move):
        """
        Get the landing position of the token given a move.
        :param move: A move. e.g., (1, 1) (1,-1)...
        :return: Landing position.
        """
        return self.position[0] + move[0], self.position[1] + move[1]

    def reset(self):
        self.arc_set = []
        self.read_to_jump = 0
        self.jump_path = []
        self.available_moves = [i for i in self.front]
        if self.position[1] == 0:
            self.available_moves = [self.front[0]]
        elif self.position[1] == 7:
            self.available_moves = [self.front[1]]

    def to_checker_position(self):
        """
        Return the position as human readable format.
        :return: string (checker format e.g., "a1", 'e6", etc.)
        """
        return f"{chr(ord('a') + self.position[1])}{self.position[0] + 1}"

    def __str__(self):
        return f"Position: {self.position}\nColor: {self.color}\nKing: {self.is_king}\n" \
               f"Available Moves: {self.available_moves}"


class ObjectEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Token):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)


def display_board(board, filename):
    b = [['.' for i in range(8)] for j in range(8)]
    with open(filename, 'w') as f:
        for key, value in board.items():
            f.writelines(f"{{{key}: {value.__dict__}}}\n")
            b[key[0]][key[1]] = value.color if not value.is_king else value.color.upper()
        b.reverse()
        display = ""
        for row in b:
            display += "".join(row) + '\n'
        f.writelines(display)
    print(display)


def test(game):
    display_board(game.board, 'board.txt')
    test_token = game.board[(1, 3)]
    # game.player_w.single_move(test_token, test_token.available_moves[1])
    game.player_b.jump(test_token, test_token.jump_path[0])
    display_board(game.board, 'board2.txt')


if __name__ == '__main__':
    game = Game("input4.txt")

    with open('debug.txt', 'w') as f:
        json.dump(list(map(ObjectEncoder().encode, game.player_w.tokens)), f, indent=4)
        json.dump(list(map(ObjectEncoder().encode, game.player_b.tokens)), f, indent=4)

    test(game)

    with open('debug2.txt', 'w') as f:
        json.dump(list(map(ObjectEncoder().encode, game.player_w.tokens)), f, indent=4)
        json.dump(list(map(ObjectEncoder().encode, game.player_b.tokens)), f, indent=4)
