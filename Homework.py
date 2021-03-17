import json
from json import JSONEncoder
import copy

MAX_DEPTH = 6
time_spent = 0


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


def apply_alg(player, is_max=True, depth=1, a=float('-inf'), b=float('inf')):
    if depth == MAX_DEPTH + 1:
        h = player.get_heuristic(depth) if depth % 2 == 1 else player.opponent.get_heuristic(depth)
        return h, {depth: (player.color, None, None, None)}
    v = float('-inf') if is_max else float('inf')
    best_move = {}
    best_next_moves = {}
    if len(player.jump_available_tokens) != 0:
        for jt in player.jump_available_tokens:
            for path in jt.jump_path:
                p = copy.deepcopy(player)
                tkn = find_token(jt, p.tokens)
                p.jump(tkn, path)
                v_next, next_moves = apply_alg(p.opponent, not is_max, depth + 1, a, b)
                del p
                if is_max:
                    # v = max(v, v_next)
                    if v < v_next:
                        v = v_next
                        best_next_moves = next_moves
                    if v > b:
                        best_move[depth] = (player.color, jt.readable_position, 'J', path)
                        best_move[depth + 1] = best_next_moves
                        return v, best_move
                    if a < v:
                        a = v
                        best_move[depth] = (player.color, jt.readable_position, 'J', path)
                else:
                    # v = min(v, v_next)
                    if v > v_next:
                        v = v_next
                        best_next_moves = next_moves
                    if v < a:
                        best_move[depth] = (player.color, jt.readable_position, 'J', path)
                        best_move[depth + 1] = best_next_moves
                        return v, best_move
                    if b > v:
                        b = v
                        best_move[depth] = (player.color, jt.readable_position, 'J', path)
    elif len(player.move_available_tokens) != 0:
        for mt in player.move_available_tokens:
            for move in mt.available_moves:
                p = copy.deepcopy(player)
                tkn = find_token(mt, p.tokens)
                p.single_move(tkn, move)
                v_next, next_moves = apply_alg(p.opponent, not is_max, depth + 1, a, b)
                del p
                if is_max:
                    if v < v_next:
                        v = v_next
                        best_next_moves = next_moves
                    if v >= b:
                        best_move[depth] = (player.color, mt.readable_position, 'M', move)
                        best_move[depth + 1] = best_next_moves
                        return v, best_move
                    if a < v:
                        a = v
                        best_move[depth] = (player.color, mt.readable_position, 'M', move)
                else:
                    if v > v_next:
                        v = v_next
                        best_next_moves = next_moves
                    if v <= a:
                        best_move[depth] = (player.color, mt.readable_position, 'M', move)
                        best_move[depth + 1] = best_next_moves
                        return v, best_move
                    if b > v:
                        b = v
                        best_move[depth] = (player.color, mt.readable_position, 'M', move)
    else:
        h = player.get_heuristic(depth) if depth % 2 == 1 else player.opponent.get_heuristic(depth)
        return h, {depth: (player.color, None, None, None)}

    best_move[depth + 1] = best_next_moves
    return v, best_move


def find_token(token, token_set):
    for t in token_set:
        if token.readable_position == t.readable_position:
            return t
    return None


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
        self.player = self.player_w if self.my_color == 'w' else self.player_b
        global MAX_DEPTH
        if len(self.board) <= 6:
            MAX_DEPTH = 7
        # if len(self.board) <= 15:
        #     MAX_DEPTH = 7
        if float(self.time_left) < 10.0:
            MAX_DEPTH = 3

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
            self.my_color = "w" if f.readline().strip() == "WHITE" else 'b'
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

    def play(self):
        """
        Apply the algorithm to make a move.
        """
        v, moves = apply_alg(self.player)

        return v, moves

    def output_result(self, moves, filename):
        with open(filename, 'w') as f:
            if moves is None:
                return
            if moves[1][1] is None:
                return
            m = moves[1]
            if m[2] == 'J':
                path = m[3]
                for i in range(len(path)):
                    if i == 0:
                        f.write(f"J {m[1]} {chr(ord('a') + path[i][1])}{path[i][0] + 1}\n")
                    else:
                        f.write(f"J {chr(ord('a') + path[i-1][1])}{path[i-1][0] + 1} {chr(ord('a') + path[i][1])}{path[i][0] + 1}\n")
            else:
                move = m[3]
                row = chr(ord(m[1][0]) + move[1])
                col = int(m[1][1]) + move[0]
                f.write(f"E {m[1]} {row}{col}\n")


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
        self.move_available_tokens = set()
        self.jump_available_tokens = set()
        for token in self.tokens:
            self.arc_check(token)
        # self.get_available_tokens()

    def check_all_jump_tokens(self):
        # Check all the tokens in the board that is read for jumps.
        for token in self.board.values():
            if token.read_to_jump:
                if token.color == self.color:
                    self.arc_check(token)
                else:
                    self.opponent.arc_check(token)

    def arc_check(self, token):
        """
        For each token, check the available moves and its affecting tokens (arcs), so that when the state
        of this token changed (captured, move, or jump), it can notify its affecting tokens to update their
        availabilities.
        """
        token.reset()

        for corner in map(token.get_landing, token.front + token.back):
            if corner in self.board:
                token.arc_set.add(corner)
        # check for available moves and jump
        jump_path = self.__find_all_jump_path(token.position, token.position, token.front, token.color)
        token.jump_path.extend(jump_path)
        if len(jump_path) != 0:
            token.read_to_jump = 1
            self.jump_available_tokens.add(token)
        else:
            if token in self.jump_available_tokens:
                self.jump_available_tokens.remove(token)
        for move in [m for m in token.available_moves]:
            landing = token.get_landing(move)
            if landing in token.arc_set:
                token.available_moves.remove(move)
        if len(token.available_moves) == 0:
            if token in self.move_available_tokens:
                self.move_available_tokens.remove(token)
        else:
            self.move_available_tokens.add(token)

    def __find_all_jump_path(self, token_pos, org_pos, front, color, pre_path=None, taken_pieces=None):
        if taken_pieces is None:
            taken_pieces = set()
        if pre_path is None:
            pre_path = []
        result = []
        for next_move in front:
            next_front = tuple_operation(token_pos, next_move)
            if next_front in self.board:
                piece = self.board[next_front]
                if piece.color != color and piece not in taken_pieces:
                    next_landing = tuple_operation(next_front, next_move)
                    taken_pieces.add(self.board[next_front])
                    if (next_landing not in self.board or next_landing == org_pos)\
                            and 0 <= next_landing[0] <= 7 \
                            and 0 <= next_landing[1] <= 7:
                        ret = self.__find_all_jump_path(next_landing, org_pos, front, color, pre_path + [next_landing]
                                                        , copy.copy(taken_pieces))
                        if len(ret) > 0:
                            result.extend(ret)
                    taken_pieces.remove(self.board[next_front])

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
        if token in self.tokens:
            self.tokens.remove(token)
        if token in self.move_available_tokens:
            self.move_available_tokens.remove(token)
        if token in self.jump_available_tokens:
            self.jump_available_tokens.remove(token)
        del self.board[token.position]

        # 2. Notify the affected tokens
        for arc in token.arc_set:
            notified = self.board[arc]
            if notified.color == self.color:
                self.arc_check(notified)
            else:
                self.opponent.arc_check(notified)

    def place_a_token(self, token, landing):
        """
        Place a token.
        :param token: The token to place
        :param landing: The landing position of the token.
        """
        # Place a token in its place and do the arc check
        token.position = landing
        if token.color == "w":
            if token.position[0] == 7 and not token.is_king:
                token.become_king()
        else:
            if token.position[0] == 0 and not token.is_king:
                token.become_king()
        self.tokens.add(token)
        self.board[landing] = token
        self.arc_check(token)

        # notify all other tokens in the arc
        for arc in token.arc_set:
            notified = self.board[arc]
            if notified.color == self.color:
                self.arc_check(notified)
            else:
                self.opponent.arc_check(notified)

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
            self.opponent.remove_a_token(tkn)

        landing = path[-1]
        self.place_a_token(token, landing)
        self.check_all_jump_tokens()

    def get_heuristic(self, depth):
        def heuristic(player):
            piece_count = len(player.tokens)
            jump_reward = 0
            protection = 0
            position_reward = 0
            king = 0
            number_of_moves = 0
            if len(player.jump_available_tokens) != 0:
                for t in player.jump_available_tokens:
                    number_of_moves += len(t.jump_path) * 2
            else:
                for t in player.move_available_tokens:
                    number_of_moves += len(t.available_moves)
            if number_of_moves == 0:
                # No moves means losing
                number_of_moves = -1000
            for t in player.tokens:
                protection -= 1
                for arc in t.arc_set:
                    if player.board[arc].color == t.color:
                        protection += 0.5
                if t.read_to_jump:
                    jump_reward += max(map(len, t.jump_path)) * 3
                if t.is_king:
                    king += 10
                else:
                    # for not king
                    if t.front[0][0] > 0:
                        # if it's white
                        position_reward += t.position[0] + 1
                    else:
                        # if it's black
                        position_reward += -t.position[0] + 8

            return piece_count + king + jump_reward + position_reward + number_of_moves + protection + depth
        bonus = 0
        if len(self.opponent.tokens) == 0:
            bonus = 1000
        return heuristic(self) - heuristic(self.opponent) * 1.5 + bonus


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

        self.read_to_jump = 0  # if there's any opponent's tokes in the attacking area, mark this as 1
        if not is_king:
            self.available_moves = [i for i in self.front]
            if pos[1] == 0:
                self.available_moves = [self.front[0]]
            elif pos[1] == 7:
                self.available_moves = [self.front[1]]
        else:
            self.become_king()

        self.arc_set = set()  # Tokens that is blocked by this token
        self.jump_path = []

    def __swap_back_and_front(self):
        """
        Simply swap the back and the front of the token.
        """
        temp = self.front
        self.front = self.back
        self.back = temp

    def become_king(self):
        self.is_king = True
        self.front = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        self.back = []
        self.available_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        pos = self.position
        if pos[1] == 0:
            self.available_moves = list(filter(lambda x: x[1] > 0, self.available_moves))
        elif pos[1] == 7:
            self.available_moves = list(filter(lambda x: x[1] < 0, self.available_moves))

        if pos[0] == 0:
            self.available_moves = list(filter(lambda x: x[0] > 0, self.available_moves))
        elif pos[0] == 7:
            self.available_moves = list(filter(lambda x: x[0] < 0, self.available_moves))

    def get_landing(self, move):
        """
        Get the landing position of the token given a move.
        :param move: A move. e.g., (1, 1) (1,-1)...
        :return: Landing position.
        """
        return self.position[0] + move[0], self.position[1] + move[1]

    def reset(self):
        self.arc_set = set()
        self.read_to_jump = 0
        self.jump_path = []
        if not self.is_king:
            self.available_moves = [i for i in self.front]
            if self.position[1] == 0:
                self.available_moves = [self.front[0]]
            elif self.position[1] == 7:
                self.available_moves = [self.front[1]]
        else:
            self.become_king()

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


def run(input_filename, output_filename):
    game = Game(input_filename)
    v, moves = game.play()
    game.output_result(moves, output_filename)


run("input.txt", "output.txt")