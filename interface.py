from screenshot import screengrab
import json
import sqlite3
import time
import shutil

from fake_keyboard import up, down, left, right
from dmqh import Dmqh
import urllib


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    
# enable browser logging

# print messages




class GameReader(object):
    src = "C:\\Users\\Samuel\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Local Storage\\http_gabrielecirulli.github.io_0.localstorage"
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = { 'browser':'ALL' }
    driver = webdriver.Chrome(desired_capabilities=d)
    # load some site
    driver.get('file:///D:/Dropbox/Perso/dmqh/2048.htm')
    
    
    def read(self):
        text = self.driver.find_element_by_id('yop').get_attribute('value')
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
        return game
        
    
    def read_old(self):
        
        
        
        
        p = urllib.urlopen("file:///D:/Dropbox/Perso/dmqh/2048.htm")#"http://gabrielecirulli.github.io/2048/")#
        text = p.read()
        print text
        return text[text.find("<div class=\"tile-container\">"):text.find("<p class=\"game-explanation\">")]
#        <div class="tile tile-8 tile-position-1-1"><div class="tile-inner">8</div></div>
        
        #dst = "C:\\Users\\Samuel\\Desktop\\db.db"
        #shutil.copy(src, dst)
        conn = sqlite3.connect(self.src)        
        c = conn.cursor()
        it = c.execute("SELECT * FROM ItemTable;")
        (best_score, game_state) = it.fetchall()
        game_state = str(game_state[1])
        game_state = game_state.replace('\x00','')
        game_state = json.loads(game_state)
        
        game = Dmqh(4)
        
        for x,val in enumerate(game_state['grid']['cells']):
            for y,val in enumerate(val):
                if val==None:
                    val = 0
                else:
                    val =  val['value']
                game.dat[x,y] = val
        game.dat = game.dat.T
        conn.close()
        return game
        
    def play(self):
        while(True):
            game = self.read()
            print "present state of the game is:"
            print game
            #raw_input('OK?')
            suggestion = game.optimize(5)[0]
            print "my suggestion is: ", suggestion
            print 'pressing',
            if suggestion == "i":
                print 'up ',
                up()
            if suggestion == "j":
                print 'left ',
                left()
            if suggestion == "l":
                print 'right ',
                right()
            if suggestion == "k":
                print 'down ', 
                down()
            
                
        