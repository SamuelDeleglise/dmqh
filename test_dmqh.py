from dmqh import Dmqh

from unittest import TestCase, main
import numpy as np

class TestDmqh(TestCase):
    def test_crunch(self):
        d = Dmqh(4)
        self.assertEquals(d.crunch([2,0,2,0]), [4,0,0,0])
        self.assertEquals(d.crunch([4,0,2,0]), [4,2,0,0])
        self.assertEquals(d.crunch([4,2,2,0]), [4,4,0,0])
        self.assertEquals(d.crunch([4,2,0,2]), [4,4,0,0])
        self.assertEquals(d.crunch([4,2,0,4]), [4,2,4,0])
        self.assertEquals(d.crunch([4,2,4,2]), [4,2,4,2])
        self.assertEquals(d.crunch([4,2,2,2]), [4,4,2,0])

    def test_evaluate(self):
         d = Dmqh(4)
         d.dat = np.array([[16,8,4,2], [0,8,4,2], [0,8,4,2], [0,8,4,2]])
         d2 = Dmqh(4)
         d2.dat = np.array([[0,32,4,2], [0,8,4,2], [0,8,4,2], [0,8,4,2]])
         self.assertGreater(d.evaluate(), d2.evaluate())
         
         d = Dmqh(4)
         d.dat = np.array([[32,8,4,2], [0,8,4,2], [0,8,4,2], [0,8,4,2]])
         d2 = Dmqh(4)
         d2.dat = np.array([[16,8,4,2], [0,8,4,2], [0,8,4,2], [0,8,4,2]])
         self.assertGreater(d.evaluate(), d2.evaluate())

        

if __name__=="__main__":
    main()