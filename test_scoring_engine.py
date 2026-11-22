import unittest
from scoring_engine import calculate, DISTANCE_WEIGHTS, PERMISSION_WEIGHTS

class TestEngine(unittest.TestCase):
    def test_zero(self):
        r=calculate('A', {k:0 for k in DISTANCE_WEIGHTS}, {k:0 for k in PERMISSION_WEIGHTS})
        self.assertEqual((r.raw_weirdness,r.permission_ceiling,r.permission_gap),(0,0,0))
    def test_full(self):
        r=calculate('A', {k:10 for k in DISTANCE_WEIGHTS}, {k:10 for k in PERMISSION_WEIGHTS})
        self.assertEqual((r.raw_weirdness,r.permission_ceiling,r.permission_gap),(100,100,0))
    def test_bridge_and_gap(self):
        r=calculate('A', {k:6 for k in DISTANCE_WEIGHTS}, {k:4 for k in PERMISSION_WEIGHTS}, 10)
        self.assertEqual((r.raw_weirdness,r.effective_weirdness,r.permission_ceiling,r.permission_gap),(60,50,40,10))
    def test_bridge_floor(self):
        r=calculate('A', {k:0 for k in DISTANCE_WEIGHTS}, {k:1 for k in PERMISSION_WEIGHTS}, 20)
        self.assertEqual(r.effective_weirdness,0)
    def test_validation(self):
        with self.assertRaises(ValueError):
            calculate('A',{k:11 for k in DISTANCE_WEIGHTS},{k:4 for k in PERMISSION_WEIGHTS})
        with self.assertRaises(ValueError):
            calculate('A',{k:3 for k in DISTANCE_WEIGHTS},{k:4 for k in PERMISSION_WEIGHTS},21)

if __name__=='__main__': unittest.main()
