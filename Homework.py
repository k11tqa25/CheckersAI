
class Game:

    def __init__(self):
        self.board = [[]]
        self.player_w = Player()
        self.player_b = Player()

    def read_board(self, filename):
        pass


class Player:

    def __init__(self):
        self.tokens = []

    def assign_tokens(self):
        pass

    def get_available_tokens(self):
        jump_available_tokens = []
        move_available_tokens = []

class Token:

    def __init__(self, id, color, pos, is_king=False):
        self.id = id
        self.color = color      # "b" or "w"
        self.position = pos     # [0, 0] ~ [7, 7] where x = rows, y = cols
        self.is_king = is_king
        self.front = [[1, 1], [-1, 1]] if is_king else [[1, -1], [-1, -1]]
        self.back = [[1, -1], [-1, -1]] if is_king else [[1, 1], [-1, 1]]
        self.jump = 0       # if it's possible to jump, jump = 1

    def to_checker_position(self):
        """
        Return the position as human readable format.
        :return: string (checker format e.g., "a1", 'e6", etc.)
        """
        return f"{chr(ord('a')+self.position[1])}{self.position[0] + 1}"





if __name__ == '__main__':
    t1 = Token(0, [0, 0])
    print(t1.to_checker_position())