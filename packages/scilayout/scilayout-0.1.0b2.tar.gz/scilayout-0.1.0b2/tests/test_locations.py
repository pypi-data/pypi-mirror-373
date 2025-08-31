import unittest
from matplotlib.figure import Figure
from matplotlib.pyplot import close

from tests import utils
utils.add_parent_dir_to_sys_path()

from scilayout.locations import locationcm_to_position

places = 7

class TestLocationToPosition(unittest.TestCase):
    def setUp(self):
        self.fig = Figure(figsize=(6, 4))
    
    def tearDown(self):
        close(self.fig)

    def test_location_to_position_positive_values(self):
        location = (1, 2, 5, 3)
        expected_result = (0.06561679790026247, 0.7047244094488189, 0.26246719160104987, 0.09842519685039364)
        result = locationcm_to_position(self.fig, location)
        for res, exp in zip(result, expected_result):
            self.assertAlmostEqual(res, exp, places=places)

    def test_location_to_position_negative_values(self):
        location = (-2, -3, -1, -1)
        expected_result = (-0.13123359580052493, 1.0984251968503937, 0.06561679790026247, 0.19685039370078727)
        result = locationcm_to_position(self.fig, location)
        for res, exp in zip(result, expected_result):
            self.assertAlmostEqual(res, exp, places=places)

    def test_location_to_position_zero_values(self):
        location = (0, 0, 0, 0)
        expected_result = (0.0, 1.0, 0.0, 0.0)
        result = locationcm_to_position(self.fig, location)
        for res, exp in zip(result, expected_result):
            self.assertAlmostEqual(res, exp, places=places)

    def test_location_to_position_different_values(self):
        location = (2, 1, 6, 4)
        expected_result = (0.13123359580052493, 0.6062992125984252, 0.2624671916010498, 0.295275590551181)
        result = locationcm_to_position(self.fig, location)
        for res, exp in zip(result, expected_result):
            self.assertAlmostEqual(res, exp, places=places)

if __name__ == '__main__':
    unittest.main()