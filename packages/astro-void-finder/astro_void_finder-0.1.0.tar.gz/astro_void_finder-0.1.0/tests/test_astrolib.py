# Beispiel-Unit-Tests für die AstroLib-Funktionalitäten
import unittest
import numpy as np
from astrolib import voidfinder, nbody, neutrino

class TestVoidFinder(unittest.TestCase):
    def test_density_field_estimate(self):
        positions = np.random.random((100, 3))
        masses = np.ones(100)
        grid_size = 32
        density = voidfinder.density_field_estimate(positions, masses, grid_size)
        self.assertEqual(density.shape, (grid_size, grid_size, grid_size))
        
class TestNBody(unittest.TestCase):
    def test_force_calculation(self):
        pos1 = np.array([0., 0., 0.])
        pos2 = np.array([1., 0., 0.])
        mass2 = 1.0
        force = nbody.calculate_force(pos1, pos2, mass2)
        self.assertEqual(len(force), 3)
        
class TestNeutrino(unittest.TestCase):
    def test_pmns_matrix(self):
        theta12 = 0.59
        theta23 = 0.785
        theta13 = 0.15
        delta_cp = 0.0
        matrix = neutrino.pmns_matrix(theta12, theta23, theta13, delta_cp)
        self.assertEqual(matrix.shape, (3, 3))

if __name__ == '__main__':
    unittest.main()
