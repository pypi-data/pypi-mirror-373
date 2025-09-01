
from context import ngawari # This is useful for testing outside of environment

import os
import shutil
import unittest
import numpy as np
from ngawari import fIO
from ngawari import vtkfilters


this_dir = os.path.split(os.path.realpath(__file__))[0]
TEST_DIRECTORY = os.path.join(this_dir, 'TEST_DATA')
imageFile = os.path.join(TEST_DIRECTORY, 'test-image.vti')
pvdFile = os.path.join(TEST_DIRECTORY, 'test-pvd.pvd')
pvdFile2 = os.path.join(TEST_DIRECTORY, 'test-pvd2.pvd')

os.makedirs(TEST_DIRECTORY, exist_ok=True)
DEBUG = False

if DEBUG: 
    print('')
    print("WARNING - RUNNING IN DEBUG MODE - TEST OUTPUTS WILL NOT BE CLEANED")
    print('')

# def cleanMakeDirs(idir):
#     try:
#         os.makedirs(idir)
#     except FileExistsError:
#         shutil.rmtree(idir)
#         os.makedirs(idir)


def buildSinusoidalVTI(freq, phase, N=10):
    """Generate a 3D sinusoidal dataset.
    """
    ii = vtkfilters.buildRawImageData(dims=[N,N,N], res=[1,1,1], origin=[0,0,0])
    x = np.linspace(0, 2*np.pi, N)
    y = np.linspace(0, 2*np.pi, N)
    z = np.linspace(0, 2*np.pi, N)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    A = np.sin(freq*X + phase) * \
        np.sin(freq*Y + phase) * \
        np.sin(freq*Z + phase)
    A = (A + 1) / 2
    vtkfilters.addNpArray(ii, A, 'sinusoidalArray', SET_SCALAR=True, IS_3D=True)
    return ii

def buildVTIDict():
    vtiDict = {}
    for iTime in [0.1, 0.3, 0.6, 0.99]:
        vtiDict[iTime] = buildSinusoidalVTI(0.5, 4.0*iTime, 15)
    return vtiDict

class TestBuildVTI(unittest.TestCase):
    def runTest(self):
        N = 12
        image = buildSinusoidalVTI(0.5, 3.0, N)
        dims = [0,0,0]
        image.GetDimensions(dims)
        self.assertEqual(image.GetNumberOfPoints(), N*N*N, "Incorrect number of points")
        self.assertEqual(image.GetNumberOfCells(), (N-1)*(N-1)*(N-1), "Incorrect number of cells")
        self.assertEqual(image.GetPointData().GetArrayName(0), 'sinusoidalArray', "Incorrect array name")
        self.assertEqual(dims, [N,N,N], "Incorrect dimensions")
        self.assertEqual(image.GetOrigin(), (0,0,0), "Incorrect origin")
        self.assertEqual(image.GetSpacing(), (1,1,1), "Incorrect spacing")

        
class TestReadVTI(unittest.TestCase):
    def runTest(self):
        N = 15
        image = buildSinusoidalVTI(0.5, 4.0, N)
        fIO.writeVTKFile(image, imageFile)
        image2 = fIO.readVTKFile(imageFile)
        self.assertEqual(image2.GetNumberOfPoints(), N*N*N, "Incorrect number of points")
        self.assertEqual(image2.GetNumberOfCells(), (N-1)*(N-1)*(N-1), "Incorrect number of cells")
        A = vtkfilters.getScalarsAsNumpy(image2)
        self.assertAlmostEqual(A[36], 0.205667, places=4)
        A3D = vtkfilters.getScalarsAsNumpy(image2, RETURN_3D=True)
        self.assertAlmostEqual(A3D[6,4,5], 0.136813, places=4)
        if not DEBUG:
            os.unlink(imageFile)


class TestWritePVD(unittest.TestCase):
    def runTest(self):
        vtiDict = buildVTIDict()
        fOut = fIO.writeVTK_PVD_Dict(vtiDict, TEST_DIRECTORY, 'test-pvd', 'vti')
        self.assertEqual(fOut, pvdFile, "Incorrect output file")
        if not DEBUG:
            fIO.deleteFilesByPVD(pvdFile)


class TestReadPVD(unittest.TestCase):
    def runTest(self):
        ID = 656
        file2 = os.path.join(TEST_DIRECTORY, 'test-pvd', 'test-pvd_000002.vti')
        vtiDict = buildVTIDict()
        times1 = sorted(vtiDict.keys())
        fIO.writeVTK_PVD_Dict(vtiDict, TEST_DIRECTORY, 'test-pvd', 'vti')
        vtiDict2 = fIO.readPVD(pvdFile)
        times2 = sorted(vtiDict2.keys())
        self.assertEqual(times1, times2, "Incorrect times")
        #
        for iTime in times1:
            self.assertAlmostEqual(vtkfilters.getScalarsAsNumpy(vtiDict2[iTime])[ID], vtkfilters.getScalarsAsNumpy(vtiDict[iTime])[ID], places=4)
        #
        times3 = fIO.pvdGetTimes(pvdFile)
        self.assertEqual(times1, times3, "Incorrect times")
        #
        T = fIO.pvdGetClosestTimeToT(pvdFile, 0.5)
        self.assertAlmostEqual(T, 0.6, places=4)
        #
        iFile = fIO.pvdGetFileAtT(pvdFile, 0.5)
        self.assertEqual(iFile, file2)
        #
        N = fIO.pvdGetNumberTimePoints(pvdFile)
        self.assertEqual(N, 4)
        #
        fIO.pvdResetStartPoint(pvdFile, 0.5, pvdFile2)
        vtiDict2 = fIO.readPVDFileName(pvdFile2)
        times4 = sorted(vtiDict2.keys())
        self.assertEqual(vtiDict2[times4[0]], file2, "Incorrect file after reset")
        #
        if not DEBUG:
            fIO.deleteFilesByPVD(pvdFile)
            fIO.deleteFilesByPVD(pvdFile2)


class TestTarGZLocal_AndMove(unittest.TestCase):
    def runTest(self):
        vtiDict = buildVTIDict()
        fOut = fIO.writeVTK_PVD_Dict(vtiDict, TEST_DIRECTORY, 'test-pvd', 'vti')
        pvdDir = os.path.join(TEST_DIRECTORY, 'test-pvd')
        fIO.tarGZLocal_AndMove(pvdDir, 'test-pvd.tar.gz', TEST_DIRECTORY)
        self.assertTrue(os.path.exists(os.path.join(TEST_DIRECTORY, 'test-pvd.tar.gz')))
        if not DEBUG:
            os.unlink(os.path.join(TEST_DIRECTORY, 'test-pvd.tar.gz'))







if __name__ == '__main__':
    unittest.main()
