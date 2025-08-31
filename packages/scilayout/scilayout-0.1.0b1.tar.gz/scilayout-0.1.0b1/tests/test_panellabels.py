import unittest

from matplotlib.pyplot import close

from tests import utils
utils.add_parent_dir_to_sys_path()

import scilayout

class TestPanelLabels(unittest.TestCase):
    def setUp(self):
        self.fig = scilayout.figure()
        self.ax = self.fig.add_panel((1, 2, 5, 5), method='size')
        self.ax.add_label('a')
        self.panellabel = self.ax.panellabel
    
    
    def tearDown(self):
        close(self.fig)
    
    
    def test_initial_panel_labels(self):
        xoffset = scilayout.style.params['panellabel.xoffset']
        yoffset = scilayout.style.params['panellabel.yoffset']
        self.assertEqual(self.panellabel.xoffset, xoffset)
        self.assertEqual(self.panellabel.yoffset, yoffset)
        pos = self.panellabel.get_location()
        self.assertAlmostEqual(pos[0], 1 + xoffset)
        self.assertAlmostEqual(pos[1], 2 + yoffset)
        

    def test_panel_reposition(self):
        """Test that the label is repositioned when the panel is moved"""
        self.ax.set_location((2, 3, 6, 6), method='size')
        xoffset = scilayout.style.params['panellabel.xoffset']
        yoffset = scilayout.style.params['panellabel.yoffset']
        pos = self.panellabel.get_location()
        self.assertAlmostEqual(pos[0], 2 + xoffset)
        self.assertAlmostEqual(pos[1], 3 + yoffset)
    
    
    def test_set_location(self):
        """Set locations of panel labels manually"""
        # Test x position
        self.panellabel.set_location(x=3)
        pos = self.panellabel.get_location()
        self.assertAlmostEqual(pos[0], 3)
        
        # Test y position
        self.panellabel.set_location(y=4.2)
        pos = self.panellabel.get_location()
        self.assertAlmostEqual(pos[1], 4.2)
        
        # Test both x and y location changes
        self.panellabel.set_location(x=1.5, y=2.5)
        pos = self.panellabel.get_location()
        self.assertAlmostEqual(pos[0], 1.5)
        self.assertAlmostEqual(pos[1], 2.5)
    

if __name__ == '__main__':
    unittest.main()