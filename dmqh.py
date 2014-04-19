import numpy as np


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
        val = 2**(1 + np.random.randint(2))
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
                    
    def play(self):
        while(True):
            print ""
            print "current position:"
            print self
            print "press one of the keys i,j,k or l in the console to move..."
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
    
    
if __name__=="__main__":
    GAME = Dmqh(4)
    GAME.play()