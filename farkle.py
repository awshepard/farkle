import itertools
import argparse
import logging
import random

parser = argparse.ArgumentParser()
parser.add_argument(
    '--debug', action='store_true', default=False, help='debug mode')
parser.add_argument(
    '--games', type=int, default=1, help='how many games to play')
parser.add_argument('--turnStrategy', type=str, default='simple',
                    help='what strategy to use when turning over cards')
parser.add_argument('--collapseStrategy', type=str, default='simple',
                    help='what strategy to use when collapsing the board')

global args
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)


def main():
    # 1 = 100
    # 5 = 50
    # 123456 = 1000
    # 3 of anything = 3 x X
    # 3 1's = 1000

    # die = 3 bits -> pack 6 into 1 integer
    # lock 1 per turn
    # keep rolling as long as you're scoring
    locked = []
    board = []
    # do roll =
    for i in range(0, 6):
        board.append(random.randint(1, 6))

    print board
    # check loss condition on board
    # choose lock
    fr = 0
    to = 1
    for i in board[fr:to]:
        locked.append(i)
    board = board[0:fr] + board[to:]
    print locked
    print board

    scores = {}
    count = 0
    for i in itertools.product([1, 2, 3, 4, 5, 6], repeat=6):
        count += 1
        scores[str(i)] = score(i)
    # print scores

    score_dist = {}
    max_score = 0
    max_board = None
    reset_count = 0
    mod = args.games / 10
    for i in range(args.games):
        if not args.debug and i % mod == 0:
            logging.info("Game %d" % i)
        logging.debug("++++GAME %d++++" % i)
        m, board, resets = turn()
        if resets > 0:
            reset_count += 1
        if m not in score_dist:
            score_dist[m] = []
        score_dist[m].append(board)
        if m > max_score:
            max_score = m
            max_board = board
        logging.debug("Score = %d" % m)
    print "Max board = %s, score = %d" % (str(max_board), max_score)
    print "Had %d turns that rest dice" % reset_count
    for i in sorted(score_dist):
        print "Score %d = %d" % (i, len(score_dist[i]))


def turn():
    turn_score = 0
    roll_score = -1
    num_dice = 6
    pinned_dice = []
    old_pinned_dice = []
    reset_count = 0
    while roll_score != 0 and num_dice > 0 and turn_score < 10000:
        logging.debug("board: %s. current turn score: %d. now rolling %d dice..." % (
            str(pinned_dice), turn_score, num_dice))
        dice_roll = roll(num_dice)
        logging.debug("got roll: %s" % str(dice_roll))
        roll_score = score(dice_roll)
        logging.debug("has score: %d" % roll_score)
        if roll_score > 0:
            to_pin = choose(dice_roll)
            logging.debug("pinning: %s" % str(to_pin))
            pinned_dice.append(to_pin)
            num_dice -= len(to_pin)
            turn_score += score(to_pin)
            if num_dice == 0:
                # keep rolling, or choose to stop
                # TODO: implement choice to stop?
                logging.debug("resetting dice!")
                reset_count += 1
                num_dice = 6
                old_pinned_dice.append(pinned_dice)
                pinned_dice = []
        else:
            if len(pinned_dice) > 0:
                old_pinned_dice.append(pinned_dice)
            logging.debug("0 score! Ending turn.")
            return turn_score, old_pinned_dice, reset_count
    logging.debug("reset %d times" % reset_count)
    if len(pinned_dice) > 0:
        old_pinned_dice.append(pinned_dice)
    if turn_score >= 350:
        logging.debug("Final board: %s" % str(pinned_dice))
        return turn_score, old_pinned_dice, reset_count
    else:
        logging.debug("turn score < 350! Ending turn.")
        return turn_score, old_pinned_dice, reset_count


def choose(i):
    # choice:
    # pin all 3's, 1's, and straights
    # 5 only if we have to
    d = i
    if isinstance(i, list):
        d = {x: i.count(x) for x in i}

    to_pin = []
    for key, val in d.iteritems():
        while val >= 3:
            to_pin += [key, key, key]
            val -= 3
        if key == 1:
            to_pin += [key for z in range(val)]
        if key == 5 and len(to_pin) == 0:
            to_pin += [key for z in range(val)]

    return to_pin


def roll(num_dice=6):
    dice_roll = [random.choice([1, 2, 3, 4, 5, 6]) for i in range(num_dice)]
    # d = {x: dice_roll.count(x) for x in dice_roll}
    return dice_roll
    # itertools.product([1, 2, 3, 4, 5, 6], repeat=num_dice)


def score(i):
    # itertools.product guarantees i will be sorted
    score = 0
    d = {}
    if isinstance(i, list):
        d = {x: i.count(x) for x in i}
        # i = d
    else:
        d = i
    # if a straight, return 1000
    if len(d) == 6:
        return 1000
    # print d
    for key, val in d.iteritems():
        # if we have 3 or more items, add 1000 for 1
        # or 3 x X for others
        while val >= 3:
            if key == 1:
                score += 1000
            else:
                score += 100 * key
            val -= 3
        if key == 1:
            score += 100 * val
        elif key == 5:
            score += 50 * val
    return score

if __name__ == '__main__':
    main()
