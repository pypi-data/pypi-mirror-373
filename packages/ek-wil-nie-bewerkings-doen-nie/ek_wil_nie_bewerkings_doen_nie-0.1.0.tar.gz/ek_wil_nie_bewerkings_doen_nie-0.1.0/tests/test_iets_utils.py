import unittest
import numpy as np
from ek_wil_nie_bewerkings_doen_nie_library import (
    een_t_toets,
    twee_t_toets,
    gepaard_t_toets,
    anova,
    chi_kwadraat_onafhanklik,
    chi_kwadraat_pasvorm,
    f_toets,
    z_toets
)

class TestStatsFunctions(unittest.TestCase):

    def test_een_t_toets(self):
        data = np.array([9.8, 10.1, 9.9, 10.2, 9.7, 10.3, 10.0, 9.6, 10.4, 9.9])
        mean = 10.0
        t_stat, p_val = een_t_toets(data, mean)
        self.assertAlmostEqual(t_stat, -0.12156613477096352, places=5)   # replace 0.0 with your actual expected t-stat
        self.assertAlmostEqual(p_val, 0.9059136241299492, places=5)    # replace 1.0 with your actual expected p-value

    def test_twee_t_toets(self):
        a = np.array([3.1, 3.4, 3.2, 3.5, 3.3])
        b = np.array([3.7, 3.8, 3.6, 3.9, 3.8])
        t_stat, p_val = twee_t_toets(a, b)
        self.assertAlmostEqual(t_stat, -5.276561879022928, places=5)  # replace with actual t-stat
        self.assertAlmostEqual(p_val, 0.0007493176296417789, places=2)   # replace with actual p-value

    def test_gepaard_t_toets(self):
        before = np.array([70, 72, 68, 65, 74])
        after = np.array([68, 70, 66, 64, 73])
        t_stat, p_val = gepaard_t_toets(before, after)
        self.assertAlmostEqual(t_stat, 6.531972647421809, places=5)  # replace with actual t-stat
        self.assertAlmostEqual(p_val, 0.002837845926734446, places=2)    # replace with actual p-value

    def test_anova(self):
        g1 = np.array([85, 88, 90, 87, 86])
        g2 = np.array([78, 74, 80, 77, 76])
        g3 = np.array([92, 95, 93, 91, 94])
        f_stat, p_val = anova(g1, g2, g3)
        self.assertAlmostEqual(f_stat, 87.87500000000011, places=2)   # replace with actual F-stat
        self.assertAlmostEqual(p_val, 6.81722773546615e-08, places=2)   # replace with actual p-value

    def test_chi_kwadraat_onafhanklik(self):
        data = np.array([[30, 10], [10, 50]])
        chi2_stat, p_val = chi_kwadraat_onafhanklik(data)
        self.assertAlmostEqual(chi2_stat, 31.640625, places=3)  # replace with actual chi2
        self.assertAlmostEqual(p_val, 1.855079746912165e-08, places=2)        # replace with actual p-value

    def test_chi_kwadraat_pasvorm(self):
        observed = np.array([18, 16, 14, 15, 18, 19])
        expected = np.array([16.66666667, 16.66666667, 16.66666667, 16.66666667, 16.66666667, 16.66666667])
        chi2_stat, p_val = chi_kwadraat_pasvorm(observed, expected)
        self.assertAlmostEqual(chi2_stat, 1.1599999997679997, places=3)   # replace with actual chi2
        self.assertAlmostEqual(p_val, 0.9486567758101276, places=3)       # replace with actual p-value

    def test_f_toets(self):
        a = np.array([24, 26, 22, 25, 23])
        b = np.array([30, 28, 29, 27, 31])
        f_stat, p_val = f_toets(a, b)
        self.assertAlmostEqual(f_stat, 1.0, places=4)     # replace with actual F-stat
        self.assertAlmostEqual(p_val, 0.5, places=2)        # replace with actual p-value

    def test_z_toets(self):
        data = np.array([498, 502, 501, 489, 500, 503, 497, 500, 501, 499])
        pop_var = 4
        z_stat, p_val = z_toets(data, pop_var)
        self.assertAlmostEqual(z_stat, -1.5811388300841895, places=2)        # replace with actual z-stat
        self.assertAlmostEqual(p_val, 0.11384629800665813, places=2)         # replace with actual p-value

if __name__ == "__main__":
    unittest.main()
