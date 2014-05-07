from __future__ import division

import numpy as np
from random import random
import copy

import json
import itertools

class GameOver(BaseException): pass

### from http://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): 
        char = self.impl()
        if char == '\x03':
            raise KeyboardInterrupt
        elif char == '\x04':
            raise EOFError
        return char

class _GetchUnix:
    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


def random_from_distribution(distribution):
    total = sum(distribution)
    seed = random()*total
    for index, n in enumerate(distribution):
        if seed<n:
            return index
        else:
            seed-=n
    return index

ALLOWED_DICT = {}
for n in range(5):
    for combi in itertools.combinations(('i','j','k','l'),n):
        ALLOWED_DICT[combi] = 0


class Tree(object):
    N_SIMU_MAX = 100
    VERBOSE = 0
#    dir = ["i", "j", "k", "l"]
    
    def __init__(self, parent, current_game):
        self.childs = {}
        self.parent = parent
        
        self.n_played_ = 0
        self.initial_score = current_game.evaluate()
        self.total_score_ = 0
        self.possibilities_ = [] #i,j,k,l
        
        self.n_blocked_ = copy.copy(ALLOWED_DICT)

        
    def simulate(self, current_game, depth):
        if self.VERBOSE > 1:
            print current_game
        if depth == 0:
            self.total_score_ += current_game.evaluate()
            self.n_played_ += 1
            self.parent.update_score()
        else:
            try:
                dir = self.pick_dir(current_game)
            except GameOver:
                self.total_score_ += 0
                self.n_played_ += 1
                self.parent.update_score()
            else:
                current_game.move(dir)
                current_game.add_number()
                self.childs[dir].simulate(current_game, depth-1)
    
            
    @property
    def mean_score(self):
        if self.n_played_ == 0:
            return self.initial_score
        return self.total_score_/self.n_played_

    def pick_dir(self, current_game):
        blocked = []
        distribution = []
        moves = ['i','j','k','l']
        self.possibilities_ = []
        for dir in moves:
            game = current_game.copy()
            if game.move(dir):
                game.add_number()
                if not dir in self.childs:
                    self.childs[dir] = Tree(self, game)
                distribution.append(self.childs[dir].mean_score+0.1)
                self.possibilities_.append(dir)
            else:
                blocked.append(dir)
                distribution.append(0)
        self.n_blocked_[tuple(blocked)] += 1
        dir_index = random_from_distribution(distribution)
        if distribution == [0,0,0,0]:
            raise GameOver("can't move")
        #print distribution
        return moves[dir_index]
    
    def update_score(self):
        self.n_played_ += 1
        
        scores_dir = [(self.childs[dir].mean_score, dir) for dir in self.possibilities_] 
        scores_dir = sorted(scores_dir, reverse=True)
        
        played = 0
        combi = []
        to_play = self.n_played_
        total_score = 0
        for score, dir in scores_dir:
            combi.append(dir)
            combi_tuple = tuple(np.sort(combi))
            n_times_blocked = self.n_blocked_[combi_tuple]
            n_play_this = to_play - n_times_blocked
            total_score += score*n_play_this
            to_play = n_times_blocked
        self.total_score_ = total_score
            #import pdb
            #pdb.set_trace()
        if self.parent is not None:
            self.parent.update_score()
      
    def optimize(self, current_game, depth=5):
        for i in range(Tree.N_SIMU_MAX):
            if self.VERBOSE >= 1:
                print """============ NEW SIMU =========="""
            game = current_game.copy()
            self.simulate(game, depth=depth)
    
        dirs = []
        scores = []
        for dir, child in self.childs.iteritems():
            score = child.mean_score 
            if self.VERBOSE > 0:
                print dir, ": ", child.n_played_," times played, mean_score: ", score
            dirs.append(dir)
            scores.append(score)
        best_index = np.argmax(scores)
        return dirs[best_index]
            
class Dmqh(object):
    N_BRANCHES_MONTE_CARLO = 1
    MAX_LOSS_ALLOWED = 16 ###4 would like to try -128
    def __init__(self, n):
        self.n = n
        self.dat = np.zeros((n,n), dtype=int) 
        self.add_number()
        self.add_number()
    
    def empty_places(self):
        """returns the list of free slots"""
        return np.where(self.dat==0)
    
    def add_number(self):
        n_slots = len(self.empty_places()[0])
        if n_slots==0:
            raise GameOver("could not add number")
        position = np.random.randint(n_slots)
        val = 2**(1 + np.random.randint(11)//10)
        where = self.empty_places()
        self.dat[where[0][position],where[1][position]] = val
        return self
        
    def crunch(self, col):
        last_val = 0
        pos = 0
        for i, val in enumerate(col):
            col[i] = 0
            if val==0:
                continue
            else:
                if val==last_val:
                    pos-=1
                    col[pos] = 2*val
                    last_val = 0
                    pos+=1
                else:
                    last_val = val
                    col[pos] = last_val
                    pos+=1
        return col
                    
    def play(self, auto=False):
        while(True):
            print ""
            print "current position:"
            print self
            suggestion = self.optimize()
            print "press one of the keys i,j,k or l in the console to move... my advise:" \
            , suggestion
            if auto:
                c = suggestion
                self.move(c)
            else:
                c = getch()
                print c + " pressed"
                while not self.move(c):
                    print "move not allowed!"
                    c = getch()
                    print c + " pressed"                
            self.add_number()
        return self
    
    
    def move(self, dir):
        old_dat = np.copy(self.dat)
        if dir=="j":
            for i,col in enumerate(self.dat):
                self.dat[i,:] = self.crunch(col)
            return not np.array_equal(self.dat, old_dat)
        if dir=='l':
            for i,col in enumerate(self.dat):
                self.dat[i,:] = self.crunch(col[-1::-1])[-1::-1]
            return not np.array_equal(self.dat, old_dat)
        if dir=='k':
            for i,col in enumerate(self.dat.T):
                self.dat[:,i] = self.crunch(col[-1::-1])[-1::-1]
            return not np.array_equal(self.dat, old_dat)
        if dir=='i':
            for i,col in enumerate(self.dat.T):
                self.dat[:,i] = self.crunch(col)
            return not np.array_equal(self.dat, old_dat)
        return False
        
    def __repr__(self):
        ret = ""
        for col in self.dat:
            for j in col:
                ret = ret + str(j) + '\t'
            ret+='\n'
        return ret
    
    def snake_coords(self):
        revert_direction = True
        for x,line in enumerate(self.dat):
            revert_direction = not revert_direction
            if revert_direction:
                line = line[-1::-1]
            for y, val in enumerate(line):
                if revert_direction:
                    y = self.n - y - 1
                yield val, x, y

    def snake(self):
        revert_direction = True
        for line in self.dat:
            revert_direction = not revert_direction
            if revert_direction:
                line = line[-1::-1]
            for val in line:
                yield val
    
    def evaluate(self):
        """
        Evaluates the value of a position:
          - The slots matching the decreasing S are added to the total
          - The other ones are subtracted
        """
        
        count_plus = True
        total = 0
        last = 1000000
        for val in self.snake():
            if count_plus:
                if val>last:
                    count_plus = False
                else:
                    total+=val
                    last = val
            if not count_plus:
                pass
                #total-=val**2/10
        return total
    
    def copy(self):
        return copy.deepcopy(self)
    
    def move_list(self):
        """
        iterator over the possible moves at that stage.
        yields the tuple (direction, resulting_game)
        """
        for dir in ["i","j","k","l"]:
            game = self.copy()
            if game.move(dir):
                yield dir, game
    
    def fill_list(self):
        """
        iterator over the possible random fills at that stage.
        yields the resulting_game. 
        """    
        

        for val, x, y in self.snake_coords():
            for new_val in [2,4]:
                if val==0:
                    game = self.copy()
                    game.dat[x, y] = new_val
                    yield game


    """
    def possible_moves(self):
        possible = {}
        for dir in ["i", "j", "k", "l"]:
            game = self.copy()
            if game.move(dir):
                possible.append(dir)
        return possible
    """
    
    
    def optimize(self):
        tree = Tree(None, self)
        return tree.optimize(self)
        
    def optimize_old(self, depth, check_all=False):
        if depth==0:
            return ("", self.evaluate())
        mean_scores = []
        directions = []
        previous_score = self.evaluate()
        for move, res in self.move_list():
            mean_score = 0
            n = 0
            if not check_all:
                if res.evaluate()<previous_score - self.MAX_LOSS_ALLOWED:
                    continue
            for pos in res.fill_list():
                (dir, score) = pos.optimize(depth - 1, check_all)
                n+=1
                mean_score+=score
            mean_score/=n
            mean_scores.append(mean_score)
            directions.append(move)
        if len(mean_scores)==0: ### GAME OVER
            if check_all:
                return ("", -1000000)
            else:
                return self.optimize(depth, check_all=True)
            
        best = np.argmax(mean_scores)
        return (directions[best], mean_scores[best])
    
    def optimize_naive(self):
        best_score = -1
        best_dir = ""
        for dir, game in self.move_list():
            score = game.evaluate()
            if score>best_score:
                best_dir = dir
                best_score = score
        return best_dir


def best_move(json_str): 
    game_state = json.loads(text)
    game = Dmqh(4)    
    for x,val in enumerate(game_state['grid']['cells']):
        for y,val in enumerate(val):
            if val==None:
                val = 0
            else:
                val =  val['value']
            game.dat[x,y] = val
    game.dat = game.dat.T
    return d.optimize_naive()

if __name__=="__main__":
    GAME = Dmqh(4)
    GAME.play(auto=True)