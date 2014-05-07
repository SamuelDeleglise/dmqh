from __future__ import division
from dmqh_new import Dmqh, random_from_distribution


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

    def test_random(self):
        vals = {0:0,1:0,2:0,3:0}
        total = 10000
        for i in range(total):
            res = random_from_distribution([10,25,25,40])
            vals[res]+=1
        self.assertGreater(vals[0]/total, 0.05)
        self.assertGreater(0.15,vals[0]/total)
        
        self.assertGreater(vals[1]/total, 0.2)
        self.assertGreater(0.3,vals[1]/total)

        self.assertGreater(vals[2]/total, 0.2)
        self.assertGreater(0.3,vals[2]/total)
        
        self.assertGreater(vals[3]/total, 0.35)
        self.assertGreater(0.45, vals[3]/total)
        
    def test_bug(self):
        d = Dmqh(4)
        d.dat = np.array([[256,128,64,32], [0,4,8,32], [2,4,2,8], [0,2,8,2]])
        d.optimize(depth=3)
        
    def test_bug2(self):
        d = Dmqh(4)
        d.dat = np.array([[2048,1024,256,32], [16,32,64,16], [2,16,8,4], [2,8,4,2]])
        print d
        print d.optimize(depth=3)
        
    def test_bug3(self):
        d = Dmqh(4)
        d.dat = np.array([[1024,512,256,128], [0,0,32,0], [0,0,0,0],[0,0,0,2]])
        print d
        print d.optimize(depth=5)
    
    def update_score(self):
        pass
    
"""    def test_optimize(self):
        d = Dmqh(4)
        d.dat = np.array([[2,0,2,0], [2,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=1)[0]=="j")     
""" 
    
"""
    def test_optimize(self):
        d = Dmqh(4)
        d.dat = np.array([[0,8,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=1)[0]=="j")
        
        d = Dmqh(4)
        d.dat = np.array([[0,2,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=1)[0]=="j")

        d = Dmqh(4)
        d.dat = np.array([[4,0,2,0], [4,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=1)[0]=="i")
        
        d = Dmqh(4)
        d.dat = np.array([[32,16,8,4], [4,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=1)[0]=="l")

    def test_optimize_depth_2(self):
        d = Dmqh(4)
        d.dat = np.array([[0,8,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=2)[0]=="j")
        
        d = Dmqh(4)
        d.dat = np.array([[0,8,0,0], [0,8,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=2)[0]=="j")

        d = Dmqh(4)
        d.dat = np.array([[0,2048,0,0], [8,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.assertTrue(d.optimize(depth=2)[0]=="j")

        d = Dmqh(4)
        d.dat = np.array([[64,16,4,4], [16,4,0,0], [4,0,0,0], [0,0,0,0]])
        self.assertEquals(d.optimize(depth=1)[0], "j")
        
    def test_optimize_game_over(self):
        d = Dmqh(4)
        d.dat = np.array([[512,256,128,8], [4,8,16,4], [0,16,4,8], [2,4,2,4]])
        self.assertEquals(d.optimize(depth=2)[0], "j")
        
    def test_strange_bug(self):
        d = Dmqh(4)
        d.dat = np.array([[4,4,4,2], [2,2,2,4], [4,4,2,4], [4,4,2,2]])
    def test_other_bug(self):
        d = Dmqh(4)
        d.dat = np.array([[512,256,64,32], [4,8,32,16], [8,4,4,4], [4,2,0,2]])
        self.assertEqual(d.optimize(d.DEPTH), 'j')
    def test_last(self):
        d = Dmqh(4)
        d.dat = np.array([[2048,512,256,64], [8,32,64,16], [2,16,32,8], [2,8,4,2]])
        self.assertEqual(d.optimize(d.DEPTH), 'j')
"""

if __name__=="__main__":
    main()