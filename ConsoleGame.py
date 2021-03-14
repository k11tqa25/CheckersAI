import Agent2 as Agent
import time
from colorama import init   # To make the command line colorful
from colorama import Fore, Back, Style

init(autoreset=True)

GAME_FILE = "Game.txt"
RESULT_FILE = "output.txt"
AGENT_COLOR = "WHITE"
TOTAL_TIME = 100.0


def decode_checker_position(pos):
    # pos should be a string like 'a2', 'b5'...
    return int(pos[1]) - 1, int(ord(pos[0])) - int(ord('a'))


def read_agent_result():
    with open(RESULT_FILE, 'r') as f:
        path = []
        count = 0
        for i, line in enumerate(f.readlines()):
            count += 1
            print(line)
            info = line.split(' ')
            if info[0] == 'J':
                if i == 0:
                    curr_loc = decode_checker_position(info[1])
                path.append(decode_checker_position(info[2]))
            else:
                curr_loc = decode_checker_position(info[1])
                move_loc = decode_checker_position(info[2])
                move = Agent.tuple_operation(move_loc, curr_loc, 's')
        if count != 0:
            token = com.board[curr_loc]
            if len(path) != 0:
                com.player.jump(token, path)
            else:
                com.player.single_move(token, move)
        else:
            return False
    return True


def read_player_input(input):
    input = input.strip()
    commands = input.split(' ')
    if len(commands) < 2:
        print(Back.RED + "Invalid Input!")
        return False
    else:
        commands = list(map(str.lower, commands))
        start = decode_checker_position(commands[0])
        first = decode_checker_position(commands[1])
        valid = False
        for t in com.player.opponent.tokens:
            if t.position == start:
                valid = True
        if not valid:
            print(Back.RED + f"Invalid Piece at {commands[0]}")
            return False
        if (first[0] + first[1]) % 2 != 0:
            print(Back.RED + f"You can't go to {commands[1]}")
        need_to_jump = len(com.player.opponent.jump_available_tokens) > 0
        if len(commands) > 2 or abs(start[0] - first[0]) > 1 or abs(start[1] - first[1]) > 1:
            # Jump
            path = []
            for i in range(1, len(commands)):
                path.append(decode_checker_position(commands[i]))
            token = com.board[start]
            com.player.opponent.jump(token, path)
        else:
            if need_to_jump:
                print(Back.RED + f"Invalid Move. You need to make a jump.")
                return False
            token = com.board[start]
            move = Agent.tuple_operation(first, start, 's')
            com.player.opponent.single_move(token, move)

    return True


def display_board():
    b = [[' ' for i in range(8)] for j in range(8)]
    for key, value in com.board.items():
        b[key[0]][key[1]] = value.color if not value.is_king else value.color.upper()
    b.reverse()
    row_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    col_names = [1, 2, 3, 4, 5, 6, 7, 8]
    col_names.reverse()
    for row, name in zip(b, col_names):
        print(Fore.YELLOW + f"{name} ", end="")
        for i, item in enumerate(row):
            if item != " ":
                if item == 'b' or item == 'B':
                    print(Fore.BLUE + f" {item} ", end="")
                else:
                    print(Fore.GREEN + f" {item} ", end="")
            else:
                print(f" {item} ", end="")
            if i != len(row) - 1:
                print("|", end="")
        # print(f"{name}  "+" | ".join(row))
        print(f"\n  "+"-"*31)
    print(Fore.YELLOW + "   "+"   ".join(row_names))


def check_wining(time, has_move):
    if len(com.player.tokens) == 0 or time < 0 or not has_move:
        print(Back.YELLOW + Fore.RED + "YOU WON!!!")
        return True
    elif len(com.player.opponent.tokens) == 0:
        print("YOU LOST...")
        return True

    return False


def initialize():
    global AGENT_COLOR, TOTAL_TIME
    with open(GAME_FILE, 'r') as f:
        f.readline()
        AGENT_COLOR = f.readline().strip()
        TOTAL_TIME = float(f.readline().strip())


def run():
    initialize()
    global TOTAL_TIME

    Name = input("Welcome! Type in your name and start:")
    print("Type q or Q to quit the game.")
    cmd = ""
    stop = False
    states = ["agent", "player", "check"]
    if AGENT_COLOR == "WHITE":
        state = states[0]
    else:
        state = states[1]
    agent_turn = True
    has_move = True

    while not stop:
        if state == states[0]:
            display_board()
            if AGENT_COLOR == "BLACK":
                print(Fore.BLUE + f"(Agent) is making a move...")
            else:
                print(Fore.GREEN + f"(Agent) is making a move...")
            agent_time_spent = Agent.run(GAME_FILE, RESULT_FILE)
            TOTAL_TIME = TOTAL_TIME - agent_time_spent
            if TOTAL_TIME > 0:
                has_move = read_agent_result()
                agent_turn = False
            state = states[2]
        elif state == states[1]:
            display_board()
            if AGENT_COLOR == "BLACK":
                print(Fore.GREEN + f"({Name}) makes a move:")
            else:
                print(Fore.BLUE + f"({Name}) makes a move:")
            cmd = input()
            if cmd == 'q' or cmd == "Q":
                stop = True
            else:
                if read_player_input(cmd):
                    Agent.to_agent_board(GAME_FILE, com.board, AGENT_COLOR, TOTAL_TIME)
                    agent_turn = True
                    state = states[2]
                else:
                    state = states[1]

        elif state == states[2]:
            if check_wining(TOTAL_TIME, has_move):
                display_board()
                stop = True
            else:
                state = states[0] if agent_turn else states[1]

# if __name__ == '__main__':

com = Agent.Game(GAME_FILE)
#     run()