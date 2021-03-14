# Agent 1 will always go first
import Agent4 as agent1
import Agent2 as agent2
from colorama import init   # To make the command line colorful
from colorama import Fore, Back, Style
import time

init(autoreset=True)

GAME_FILE = "Game.txt"
RESULT1_FILE = "output1.txt"
RESULT2_FILE = "output2.txt"
AGENT1_COLOR = "WHITE"
AGENT2_COLOR = "BLACK"
TOTAL_TIME1 = 100.0
TOTAL_TIME2 = 100.0
AGENT1_NAME = "protected agent"
AGENT2_NAME = "aggressive agent"


def initialize():
    global AGENT1_COLOR, TOTAL_TIME1, AGENT2_COLOR, TOTAL_TIME2
    with open(GAME_FILE, 'r') as f:
        f.readline()
        f.readline()
        TOTAL_TIME1 = TOTAL_TIME2 = float(f.readline().strip())


def decode_checker_position(pos):
    # pos should be a string like 'a2', 'b5'...
    return int(pos[1]) - 1, int(ord(pos[0])) - int(ord('a'))


def read_agent_result(agent_number):
    file = RESULT1_FILE if agent_number == 1 else RESULT2_FILE
    agent = agent1 if agent_number == 1 else agent2
    player = game.player if agent_number == 1 else game.player.opponent
    with open(file, 'r') as f:
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
                move = agent.tuple_operation(move_loc, curr_loc, 's')
        if count != 0:
            token = game.board[curr_loc]
            if len(path) != 0:
                player.jump(token, path)
            else:
                player.single_move(token, move)
        else:
            return False
    return True


def to_agent_board(filename, board, color='WHITE', t=100.00):
    with open(filename, 'w') as f:
        f.write("SINGLE\n")
        f.write(f"{color}\n")
        f.write(f"{t}\n")
        b = [['.' for i in range(8)] for j in range(8)]
        for key, value in board.items():
            b[key[0]][key[1]] = value.color if not value.is_king else value.color.upper()
        b.reverse()
        for row in b:
            f.write("".join(row) + '\n')


def display_board():
    b = [[' ' for i in range(8)] for j in range(8)]
    for key, value in game.board.items():
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
        print(f"\n  "+"-"*31)
    print(Fore.YELLOW + "   "+"   ".join(row_names))


def check_wining(has_move1, has_move2):
    if len(game.player.tokens) == 0 or TOTAL_TIME1 < 0 or not has_move1:
        print(Back.YELLOW + Fore.RED + f"{AGENT2_NAME} WON!!!")
        return True
    elif len(game.player.opponent.tokens) == 0 or TOTAL_TIME2 < 0 or not has_move2:
        print(Back.YELLOW + Fore.RED + f"{AGENT1_NAME} WON!!!")
        return True
    return False


def run():
    initialize()
    global TOTAL_TIME1, TOTAL_TIME2
    states = ["com1", "com2", "check"]
    if AGENT1_COLOR == "WHITE":
        state = states[0]
    else:
        state = states[1]
    agent1_turn = True
    has_move1 = True
    has_move2 = True
    stop = False
    step = 0
    while not stop:
        if state == states[0]:
            display_board()
            print(Fore.GREEN + f"({AGENT1_NAME}) is making a move...{TOTAL_TIME1}")
            agent_time_spent = agent1.run(GAME_FILE, RESULT1_FILE)
            TOTAL_TIME1 = TOTAL_TIME1 - agent_time_spent
            if TOTAL_TIME1 > 0:
                has_move1 = read_agent_result(1)
                agent1_turn = False
            to_agent_board(GAME_FILE, game.board, AGENT2_COLOR, TOTAL_TIME2)
            state = states[2]
        elif state == states[1]:
            display_board()
            print(Fore.BLUE + f"({AGENT2_NAME}) is making a move...{TOTAL_TIME2}")
            agent_time_spent = agent2.run(GAME_FILE, RESULT2_FILE)
            TOTAL_TIME2 = TOTAL_TIME2 - agent_time_spent
            if TOTAL_TIME2 > 0:
                has_move2 = read_agent_result(2)
                agent1_turn = True
            to_agent_board(GAME_FILE, game.board, AGENT1_COLOR, TOTAL_TIME1)
            state = states[2]

        elif state == states[2]:
            time.sleep(1)
            step += 1
            print(f"%% STEP {int(step/1)}")
            if check_wining(has_move1, has_move2):
                display_board()
                stop = True
            else:
                state = states[0] if agent1_turn else states[1]


if __name__ == "__main__":
    game = agent1.Game(GAME_FILE)
    run()
