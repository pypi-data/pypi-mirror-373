"""
@author Fraser Callaghan
"""

import numpy as np
import itertools
from scipy import stats
from scipy import optimize, interpolate
from scipy.spatial import cKDTree
import vtk


# ======================================================================================================================
#           MATH
# ======================================================================================================================
def getIDOfClosestFloat(iFloat, floatList):
    return np.argmin([abs(i-iFloat) for i in floatList])


def getClosestFloat(iFloat, floatList):
    return floatList[getIDOfClosestFloat(iFloat, floatList)]


def getIDOfClosestPoint(point, points):
    dist_2 = squareDistPointPoints(point, points)
    return np.argmin(dist_2)


def getClosestPoint(point, points):
    return points[getIDOfClosestPoint(point, points)]


def distPointPoints(point, points):
    dist_2 = squareDistPointPoints(point, points)
    return np.sqrt(dist_2)


def squareDistPointPoints(point, points):
    points = np.asarray(points)
    if points.ndim == 1:
        points = points[np.newaxis, :]
    deltas = points - point
    dist_2 = np.einsum('ij,ij->i', deltas, deltas)
    return dist_2


def sortedIDsOfClosestPoints(point, points):
    dist_2 = squareDistPointPoints(point, points)
    return np.argsort(dist_2)


def distTwoPoints(a, b):
    return distPointPoints(a, [b])[0]


def getIDsOfClosestPoints(pointsA, pointsB):
    pointsA = np.asarray(pointsA)
    pointsB = np.asarray(pointsB)
    distances = np.sum((pointsA[:, np.newaxis, :] - pointsB[np.newaxis, :, :]) ** 2, axis=2)
    minIDa, minIDb = np.unravel_index(np.argmin(distances), distances.shape)
    return minIDa, minIDb


def getIDsOfFartherestPoints(pointsA, pointsB):
    pointsA = np.asarray(pointsA)
    pointsB = np.asarray(pointsB)
    distances = np.sum((pointsA[:, np.newaxis, :] - pointsB[np.newaxis, :, :]) ** 2, axis=2)
    maxIDa, maxIDb = np.unravel_index(np.argmax(distances), distances.shape)
    return maxIDa, maxIDb


def vectorMagnitudes(vecs):
    vecs = np.asarray(vecs)
    try:
        return np.sqrt(np.sum(vecs*vecs,-1))
    except IndexError:
        return np.array([np.linalg.norm(vecs)])


def normaliseArray(vectors):
    """
    Normalise an array of vectors.

    Parameters:
    vectors (array-like): Input array of vectors. Can be 1D or 2D.

    Returns:
    numpy.ndarray: Array of normalised vectors.
    """
    vectors = np.asarray(vectors)
    if vectors.ndim == 1:
        vectors = vectors[np.newaxis, :]
    magnitudes = np.linalg.norm(vectors, axis=-1, keepdims=True)
    magnitudes = np.maximum(magnitudes, 1e-8) # Avoid division by zero
    normalised = vectors / magnitudes
    
    return normalised.squeeze()


def angleBetween2Vec(v1, v2, RETURN_DEGREES=False):
    """
    Returns the angle in radians between vectors 'v1' and 'v2'::
        Can be lists of same size
    :param v1:
    :param v2:
    :param RETURN_DEGREES:
    :return: angle in radians
    """
    if RETURN_DEGREES:
        return vtk.vtkMath.DegreesFromRadians(angleBetween2Vec(v1, v2, RETURN_DEGREES=False))
    return vtk.vtkMath.AngleBetweenVectors(v1, v2)


def angleBetweenVecAndPlane(vector, planeNormal):
    return np.arcsin(abs(np.dot(vector, planeNormal)) / (np.linalg.norm(vector)) * np.linalg.norm(planeNormal))


def areVecsMatching(v1, v2, angleTol_rad, magTol):
    m1, m2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if abs(m1 - m2) > magTol:
        return False
    theta = angleBetween2Vec(v1, v2)
    if theta > angleTol_rad:
        return False
    return True


def __forcePts_nx3(pts):
    pts = np.array(pts)
    dims = pts.shape
    if len(dims) == 1:
        pts = np.reshape(pts, (1,dims[0]))
    else:
        if ((dims[0] == 3) and (dims[1] != 3)) | ((dims[0] == 2) and (dims[1] > 3)):
            pts = pts.T
    return pts


# ======================================================================================================================
#           FITTING & PROJECTION
# ======================================================================================================================
def linearFit(X ,Y):
    """
    Fit a linear model to the data.

    Parameters:
    - X: Independent variable.
    - Y: Dependent variable.

    Returns:
    slope, intercept, R, pValue, std: Parameters of the linear model.
    """
    slope, intercept, R, pValue, std = stats.linregress(X, Y) # c, m, R
    return slope, intercept, R, pValue, std


def fitPlaneToPoints(pts):
    """
    Fit a plane to a set of 3D points.

    Parameters:
    - pts: A numpy array of shape (N, 3) representing the 3D points.

    Returns:
    - planeABC: Coefficients of the plane equation [a, b, c, d].
    """
    pts = __forcePts_nx3(pts)
    A = pts - np.mean(pts, 0)
    _, S, V = np.linalg.svd(A)
    i = np.argmin(S)  # find position of minimal singular value
    coeff = V[i, :]  # this may be multiple
    planeABC = coeff / np.linalg.norm(coeff[:3])
    Ds = [planeABC[0]*x[0]+planeABC[1]*x[1]+planeABC[2]*x[2] for x in pts]
    return np.hstack((planeABC, -np.mean(Ds)))


def polyfit2d(x, y, z, order=3):
    ncols = (order + 1) ** 2
    G = np.zeros((x.size, ncols))
    ij = itertools.product(range(order + 1), range(order + 1))
    for k, (i, j) in enumerate(ij):
        G[:, k] = x ** i * y ** j
    m, _, _, _ = np.linalg.lstsq(G, z, rcond=None)
    return m


def polyval2d(x, y, m):
    order = int(np.sqrt(len(m))) - 1
    ij = itertools.product(range(order + 1), range(order + 1))
    z = np.zeros_like(x)
    for a, (i, j) in zip(m, ij):
        z += a * x ** i * y ** j
    return z


def projectPtsToPlane(pts, plane):
    """
    projects the points so all lie on the plane
    :param pts: list/array of points Nx3
    :param plane: equation of plane: either [a,b,c,d] or [norm, ptInPlane]
    :return: pts array all lying on plane
    """
    if isinstance(plane, tuple):
        planeNorm = plane[0]
        inplanePt = plane[1]
        D = -inplanePt[0] * planeNorm[0] - inplanePt[1] * planeNorm[1] - \
            inplanePt[2] * planeNorm[2]
    else:
        planeNorm = plane[:3]
        D = plane[3]
    pts = __forcePts_nx3(pts)
    fraction = (planeNorm[0] * pts[:, 0] +
                planeNorm[1] * pts[:, 1] +
                planeNorm[2] * pts[:, 2] + D) / \
               (planeNorm[0] ** 2 + planeNorm[1] ** 2 + planeNorm[2] ** 2)
    x0 = pts[:, 0] - planeNorm[0] * fraction
    y0 = pts[:, 1] - planeNorm[1] * fraction
    z0 = pts[:, 2] - planeNorm[2] * fraction
    return np.column_stack((x0, y0, z0))


def project3DPointsToPlanarCoordinateSystem(pts, planeNorm=None):
    origin = np.mean(pts, axis=0)
    normal = planeNorm / np.linalg.norm(planeNorm)
    projected_points = projectPtsToPlane(pts, (planeNorm, origin))
    # Create a local coordinate system on the plane
    # Find two vectors in the plane
    u = projected_points[1] - projected_points[0]
    u = u / np.linalg.norm(u)
    v = np.cross(normal, u)
    # Convert the projected 3D points to 2D coordinates in the (u, v) plane
    points_2d = np.array([[np.dot(pt - origin, u), np.dot(pt - origin, v)] for pt in projected_points])
    return points_2d, u, v, origin


def project3DPointsToPlanarCoordinateSystem_OLD(pts, planeNorm=None):
    """
    Will rotate pts to lie in given plane
       - shifts pts to be centered on origin
        FIXME: If points are aligned with an axis (almost) then will fail.
       - raise LinAlgError
          Need to check for this, then simply rotate by different vector set.
    source: http://mathforum.org/library/drmath/view/51727.html
    source: https://stackoverflow.com/questions/23472048/projecting-3d-points-to-2d-plane
    :param pts:
    :param planeNorm:
    :return:
    """
    pts = __forcePts_nx3(pts)
    npts, _ = pts.shape
    try:
        len(planeNorm)
    except TypeError:
        planeNorm = fitPlaneToPoints(pts)[:3]
    planeNorm = planeNorm / np.linalg.norm(planeNorm)
    cPt = np.mean(pts, 0)
    pPts = projectPtsToPlane(pts, (planeNorm, cPt))
    e1 = np.array([-1 * planeNorm[1], planeNorm[0], 0.0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(planeNorm, e1)
    A = np.array([e1[:2], e2[:2]])
    xPrime = np.zeros((npts, 2))
    for k1 in range(npts):
        b = pPts[k1] - cPt
        xPrime[k1, :] = np.linalg.solve(A.T, b[:2])
    return xPrime, e1, e2, cPt


def project3DPointsToPlanarCoordinateSystem2(pts, planeNorm=None, datumPt=None):
    # https://stackoverflow.com/questions/26369618/getting-local-2d-coordinates-of-vertices-of-a-planar-polygon-in-3d-space
    pts = __forcePts_nx3(pts)
    npts, _ = pts.shape
    if planeNorm is None:
        planeNorm = fitPlaneToPoints(pts)[:3]
    if datumPt is None:
        datumPt = np.mean(pts,0)
    locx = pts[0] - datumPt
    locy = np.cross(planeNorm, locx)
    locx = locx / np.linalg.norm(locx)
    locy = locy / np.linalg.norm(locy)
    xy = [[np.dot(p-datumPt,locx), np.dot(p-datumPt,locy)] for p in pts]
    return np.array(xy), locx, locy, datumPt


def convert2DPointsTo3DCoordinateSystem(xy, e1, e2, origin):
    A = np.matrix([e1, e2])
    xyzPrime = np.matrix(xy) * A
    return np.squeeze(np.asarray(xyzPrime + origin))


def circleFit2DErr(allParams, xData, yData):
    pts = [np.linalg.norm([x - allParams[0], y - allParams[1]]) - allParams[2] for x, y in zip(xData, yData)]
    return (np.array(pts) ** 2).sum()


def fitCircle2D(pts, xGuess=0.0, yGuess=0.0, radiusGuess=1.0):
    X, Y = pts[:, 0], pts[:, 1]
    paramsToOptimize = np.array([xGuess, yGuess, radiusGuess])
    optimizedParams = optimize.fmin_powell(circleFit2DErr, paramsToOptimize, args=(X, Y))  # @UndefinedVariable
    xf = optimizedParams[0]
    yf = optimizedParams[1]
    rf = optimizedParams[2]
    return (xf, yf, rf)


def fitCircleRANSAC(x, y, tolerance, FRACTION_PTS_USE_FOR_CONVERGENCE,
                    MAX_ITERATIONS, EXCLUDE_INNERS=False, DEBUG=False):
    """

    :param x:
    :param y:
    :param tolerance:
    :param FRACTION_PTS_USE_FOR_CONVERGENCE:
    :param MAX_ITERATIONS:
    :param EXCLUDE_INNERS:
    :param DEBUG:
    :return:
    """
    count = 0
    nPts = len(x)
    Sbest = []
    while count < MAX_ITERATIONS:
        count += 1
        Si, Sx = [], []
        id0 = np.random.randint(nPts)
        id1 = np.random.randint(nPts)
        id2 = np.random.randint(nPts)
        if (id0 == id1) | (id1 == id2) | (id0 == id2):
            continue
        ma = (y[id1] - y[id0]) / (x[id1] - x[id0])
        mb = (y[id2] - y[id1]) / (x[id2] - x[id1])
        xc = (ma * mb * (y[id0] - y[id2]) + mb * (x[id0] + x[id1]) - ma * (x[id1] + x[id2])) / (2.0 * (mb - ma))
        yc = -1 * (1.0 / ma) * (xc - (x[id0] + x[id1]) / 2.0) + (y[id0] + y[id1]) / 2.0
        r = np.sqrt((xc - x[id0]) ** 2.0 + (yc - y[id0]) ** 2.0)
        for k1 in range(nPts):
            ri = np.sqrt((x[k1] - xc) ** 2.0 + (y[k1] - yc) ** 2.0)
            if EXCLUDE_INNERS:
                if ri < r:
                    continue
            dr = np.sqrt((ri - r) ** 2.0)
            if dr < tolerance:
                Si.append(k1)
            else:
                Sx.append(k1)
        if (len(Si) / nPts) > FRACTION_PTS_USE_FOR_CONVERGENCE:
            Sbest = Si
            xBest, yBest, rBest, countBest = xc, yc, r, count
            if DEBUG:
                print('Terminated on large Si')
            break
        if len(Si) > len(Sbest):
            Sbest = Si
            xBest, yBest, rBest, countBest = xc, yc, r, count
    xf, yf, rf = fitCircle2D(np.vstack((x[Sbest], y[Sbest])).T, xBest, yBest, rBest)
    return xf, yf, rf


def fitCircleRANSAC3D_xyz(xyz, tolerance, FRACTION_PTS_USE_FOR_CONVERGENCE,
                      MAX_ITERATIONS, EXCLUDE_INNERS=False, DEBUG=False):
    return fitCircleRANSAC3D(xyz[:,0],xyz[:,1],xyz[:,2], tolerance, FRACTION_PTS_USE_FOR_CONVERGENCE,
                      MAX_ITERATIONS, EXCLUDE_INNERS=False, DEBUG=False )


def fitCircleRANSAC3D(x, y, z, tolerance, FRACTION_PTS_USE_FOR_CONVERGENCE,
                      MAX_ITERATIONS, EXCLUDE_INNERS=False, DEBUG=False):
    """
    Rotate to plane of best fit, then 2D fit, rotate results back to 3D
        Return fitted point, R, norm
    :param x:
    :param y:
    :param z:
    :param tolerance:
    :param FRACTION_PTS_USE_FOR_CONVERGENCE:
    :param MAX_ITERATIONS:
    :param EXCLUDE_INNERS:
    :param DEBUG:
    :return:  xf, yf, zf, rf, normalVec
    """
    xy, e1, e2, origin = project3DPointsToPlanarCoordinateSystem(np.vstack((x, y, z)))
    xf, yf, rf = fitCircleRANSAC(xy[:, 0], xy[:, 1], tolerance, FRACTION_PTS_USE_FOR_CONVERGENCE,
                                 MAX_ITERATIONS, EXCLUDE_INNERS, DEBUG)
    xyzf = convert2DPointsTo3DCoordinateSystem([xf, yf], e1, e2, origin)
    return xyzf, rf, np.cross(e1, e2)


# ======================================================================================================================
#           GEOMETRY
# ======================================================================================================================
def buildCircle3D(X, N, R, nPts=50):
    """

    :param X: centre of circle
    :param N: normal of circle
    :param R: radius of circle
    :param nPts: number of points to place around circumference [50]
    :return: xyz of points on circumference of circle
    """
    ### Let W = (w0,w1,w2). Choose U = (u0,u1,u2) and V = (v0,v1,v2) using
    normalVec = N / np.linalg.norm(N)
    if (abs(normalVec[0]) >= abs(normalVec[1])):
        factor = 1.0 / np.sqrt(normalVec[0] * normalVec[0] + normalVec[2] * normalVec[2])
        u0 = -normalVec[2] * factor
        u1 = 0.0
        u2 = normalVec[0] * factor
    else:
        factor = 1.0 / np.sqrt(normalVec[1] * normalVec[1] + normalVec[2] * normalVec[2])
        u0 = 0.0
        u1 = normalVec[2] * factor
        u2 = -normalVec[1] * factor
    u = np.array([u0, u1, u2])
    v = np.cross(normalVec, u)
    ### X(t) = C + (r*cos(t))*U + (r*sin(t))*V ##
    theta = 0
    dtheta = 2 * np.pi / nPts
    fc_circle = np.zeros((3, nPts))
    for k in range(nPts):
        theta = theta + dtheta
        fc_circle[:, k] = (X + (R * np.cos(theta)) * u + (R * np.sin(theta)) * v).T

    return fc_circle.T


def fitPlaneToPointCloud_RANSAC(pts, planeSearchDist_abs, planeFractionToInclude, max_iterations=1000, VERBOSE=False):
    """
    Fits a plane to a 3D point cloud using RANSAC.
        Choose random point
        Take next two closest points - calc plane
        Test number of points within planeSearchDist_abs 
            If > planeFractionToInclude
                test RMSE vs best

    Parameters:
    - pts: A numpy array of shape (N, 3) representing the 3D point cloud.
    - planeSearchDist_abs: The absolute distance to search for points for plane RMSE calc.
    - planePercentageToInclude: The fraction of points required to be part of plane.
    - max_iterations: The maximum number of iterations for the RANSAC algorithm (default=1000).
    - random_state: Random state for reproducibility (default=None).

    Returns:
    - plane_normal: A numpy array representing the normal vector of the fitted plane.
    - plane_center: A numpy array representing a point on the fitted plane.
    """
    best_plane_normal = None
    best_plane_center = None
    best_num_inliers = 0

    total_points = pts.shape[0]
    target_inliers = int(total_points * planeFractionToInclude)
    rndIDs = list(range(total_points))
    np.random.shuffle(rndIDs)
    if VERBOSE:
        print(f"Have {total_points} total_points. Target inliers={target_inliers}")
    for k1 in range(min(total_points, max_iterations)):
        # Randomly sample point - get closest 2 neighbours
        rndID = rndIDs[k1]
        idists = distPointPoints(pts[rndID], pts)
        sampleIDs = np.argsort(idists)[[1,3,6]]
        samplePts = pts[sampleIDs]

        # Calculate plane parameters using these points
        v1 = samplePts[1] - samplePts[0]
        v2 = samplePts[2] - samplePts[0]
        plane_normal = np.cross(v1, v2)
        plane_normal /= np.linalg.norm(plane_normal)
        plane_center = np.mean(samplePts, axis=0)

        # Calculate distances from points to plane
        distances = np.abs(np.dot(pts - plane_center, plane_normal))

        # Count inliers
        inlier_mask = distances < planeSearchDist_abs
        num_inliers = np.sum(inlier_mask)
        # if k1 > 0:
        #     if num_inliers > 5:
        #         # Add a penalty if all pts at boundary
        #         selectedPts = pts[inlier_mask,:]
        #         distFromCenter = min(distPointPoints(np.mean(selectedPts, axis=0), selectedPts))
        #         if distFromCenter > planeSearchDist_abs:
        #             if DEBUG: 
        #                 print(f"Dist from center {distFromCenter:0.4f} > searchDist {planeSearchDist_abs} - continue")
        #             continue

        # Update best model if necessary
        if (best_plane_normal is None) or ((num_inliers >= target_inliers) and (num_inliers > best_num_inliers)):
            if VERBOSE:
                print(f"    Update best num_inliers = {num_inliers} ({num_inliers/total_points*100:0.2f}%). best_plane_normal={plane_normal}")
            best_plane_normal = plane_normal
            best_plane_center = plane_center
            best_num_inliers = num_inliers
    if VERBOSE:
        print(f"It:{k1} - best plane norm = {best_plane_normal}")
    return best_plane_normal, best_plane_center


# ======================================================================================================================
# def findCylinderAxis(point_cloud):
#     """
#     Finds the main axis of a cylindrical point cloud.
    
#     :param point_cloud: Nx3 numpy array where N is the number of points and each row is (x, y, z).
#     :return: A unit vector defining the main axis of the cylinder.
#     """
#     from sklearn.decomposition import PCA
#     point_cloud_centered = point_cloud - np.mean(point_cloud, axis=0)
#     pca = PCA(n_components=3)
#     pca.fit(point_cloud_centered)
#     main_axis = pca.components_[0]
#     return main_axis / np.linalg.norm(main_axis)


# ======================================================================================================================
# ======================================================================================================================

def deg2rad(deg):
    return np.pi * deg / 180.0


def rad2deg(rad):
    return 180.0 * rad / np.pi


def rotateArray(velArray, rotationMatrix):
    vel = np.array(velArray)
    dims = vel.shape
    if dims[-1] != 3:
        raise AttributeError('ERROR ARRAY IS WRONG SIZE')
    pts = np.prod(dims[:-1])
    newDims = (pts, 3)
    vel = np.reshape(vel, newDims)
    velM = np.matrix(vel)
    velM = np.transpose(velM)
    velMR = np.zeros((pts, 3))
    for i in range(pts):
        velMR[i, :] = np.squeeze(rotationMatrix * velM[:, i])
    velOut = np.reshape(velMR, dims)
    return velOut


def rotationMatrixFromThreeAngles(xTheta, yTheta, zTheta):
    X = np.array([[1, 0, 0], [0, np.cos(xTheta), -np.sin(xTheta)], [0, np.sin(xTheta), np.cos(xTheta)]])
    Y = np.array([[np.cos(yTheta), 0, np.sin(yTheta)], [0, 1, 0], [-np.sin(yTheta), 0, np.cos(yTheta)]])
    Z = np.array([[np.cos(zTheta), -np.sin(zTheta), 0], [np.sin(zTheta), np.cos(zTheta), 0], [0, 0, 1]])
    return np.dot(np.dot(Z, Y), X)


def getClosestInSortedList(listIn, ref, INCREASEING=True):
    for k1 in range(0, len(listIn)):
        if INCREASEING:
            if listIn[k1] >= ref:
                return k1
        else:
            if listIn[k1] < ref:
                return k1
    return len(listIn) - 1


def getIdOfClosestFloat(listIn, ref):
    dd = np.array(listIn) - np.array(ref)
    return np.argmin(abs(dd))


def polar2Cart(r,theta):
    z = polar2z(r, theta)
    return np.real(z), np.imag(z)


def polar2z(r,theta):
    return r * np.exp( 1j * theta )


def z2Polar(z):
    return ( abs(z), np.angle(z) )


def cart2Polar(x,y):
    z = x + 1j * y
    return z2Polar(z)


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    VM = np.linalg.norm(vector)
    if VM < 0.0000000000001:
        return np.array([0.0, 0.0, 0.0])
    return vector / VM


def vecFromPtToLine(pt, ptOnLine, lineNorm):
    return (ptOnLine - pt) - (np.dot(ptOnLine - pt, lineNorm) * lineNorm)


def fcdot(u, v):
    """ dot product of two lists of vecs"""
    u, v = __forcePts_nx3(u), __forcePts_nx3(v)
    return np.array([np.dot(i, j) for i, j in zip(u, v)])


def cosineDifferenceBetweenTwoMats(mA, mB):
    dims = mA.shape
    matDiff = np.zeros(dims[:-1])
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                matDiff[i, j, k] = angleBetween2Vec(mA[i, j, k], mB[i, j, k])

    return matDiff


def getVectorComponentAlongRefVec(velVec, refVec):
    """ Returns vec parallel to refVec"""
    refVec_U = refVec / np.linalg.norm(refVec)
    return np.dot(velVec, refVec_U) * refVec_U


def getVectorComponentAlongRefVec_Mag(velVec, refVec):
    """ Returns magnitude (signed) of vec parallel to refVec"""
    refVec_U = refVec / np.linalg.norm(refVec)
    llv = np.dot(velVec, refVec_U) * refVec_U
    llvM = vectorMagnitudes(llv)
    if areVecsConsistent(llv, refVec):
        return  llvM
    else:
        return  -1*llvM


def getVectorComponentNormalToRefVec(velVec, refVec):
    """ Returns vec component in plane normal to refVec"""
    vel_t = getVectorComponentAlongRefVec(velVec, refVec)
    return velVec - vel_t


def closeCurve(xyz):
    pts = np.array(xyz)
    pts = np.vstack((pts, pts[0]))
    return pts


def splinePoints(xyz, nSplinePts, periodic=0, RETURN_NUMPY=False, smooth=0, u=None, weights=None, derivitive=0):
    """
     returns list, shape (3, n), unless ask for numpy then transpose
    """
    pts = np.asarray(xyz)

    if periodic>0:
        smooth = 0.0
        pts = np.vstack((pts, pts[0]))
        if weights is not None:
            weights = np.hstack((weights, weights[-1]))
    pts = pts.transpose()
    tck, u = interpolate.splprep(pts, u=u, s=smooth, per=periodic, w=weights)
    uu = np.linspace(u.min(), u.max(), nSplinePts)
    newPts = interpolate.splev(uu, tck, der=derivitive)
    if RETURN_NUMPY:
        return np.array(newPts).T
    return newPts


def splinePoints_RansacSmooth(xyz, periodic=0, RETURN_NUMPY=False):
    """
     returns list, shape (3, n), unless ask for numpy then transpose
    """
    pts = np.asarray(xyz)

    if periodic>0:
        smooth = 0.0
        pts = np.vstack((pts, pts[0]))
    pts = pts.transpose()
    tck, u = interpolate.splprep(pts, per=periodic)
    uu = np.linspace(u.min(), u.max(), len(xyz))
    newPts = interpolate.splev(uu, tck, der=1)
    print(np.sum(np.sqrt(np.power(newPts, 2.0))))



def splineFunction(x, y, kind):
    return interpolate.interp1d(x, y, bounds_error=False, kind=kind)


def splineXY(x, y, nPts, kind='linear', per=False):
    """ Input : x, y, numPts
        Output : X, Y
    """
    if per:
        xp = np.hstack((np.array(x), x[-1]+(x[1]-x[0])))
        y = np.hstack((np.array(y), y[0]))
        f = splineFunction(xp, y, kind)
    else:
        f = splineFunction(x, y, kind)
    xx = np.linspace(min(x), max(x), nPts)
    yy = f(xx)
    return xx, yy


def splineCurve(x, y, nPts, interpolation_method='cubic'):
    """Spline is 2D (i.e x not always increasing)

    Args:
        x (np.array): x array
        y (np.array): y array
        interpolation_methods (str, optional): of 'slinear', 'quadratic', 'cubic']. Defaults to 'cubic'.
    """
    points = np.vstack([x,y]).T
    distance = np.cumsum( np.sqrt(np.sum( np.diff(points, axis=0)**2, axis=1 )) )
    distance = np.insert(distance, 0, 0)/distance[-1]
    alpha = np.linspace(0, 1, nPts)
    interpolator = interpolate.interp1d(distance, points, bounds_error=False, kind=interpolation_method, axis=0)
    res = interpolator(alpha)
    return res.T


def getMaxsMinsInflections(X):
    """
    Simple extrema finder
    :param X: 1D array
    :return: linst of maxima, list of minima, lint of inflections
    """
    from scipy.signal import argrelextrema
    gg = np.gradient(X)
    return argrelextrema(X, np.greater)[0], \
           argrelextrema(X, np.less)[0], \
           np.hstack((argrelextrema(gg, np.greater)[0],argrelextrema(gg, np.less)[0]))


def sigmoidFunction(value, center=0.0, gradient=1.0):
    """
    calculate sigmoid function of input value (np array)
    center is what to adjust input by so zero centered
    gradient is used to adjust slope of sigmoid -
        (adjusted) values above this number will have output > 0.72
    """
    valueT = value - center
    output = 1.0 / (1.0 + np.exp(-valueT / gradient))
    return output


def extractContinuousSegFromPeriodic(xx, IDstart, IDend, TIME=False):
    """
    Take a sub section from an array, assuming periodic (to deal with subsection going beyond bounds)
    """
    N = len(xx)
    if TIME:
        delta = np.mean(np.diff(xx))
        tN = xx[-1]
        xx3 = np.hstack((xx, xx+delta+tN, xx+(2.0*delta)+(2.0*tN)))
    else:
        xx3 = np.hstack((xx,xx,xx))
    IDstart = IDstart + N
    IDend = IDend + N
    xxOut = xx3[IDstart:IDend]
    if TIME:
        return xxOut - tN - delta
    return xxOut


def fitGaussianToData(xx, yy):
    popt, _ = optimize.curve_fit(gaussianFunction, xx, yy)
    center, width, height = popt
    # 'x': xSub, 'y': ftk.gaussianFunction(xSub, *popt)
    return center, width, height


def gaussianFunction(value, center=0.0, width=1.0, height=1.0):
    """
    calculate gaussian function of input value (np array)
    center is what to adjust input by so zero centered
    width is standard dev of bell curve
    height is height of peak
    """
    valueT = value - center
    output = height * (np.exp(-(valueT ** 2.0) / (2.0 * width ** 2.0)))
    return output


def calculate_signed_area_2d(points_2d):
    # Use the shoelace formula to calculate the signed area of the 2D points
    n = len(points_2d)
    area = 0.0
    for i in range(n):
        x1, y1 = points_2d[i]
        x2, y2 = points_2d[(i + 1) % n]
        area += (x1 * y2 - y1 * x2)
    return area / 2.0


def isClosedPolygonClockwise(xyzIn, refVec):
    # Calculate the centroid to use as origin
    xyP = project3DPointsToPlanarCoordinateSystem(xyzIn, refVec)[0]
    # Calculate the signed area
    signed_area = calculate_signed_area_2d(xyP)
    # If the signed area is negative, it's clockwise; otherwise, it's counterclockwise
    return signed_area < 0


def ensureClosedPolyIsClockwise(xzyIn, refVec):
    if isClosedPolygonClockwise(xzyIn, refVec):
        return xzyIn
    return xzyIn[::-1]

def setFirstPtOfPolygon(xyzIn, refVec):
    """
    Reorder the points of a polygon so that the first point is closest to the refVec (e.g. '12 o'clock' position).

    This function assumes the polygon is planar and reorders the points so that the first point
    is the one closest to the end of a vector starting from the polygon's center point
    and pointing in the direction of the reference vector.

    Parameters:
    xyzIn (array-like): Input points of the polygon.
    refVec (array-like): Reference vector indicating the '12 o'clock' direction.

    Returns:
    numpy.ndarray: Reordered points of the polygon.
    """
    pts = np.array(xyzIn)
    refVec = np.array(refVec)
    nPts = len(pts)
    cp = getPolygonCenterPoint(xyzIn)
    meanDiameter = getPolygonMeanDiameter(xyzIn)
    vectorEnd = cp + meanDiameter / 1.0 * refVec
    closestPtIndex = 0
    ptToLineDist = distTwoPoints(vectorEnd, pts[0])
    for i in range(1, nPts, 1):
        iDist = distTwoPoints(vectorEnd, pts[i])
        if (iDist < ptToLineDist):
            closestPtIndex, ptToLineDist = i, iDist
    return reorderPointsStatingAti(pts, closestPtIndex)


def reorderPointsStartClosestToX(pts, X):
    ID = getIDOfClosestPoint(X, pts)
    return reorderPointsStatingAti(pts, ID)


def reorderPointsStatingAti(pts, i):
    pts = __forcePts_nx3(pts)
    ptsOut = np.vstack((pts[i:][:], pts[:i][:]))
    return ptsOut


def sortPointsByClosest_RETURNIDs(xyz, refX0):
    """ Grab closest to refX0, grab next closest, keep going in that direction
     RETURN IDs """
    X = [i for i in xyz]
    X2 = [i for i in xyz]
    IDs = [getIDOfClosestPoint(refX0, X)]
    X2.pop(IDs[0])
    while True:
        try:
            nextID = getIdOfPointClosestToX(X[IDs[-1]], X2)
            IDs.append(X.index(X2[nextID]))
            X2.pop(nextID)
        except ValueError:
            break
    return IDs


def sortPointsByClosest(xyz):
    """ Grab first, grab closest, keep going in that direction """
    X = [i for i in xyz]
    ptsOut = [X.pop(0)]
    while True:
        try:
            nextID = getIdOfPointClosestToX(ptsOut[-1], X)
            ptsOut.append(X.pop(nextID))
        except ValueError:
            break
    return np.array(ptsOut)


def cumulativeDistanceAlongLine(xyzPts):
    """ Return array same len as input with sum of dists
        [0.0, dist-0to1, dist-0to1to2, ...] """
    if len(xyzPts[0, :]) == 2:
        dists = [np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) for
                 p2, p1 in zip(xyzPts[:-1], xyzPts[1:])]
    else:
        xyzPts = __forcePts_nx3(xyzPts)
        dists = [np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2) for
                 p2, p1 in zip(xyzPts[:-1], xyzPts[1:])]
    dists.insert(0, 0.0)
    return np.cumsum(dists)


def getIdOfPointClosestToX(X, xyz):
    diffs = distPointPoints(X, xyz)
    return np.argmin(diffs)


def getPolygonMeanRadius(xyzIn, EXCLUDE_CENTER=True):
    pts = np.array(xyzIn)
    nPts = len(pts)
    cp = np.mean(pts, 0)
    allR = []
    for i in range(nPts):
        allR.append(distPointPoints(cp, pts[i]))
    if EXCLUDE_CENTER:
        allR = sorted(allR)
        return np.mean(allR[1:])
    else:
        return np.mean(allR)


def getPolygonMeanDiameter(xyzIn):
    return getPolygonMeanRadius(xyzIn) * 2.0


def getPolygonCenterPoint(xyzIn):
    pts = np.array(xyzIn)
    return np.mean(pts, 0)


def lineMagnitude(lineStartxyz, lineEndxyz):
    if len(lineStartxyz) == 3:
        lineMagnitude = np.sqrt(np.power((lineEndxyz[0] - lineStartxyz[0]), 2) +
                                np.power((lineEndxyz[1] - lineStartxyz[1]), 2) +
                                np.power((lineEndxyz[2] - lineStartxyz[2]), 2))
    else:
        lineMagnitude = np.sqrt(np.power((lineEndxyz[0] - lineStartxyz[0]), 2) +
                                np.power((lineEndxyz[1] - lineStartxyz[1]), 2))
    return lineMagnitude


def distancePointToLineSegPerpendicular(lineStartxyz, lineEndxyz, ptxyz):
    return np.linalg.norm(np.cross(lineEndxyz-lineStartxyz, lineStartxyz-ptxyz))/np.linalg.norm(lineEndxyz-lineStartxyz)


def ndarrayToListOfTuple3(ndArrayIn):
    xyzOut = []
    for ndarray3 in ndArrayIn:
        xyzOut.append(tuple(ndarray3))

    return xyzOut


def diff(myList):
    a = np.array(myList[:-1])
    b = np.array(myList[1:])
    mydiff = b - a
    return mydiff


def circleFit2DErr(allParams, xData, yData):
    """ Fit a circle to points
    """
    # pts = [(np.linalg.norm([x-allParams[0],y-allParams[1]])-allParams[2])*w for x,y,w in zip(xData,yData,allParams[3:])]
    pts = [np.linalg.norm([x - allParams[0], y - allParams[1]]) - allParams[2] for x, y in zip(xData, yData)]
    return (np.array(pts) ** 2).sum()

def distanceToPlane(p0, n, x):
    # Plane through point p0, with normal n. Point x
    return np.dot(np.array(n), np.array(x) - np.array(p0))

def residualPlane(parameters, X, Y, Z):
    px, py, pz, theta, phi = parameters
    nx, ny, nz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
    distances = [distanceToPlane([px, py, pz], [nx, ny, nz], [x, y, z]) for x, y, z in zip(X, Y, Z)]
    return distances

def residualsCircle(parameters, sArr, rArr, point, X, Y, Z):
    r, s, Ri = parameters
    planePointArr = s * sArr + r * rArr + np.array(point)
    distance = [np.linalg.norm(planePointArr - np.array([x, y, z])) for x, y, z in zip(X, Y, Z)]
    res = [(Ri - dist) for dist in distance]
    return res


def icp(sourcePts, targetPts, max_iterations=100, tolerance=1e-6):
    """
    Iterative Closest Point (ICP) algorithm for point set registration.

    Parameters:
    - X: A numpy array of shape (N, 3) representing the source set of 3D points.
    - Y: A numpy array of shape (M, 3) representing the target set of 3D points.
    - max_iterations: Maximum number of iterations for the algorithm (default=100).
    - tolerance: Convergence criterion based on the change in error (default=1e-6).

    Returns:
    - R_best: A 3x3 numpy array representing the best rotation matrix.
    - t_best: A 1x3 numpy array representing the best translation vector.
    """
    R_best = np.eye(3)  # Initial best rotation matrix (identity)
    t_best = np.zeros(3)  # Initial best translation vector
    min_error = np.inf  # Initial minimum error
    sourcePtsBest = None
    rndIt_every = int(max_iterations/5.0)
    tree = cKDTree(targetPts)
    for k1 in range(max_iterations):
        distances, indices = tree.query(sourcePts)
        Y_matched = targetPts[indices]
        centroid_X = np.mean(sourcePts, axis=0)
        centroid_Y = np.mean(Y_matched, axis=0)

        X_centered = sourcePts - centroid_X
        Y_centered = Y_matched - centroid_Y

        covariance_matrix = np.dot(Y_centered.T, X_centered)
        U, _, Vt = np.linalg.svd(covariance_matrix)

        R_new = np.dot(U, Vt)
        t_new = centroid_Y - np.dot(R_new, centroid_X)

        sourcePts = np.dot(sourcePts, R_new.T) + t_new

        total_error = np.sum(distances)

        if total_error < min_error:
            min_error = total_error
            R_best = np.dot(R_new, R_best)
            t_best = np.dot(R_new, t_best) + t_new
            sourcePtsBest = sourcePts

        if total_error < tolerance:
            break

    return R_best, t_best, sourcePtsBest

def fitPlane3DOptimize(pts):
    x,y,z = pts[:,0], pts[:,1], pts[:,2]
    estPlane = np.array([np.mean(x), np.mean(y), np.mean(z), 0, 0])
    bestFitValues = optimize.leastsq(residualPlane, estPlane, args=(x, y, z))[0]
    xF, yF, zF, tF, pF = bestFitValues
    point = np.array([xF, yF, zF])
    normal = np.array([np.sin(tF) * np.cos(pF), np.sin(tF) * np.sin(pF), np.cos(tF)])
    return normal, point


def fitCircle3D(x, y, z, xm, ym, zm, rm):
    """
    Fit a circle to 3D points.

    Parameters:
    - x, y, z: Arrays of x, y, and z coordinates of the points.
    - xm, ym, zm: Coordinates of the center of the circle.
    - rm: Radius of the circle.

    Returns:
    - centerPointArr: Coordinates of the center of the circle.
    - RiF: Radius of the circle.
    - normal: Normal vector of the plane containing the circle.
    """
    estPlane = np.array([xm, ym, zm, 0, 0])
    # print residualsPlane(estPlane, pts)
    bestFitValues = optimize.leastsq(residualPlane, estPlane, args=(x, y, z))[0]
    xF, yF, zF, tF, pF = bestFitValues

    point = [xF, yF, zF]
    normal = [np.sin(tF) * np.cos(pF), np.sin(tF) * np.sin(pF), np.cos(tF)]

    # Fitting a circle inside the plane
    # creating two inplane vectors
    sArr = np.cross(np.array([1, 0, 0]), np.array(normal))  # assuming that normal not parallel x!
    sArr = sArr / np.linalg.norm(sArr)
    rArr = np.cross(sArr, np.array(normal))
    rArr = rArr / np.linalg.norm(rArr)  # should be normalized already, but anyhow

    estimateCircle = np.array([0.0, 0.0, rm])  # px,py,pz and zeta, phi
    bestCircleFitValues = optimize.leastsq(residualsCircle, estimateCircle, args=(sArr, rArr, point, x, y, z))[0]

    rF, sF, RiF = bestCircleFitValues
    centerPointArr = sF * sArr + rF * rArr + np.array(point)
    # synthetic=[list(centerPointArr+ RiF*np.cos(phi)*rArr+RiF*np.sin(phi)*sArr) for phi in np.linspace(0, 2*np.pi,50)]
    # [cxTupel,cyTupel,czTupel]=[ x for x in zip(*synthetic)]
    return (centerPointArr, RiF, np.cross(sArr, rArr))


def lagBetweenTwoCurves(y1: np.array, y2: np.array, timeArray: np.array = None):
    """
    Calculate the lag (delay) between two similar time series curves.

    This function uses cross-correlation to determine the time delay between two signals.

    Parameters:
    - y1 (np.array): First time series.
    - y2 (np.array): Second time series.
    - timeArray (np.array, optional): Array of time points corresponding to y1 and y2. 
      If None, a normalized time array from -0.5 to 0.5 is used. Default is None.

    Returns:
    - float: The time delay between the two signals. A positive value indicates 
             that y2 lags behind y1, while a negative value indicates that y1 lags behind y2.

    Note:
    - The two input arrays (y1 and y2) must have the same length.
    - If timeArray is provided, it must have the same length as y1 and y2.
    """
    n = len(y1)
    corr = np.correlate(y2, y1, mode='same') / np.sqrt(np.correlate(y1, y1, mode='same')[int(n/2)] * np.correlate(y2, y2, mode='same')[int(n/2)])
    if timeArray is None:
        delay_arr = np.linspace(-0.5, 0.5, n)
    else:
        delay_arr = np.roll(timeArray, int(n/2))
    delay = delay_arr[np.argmax(corr)]
    return delay


def calculatePlaneThreePoints(p0, p1, p2):
    """ Plane from three points (v0(p0 to p1) and v1(p0 to p2) -> cross == norm, p2 for D)
        Return [A,B,C,D]
    """
    v0, v1 = np.array(p1) - np.array(p0), np.array(p2) - np.array(p0)
    n0 = np.cross(v0, v1)
    n0 = n0 / np.linalg.norm(n0)
    return getPlaneConstantsFromPointAndVector(p2, n0)


def getPlaneConstantsFromPointAndVector(pt, vector):
    D = -pt[0] * vector[0] - pt[1] * vector[1] - pt[2] * vector[2]
    plane = np.hstack((vector, D))
    return plane


def calculateDerivativeOnLine_backwardDiff(pim1, pi, dt):
    """ Calculate the derivative of a line using backward difference. 
    """
    dr_dt = [(m - n) / dt for m, n in zip(pim1, pi)]
    return dr_dt


def calculateSecondDerivativeOnLine(pim1, pi, pip1, dt):
    d2r_dt2 = [(p - 2.0 * n + m) / dt ** 2 for m, n, p in zip(pim1, pi, pip1)]
    return d2r_dt2


def __calcTNB(dr_dt, d2r_dt2):
    T = dr_dt / np.linalg.norm(dr_dt)
    N = np.cross(dr_dt, np.cross(d2r_dt2, dr_dt)) / \
        (np.linalg.norm(dr_dt) * np.linalg.norm(np.cross(d2r_dt2, dr_dt)))
    B = np.cross(T, N)
    return (T, N, B)


def calculateCurvature3Pts(pim1, pi, pip1, dx):
    dr_dt = calculateDerivativeOnLine_backwardDiff(pim1, pi, dx)
    d2r_dt2 = calculateSecondDerivativeOnLine(pim1, pi, pip1, dx)
    num = np.linalg.norm(np.cross(dr_dt, d2r_dt2))
    denom = np.power(np.linalg.norm(dr_dt), 3)
    k = num / denom
    TNB = __calcTNB(dr_dt, d2r_dt2)
    return (k, TNB)


def calculateCurvature_D(gf: np.array, ggf: np.array):
    num = [np.linalg.norm(np.cross(i, j)) for i, j in zip(gf, ggf)]
    denom = [np.power(np.linalg.norm(i), 3) for i in gf]
    k = np.array(num) / np.array(denom)
    TNB = [__calcTNB(i, j) for i, j in zip(gf, ggf)]
    return (k, TNB)


def setVectorDirection(vecIn, oo, pointMorePositive):
    """ Will ensure vector at point oo is pointing towards 'pointMorePositive' else flip"""
    oo, vecIn = np.asarray(oo), np.asarray(vecIn)
    dp, dm = distTwoPoints(oo + vecIn, pointMorePositive), distTwoPoints(oo - vecIn, pointMorePositive)
    if dp > dm:
        return -1 * vecIn
    return vecIn


def buildRotationMatrix(vec, theta_rad):
    vec = vec / np.linalg.norm(vec)
    RotM = [[np.cos(theta_rad) + vec[0] ** 2 * (1.0 - np.cos(theta_rad)), \
             vec[0] * vec[1] * (1.0 - np.cos(theta_rad)) - vec[2] * np.sin(theta_rad), \
             vec[1] * np.sin(theta_rad) + vec[0] * vec[2] * (1.0 - np.cos(theta_rad))], \
            [vec[2] * np.sin(theta_rad) + vec[0] * vec[1] * (1.0 - np.cos(theta_rad)), \
             np.cos(theta_rad) + vec[1] ** 2 * (1.0 - np.cos(theta_rad)), \
             -vec[0] * np.sin(theta_rad) + vec[1] * vec[2] * (1.0 - np.cos(theta_rad))], \
            [-vec[1] * np.sin(theta_rad) + vec[0] * vec[2] * (1.0 - np.cos(theta_rad)), \
             vec[0] * np.sin(theta_rad) + vec[1] * vec[2] * (1.0 - np.cos(theta_rad)), \
             np.cos(theta_rad) + vec[2] ** 2 * (1.0 - np.cos(theta_rad))]]
    return RotM


def adjustPointsCenterOfMassToOrigin(pts):
    pts = __forcePts_nx3(pts)
    centerOfMass = np.mean(pts, 0)
    return pts - centerOfMass


def areVecsConsistent(vecA, vecB):
    vecA = np.array(vecA)
    vecB = np.array(vecB)
    nA = np.linalg.norm(vecA)
    nB = np.linalg.norm(vecB)
    if nA > 0:
        vecA = vecA / nA
    if nB > 0:
        vecB = vecB / nB
    if np.linalg.norm(vecB - vecA) > np.linalg.norm(vecB - -1.0 * vecA):
        return False
    return True


def setVecAConsitentWithVecB(vecA, vecB):
    """
     Make vec dir consistant with poly order
    """
    if not areVecsConsistent(vecA, vecB):
        vecA = -1.0 * vecA
    return vecA


def buildConvexHUll3D(xyz, nPts=25, planeABCD=None, TO_SPLINE=True):
    try:
        len(planeABCD)
    except TypeError:
        planeABCD = fitPlaneToPoints(xyz)
    xy, e1, e2, origin = project3DPointsToPlanarCoordinateSystem(xyz, planeABCD[:3])
    xyL = [tuple(i) for i in xy]
    chxy = convexHull(xyL)
    if TO_SPLINE:
        chxys = np.array(splinePoints(chxy, nPts, periodic=1)).T
        # chxys = splinePoints(np.array(chxy).T, nPts, periodic=1, RETURN_NUMPY=True)
    else:
        chxys = np.array(chxy)
    chxyz = convert2DPointsTo3DCoordinateSystem(chxys, e1, e2, origin)
    return np.asarray(chxyz)


def orderPointsConvexHull_IDs(xyz):
    planeABCD = fitPlaneToPoints(xyz)
    xy, e1, e2, origin = project3DPointsToPlanarCoordinateSystem(xyz, planeABCD[:3])
    xyL = [tuple(i) for i in xy]
    chxy = convexHull(xyL)
    IDs = []
    for k1 in range(len(chxy)):
        dd = distPointPoints(chxy[k1], xy)
        iID = np.argmin(dd)
        IDs.append(iID)
    return IDs


def orderPointsConvexHull(xyz):
    IDs = orderPointsConvexHull_IDs(xyz)
    pts_out = np.array([xyz[i] for i in IDs])
    return pts_out


def groupContinuousLinesByTol(ptsIn, tol):
    """ pts is N x 3 array of pts forming continuous lines (at least one)
        separated by gaps of 'tol'
        Returns list of pts separated
    """
    pts = ptsIn.copy()
    listOut = []
    pi = pts[0, :]
    currPts = [pi]
    pts = np.delete(pts, 0, 0)
    while len(pts) > 0:
        dd = distPointPoints(pi, pts)
        nextId = np.argmin(dd)
        if dd[nextId] < tol:
            pi = pts[nextId, :]
            currPts.append(pi)
            pts = np.delete(pts, nextId, 0)
        else:
            listOut.append(np.array(currPts))
            pi = pts[nextId, :]
            currPts = [pi]
            pts = np.delete(pts, nextId, 0)
    listOut.append(np.array(currPts))
    return listOut


def buildContinuousLineByClosestPt(ptsIn):
    """ pts is N x 3 array of pts
        returns points ordered by proximity
    """
    pts = ptsIn.copy()
    pi = pts[0, :]
    currPts = [pi]
    pts = np.delete(pts, 0, 0)
    while len(pts) > 0:
        dd = distPointPoints(pi, pts)
        nextId = np.argmin(dd)
        pi = pts[nextId, :]
        currPts.append(pi)
        pts = np.delete(pts, nextId, 0)
    return np.array(currPts)


def accumulatedAverage(arrayIn):
    """
        Calc array that is average from start to i of input
    """
    aOut = [np.mean(arrayIn[:i + 1]) for i in range(len(arrayIn))]
    return np.array(aOut)


def interpolateNANsFromSurroundingValues_linear(array):
    """ This is linear temporal interpolation
    """
    mask = np.isnan(array)
    array[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), array[~mask])
    return array


def interpolateNANsFromSurroundingValues_cubic(nparray):
    arrayTF = np.isnan(nparray)
    if sum(arrayTF) == 0:
        return nparray
    dims = nparray.shape
    gridX, gridY = np.mgrid[0:dims[0], 0:dims[1]]
    pp = [[i, j] for i, j in zip(gridX.flatten(), gridY.flatten()) if not arrayTF[i, j]]
    values = [nparray[i, j] for i, j in zip(gridX.flatten(), gridY.flatten()) if not arrayTF[i, j]]
    return interpolate.griddata(pp, values, (gridX, gridY), method='cubic')


# ============ LINE SEG PIERCE TRIANGLE ========================================
def doesLineSegPierceTriangle(lineP0, lineP1, triP0, triP1, triP2):
    if doesLinePierceTriangle(lineP0, lineP1, triP0, triP1, triP2):
        s4 = pluckerSideOperator([triP1, triP2], [triP0, lineP1])
        s5 = pluckerSideOperator([triP1, triP2], [lineP0, triP0])

        if (s4 < 0) & (s5 < 0):
            return True
        elif (s4 > 0) & (s5 > 0):
            return True
    return False


def doesLinePierceTriangle(lineP0, lineP1, triP0, triP1, triP2):
    s1 = pluckerSideOperator([lineP0, lineP1], [triP0, triP1])
    s3 = pluckerSideOperator([lineP0, lineP1], [triP1, triP2])
    s2 = pluckerSideOperator([lineP0, lineP1], [triP2, triP0])
    if (s1 < 0) & (s2 < 0) & (s3 < 0):
        return True
    elif (s1 > 0) & (s2 > 0) & (s3 > 0):
        return True

    return False


def pluckerSideOperator(line0, line1):
    a = pluckerLine(line0)
    b = pluckerLine(line1)
    value = a[0] * b[4] + a[1] * b[5] + a[2] * b[3] + a[3] * b[2] + a[4] * b[0] + a[5] * b[1]
    return value

def pluckerLine(line):
    # line is 2 x 3
    L0 = line[0][0] * line[1][1] - line[1][0] * line[0][1]
    L1 = line[0][0] * line[1][2] - line[1][0] * line[0][2]
    L2 = line[0][0] - line[1][0]
    L3 = line[0][1] * line[1][2] - line[1][1] * line[0][2]
    L4 = line[0][2] - line[1][2]
    L5 = line[1][1] - line[0][1]
    return [L0, L1, L2, L3, L4, L5]


def doesVectorPierceAnyTriangle(vS, vE, triPolyData):
    nTris = triPolyData.GetNumberOfCells()
    for k2 in range(nTris):
        t0 = triPolyData.GetPoint(triPolyData.GetCell(k2).GetPointIds().GetId(0))
        t1 = triPolyData.GetPoint(triPolyData.GetCell(k2).GetPointIds().GetId(1))
        t2 = triPolyData.GetPoint(triPolyData.GetCell(k2).GetPointIds().GetId(2))

        if doesLineSegPierceTriangle(vS, vE, t0, t1, t2):
            return k2
    return None


# ==========================================================================
# ==========================================================================
def calculateBSA(height_cm, weight_kg, METHOD='DuBois'):
    if METHOD == 'DuBois':
        BSA = 0.007184 * np.power(height_cm, 0.725) * np.power(weight_kg, 0.425)
    else:
        raise ValueError('Method unknown. Use one of: {DuBois}')
    return BSA


# ==========================================================================
# RANDOM CLASSES
# ==========================================================================
def interpolateNANsFromSurroundingValues_linear(array):
    """ This is linear temporal interpolation
    """
    mask = np.isnan(array)
    array[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), array[~mask])
    return array


######################################################################
# CONVEX HULL
######################################################################
"""
Calculate the convex hull of a set of n 2D-points in O(n log n) time.  
Taken from Berg et al., Computational Geometry, Springer-Verlag, 1997.
Dinu C. Gherman
"""
def _myDet(p, q, r):
    """Calc. determinant of a special matrix with three 2D points.
    The sign, "-" or "+", determines the side, right or left,
    respectivly, on which the point r lies, when measured against
    a directed vector from p to q.
    """
    # We use Sarrus' Rule to calculate the determinant.
    # (could also use the Numeric package...)
    sum1 = q[0] * r[1] + p[0] * q[1] + r[0] * p[1]
    sum2 = q[0] * p[1] + r[0] * q[1] + p[0] * r[1]
    return sum1 - sum2


def _isRightTurn(pqr):
    """Do the vectors pq:qr form a right turn, or not?"""
    (p, q, r) = pqr
    assert p != q and q != r and p != r
    if _myDet(p, q, r) < 0:
        return 1
    else:
        return 0


def _isPointInPolygon(r, P):
    """Is point r inside a given polygon P?"""
    # We assume the polygon is a list of points, listed clockwise!
    for i in range(len(P[:-1])):
        p, q = P[i], P[i + 1]
        if not _isRightTurn((p, q, r)):
            return 0  # Out!
    return 1  # It's within!


def convexHull(P):
    """Calculate the convex hull of a set of points."""
    # Remove any duplicates
    # If the hull has a duplicate point, it will be returned once
    # It is up to the application to handle it correctly
    unique = {}
    for p in P:
        unique[p] = 1
    points = list(unique.keys())
    points.sort()
    # Build upper half of the hull.
    upper = [points[0], points[1]]
    for p in points[2:]:
        upper.append(p)
        while len(upper) > 2 and not _isRightTurn(upper[-3:]):
            del upper[-2]
    # Build lower half of the hull.
    points.reverse()
    lower = [points[0], points[1]]
    for p in points[2:]:
        lower.append(p)
        while len(lower) > 2 and not _isRightTurn(lower[-3:]):
            del lower[-2]
    # Remove duplicates.
    del lower[0]
    del lower[-1]
    # Concatenate both halfs and return.
    return tuple(upper + lower)


######################################################################
######################################################################
