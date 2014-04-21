from __future__ import division

import numpy as np
import copy

import json

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

class Tree(object):
    N_EXTENDS = 0
    MAX_EXTENDS = 200
    LOSE_PENALTY = -100000000
#    dir = ["i", "j", "k", "l"]
    
    def __init__(self, game, parent, dir, is_number_added=True):
        self.dir = dir
        self.game  = game
        self.childs = None
        self.score = game.evaluate()
        self.is_number_added = is_number_added
        self.parent = parent
        self.interesting_child = None
    
    def calculate_score_from_immediate_children(self):
        """
        Updates the score with the best or worst score of the childs
        also updates the value of self.interesting_child
        """
        
        if self.childs is not None:
            child_scores = [child.score for child in self.childs]
            if self.is_number_added:
                interesting_index = np.argmax(child_scores)
            else:
                interesting_index = np.argmin(child_scores)
            self.score = child_scores[interesting_index]
            self.interesting_child = self.childs[interesting_index]
            
        #if len(child_scores) == 0:
        else:
            self.score = self.LOSE_PENALTY
          
    def create_childs(self):
        """
        Creates the childs, and then updates the score of this one
        """
        if self.childs is not None:
            raise ValueError("childs already exist!")
        self.childs = []
        if self.is_number_added:
            for dir, child in self.game.move_list():
                self.childs.append(Tree(child, self, dir, is_number_added=False))     
        else:
            for child in self.game.fill_list():
                self.childs.append(Tree(child, self, "", is_number_added=True))
        if len(self.childs)==0:
            self.childs = None
            
    def propagate_score_to_parents(self):
        """
        Updates the score of the parent taking
        into account this score... recursively
        """
        if self.parent is None:
            return
        self.parent.calculate_score_from_immediate_children()
        self.parent.propagate_score_to_parents()
    
    def extend_tree(self):
        Tree.N_EXTENDS += 1
        if self.interesting_child is not None:
            self.interesting_child.extend_tree()
        else: # the tree should be extended here
            self.create_childs()
            self.calculate_score_from_immediate_children()
            self.propagate_score_to_parents()
            
    def optimize(self):
        Tree.N_EXTENDS = 0
        while(Tree.N_EXTENDS<Tree.MAX_EXTENDS):
            self.extend_tree()
        return self.interesting_child.dir
    """
    def test(self):
        if self.depth==0:
            score = self.current_game.evaluate()
            self.append_to_score(score)
        else:
            dir = self.next_to_test()
            #import pdb
            #pdb.set_trace()
            if dir==None:
                score = self.LOSE_PENALTY
                self.append_to_score(score)
            else:   
                child_game = self.current_game.copy()
                child_game.move(dir)
                child_game.add_number()
                
                current = self.current_game.evaluate()
                child = child_game.evaluate()
                if child<current + Tree.GIVEUP_THRESHOLD:             
                    self.childs[dir].score = min(self.childs[dir].score, child)
                    self.childs[dir].append_to_score(child)
                    return
                else:
                    self.childs[dir].current_game = child_game
                    self.childs[dir].test()
                self.n_pass+=1
                self.score = max([child.score for child in self.childs.values()])
        
    def optimize(self):
        Tree.N_EVALS = 0
        while self.N_EVALS < self.MAX_EVALS:
            self.test()
        childs = []
        scores = []
        for dir, child in self.childs.iteritems():
            game = self.current_game.copy()
            if game.move(dir):
                print dir, ":", child.score,"\t",
                childs.append(dir)
                scores.append(child.score)
        print ""
        return childs[np.argmax(scores)]
    """  
                    

class Dmqh(object):
    DEPTH = 3
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
            depth = self.DEPTH
            suggestion = self.optimize(depth)
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
    
    
    def optimize(self, depth):
        tree = Tree(self, None, "")
        return tree.optimize()
        
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