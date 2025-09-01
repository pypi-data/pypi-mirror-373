
from context import ngawari # This is useful for testing outside of environment

import unittest
import numpy as np
from ngawari import ftk


X = np.array([[0.19595138],
       [0.28244273],
       [0.45592566],
       [0.35177724],
       [0.57638623]])
Y = np.array([[0.61853641],
       [0.25369352],
       [0.1260536 ],
       [0.35207552],
       [0.92626204]])

X3 = np.array([[0.71475586, 0.48374974, 0.3985763 ],
       [0.5947318 , 0.46076401, 0.64773692],
       [0.87300795, 0.77204808, 0.83556571],
       [0.57376541, 0.94480634, 0.62267837],
       [0.02153639, 0.58467618, 0.74268892],
       [0.15408349, 0.82252412, 0.7125407 ],
       [0.05485892, 0.29044018, 0.77315737],
       [0.50089607, 0.9867252 , 0.38755493],
       [0.1811874 , 0.91620362, 0.28336708],
       [0.54303034, 0.45485989, 0.83904176]])
Y3 = [[0.2649689 , 0.96211135, 0.56446571],
       [0.49264008, 0.33443869, 0.73324406],
       [0.43922418, 0.13154316, 0.61616767],
       [0.68390255, 0.8233132 , 0.98477085],
       [0.61507173, 0.91082717, 0.2340875 ],
       [0.96827111, 0.1634428 , 0.53836741],
       [0.27115301, 0.35359689, 0.57920636],
       [0.23569023, 0.31575776, 0.86145901],
       [0.94317451, 0.842682  , 0.6084494 ],
       [0.1107103 , 0.31264041, 0.47223656]]

Y3_ = np.array(Y3).T



class TestFTK(unittest.TestCase):

    def test_getIDOfClosestFloat(self):
        float_list = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(ftk.getIDOfClosestFloat(3.2, float_list), 2)
        self.assertEqual(ftk.getIDOfClosestFloat(1.8, float_list), 1)

    def test_getClosestFloat(self):
        float_list = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(ftk.getClosestFloat(3.2, float_list), 3.0)
        self.assertEqual(ftk.getClosestFloat(1.8, float_list), 2.0)

    def test_distPointPoints(self):
        point = [0, 0, 0]
        points = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]]
        expected = [1, 1, 1, np.sqrt(3)]
        np.testing.assert_array_almost_equal(ftk.distPointPoints(point, points), expected)

    def test_normaliseArray(self):
        vecs = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        normalized = ftk.normaliseArray(vecs)
        expected = [[1.0/np.sqrt(3.), 1.0/np.sqrt(3.), 1.0/np.sqrt(3.)] for _ in range(3)]
        np.testing.assert_array_almost_equal(normalized, expected)

    def test_angleBetween2Vec(self):
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        self.assertAlmostEqual(ftk.angleBetween2Vec(v1, v2), np.pi/2)
        self.assertAlmostEqual(ftk.angleBetween2Vec(v1, v2, RETURN_DEGREES=True), 90)

    def test_fitPlaneToPoints(self):
        points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
        plane = ftk.fitPlaneToPoints(points)
        expected = [0, 0, 1, 0]  # z = 0 plane
        np.testing.assert_array_almost_equal(plane, expected)
        plane = ftk.fitPlaneToPoints(X3)
        expected = [ 0.062458, -0.542385, -0.837805,  0.861037]  
        np.testing.assert_array_almost_equal(plane, expected)

    def test_projectPtsToPlane(self):
        pts = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        plane = [0, 0, 1, -1]  # z = 1 plane
        projected = ftk.projectPtsToPlane(pts, plane)
        expected = [[1, 1, 1], [2, 2, 1], [3, 3, 1]]
        np.testing.assert_array_almost_equal(projected, expected)

    def test_buildCircle3D(self):
        center = [0, 0, 0]
        normal = [0, 0, 1]
        radius = 1
        circle = ftk.buildCircle3D(center, normal, radius, nPts=4)
        expected = [[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]]
        deltas = [np.min(ftk.distPointPoints(circle[i], expected)) for i in range(4)]
        np.testing.assert_array_less(deltas, 0.01)


if __name__ == '__main__':
    unittest.main()
