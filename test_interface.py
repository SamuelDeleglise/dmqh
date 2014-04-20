from interface import GameReader
import ImageGrab
from unittest import TestCase, main

class TestInterface(TestCase):
    def test_read(self):
        
        for i in range(10):
            im = ImageGrab.grab((0,0,10,10))
            print im.getpixel((1,1))
    
        
        
        
if __name__=="__main__":
    main()