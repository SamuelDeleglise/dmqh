from dmqh import Dmqh

from unittest import TestCase, main

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

if __name__=="__main__":
    main()