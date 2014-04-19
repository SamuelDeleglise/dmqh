from __future__ import division

import numpy as np
import copy

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

class Dmqh(object):
    
    def __init__(self, n):
        self.n = n
        self.dat = np.zeros((n,n), dtype=int) 
        self.add_number()
        self.add_number()
    
    def empty_places(self):
        """returns the list of free slots"""
        return np.where(self.dat==0)
    
    def add_number(self):
        position = np.random.randint(len(self.empty_places()[0]))
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
            #depth = np.floor(10./(len(self.empty_places()[0])+1))
            #depth = max(depth, 2)
            #depth = min(depth, 3)
            depth = 5
            print "depth :", depth
            
            suggestion = self.optimize(depth)
            print "press one of the keys i,j,k or l in the console to move... my advise:" \
            , suggestion
            if auto:
                c = suggestion[0]
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
                    total+=val**2
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
        """
        n = 0
        for val,x,y in self.snake_coords():
            n+=1
            if n>3:
                break 
            if val==0:
                game = self.copy()
                for v in [2,4]:
                    game.dat[x,y] = v
                    yield game
        """            
        for tries in range(2):
            game = self.copy()
            game.add_number()
            yield game
            
        """
        for x,y in zip(*self.empty_places()):
            for val in [2,4]:
                game = self.copy()
                game.dat[x,y] = val
                yield game
        """
    def mean_score(self, depth):
        """
        Computes the mean score.
        """
        
        mean_val = 0
        n_fill = 0
        if depth==0:
            for pos in res.fill_list():
                n_fill+=1
                mean_val = mean_val + pos.evaluate()
            mean_val/=n_fill
            return mean_val
        
        self.optimize(depth)
        
        
    def optimize(self, depth):
        if depth==0:
            return ("", self.evaluate())
        mean_scores = []
        directions = []
        previous_score = self.evaluate()
        for move, res in self.move_list():
            if depth>10:
                print "->"*(depth-1), move
            mean_score = 0
            n = 0
            if res.evaluate()<previous_score:
                continue
            for pos in res.fill_list():
                (dir, score) = pos.optimize(depth - 1)
                
                n+=1
#                mean_score = min(mean_score, score)
                mean_score+=score
            mean_score/=n
            if depth>10:
                print "->"*(depth-1), mean_score, dir
            mean_scores.append(mean_score)
            directions.append(move)
        if len(mean_scores)==0: ### GAME OVER
            return ("", -1000000)
        best = np.argmax(mean_scores)
        return (directions[best], mean_scores[best])
    
if __name__=="__main__":
    GAME = Dmqh(4)
    GAME.play(auto=True)