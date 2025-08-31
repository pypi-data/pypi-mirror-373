import unittest

from matplotlib.pyplot import close

import scilayout


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.fig = scilayout.figure()
        self.fig.set_size_cm(13, 10)
        self.grid = self.fig.grid
    
    
    def tearDown(self):
        close(self.fig)
    
    
    def test_grid_init(self):
        pass
    
    
    def test_grid_clearing_and_drawing(self):
        """Using fig.clear() and how it interacts with the grid"""
        pass
    
    def test_grid_parameters(self):
        """Test that grid can have its parameters changed properly"""
        pass
    
    
    