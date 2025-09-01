"""
@author Fraser Callaghan
"""


import vtk
from vtk.util import numpy_support # type: ignore
import numpy as np
from typing import List, Dict, Union, Optional, Tuple
from . import ftk


# ======================================================================================================================
#           VTK TYPE CHECKERS
# ======================================================================================================================
def isVTI(data):
    return data.IsA('vtkImageData')


def isVTP(data):
    try:
        return data.IsA('vtkPolyData')
    except AttributeError:
        return False


def isVTS(data):
    try:
        return data.IsA('vtkStructuredGrid')
    except AttributeError:
        return False


# ======================================================================================================================
#           VTK MATH
# ======================================================================================================================
def angleBetweenTwoVectors(vecA, vecB):
    return vtk.vtkMath.AngleBetweenVectors(vecA, vecB)


# ======================================================================================================================
#           VTK NUMPY SUPPORT HELPERS
# ======================================================================================================================
def getArrayNames(data: vtk.vtkDataObject, pointData: bool = True) -> List[str]:
    """
    Get the list of array names from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        pointData (bool): Whether to get point data arrays.

    Returns:
        List[str]: The list of array names.
    """
    if pointData:
        return [data.GetPointData().GetArrayName(i) for i in range(data.GetPointData().GetNumberOfArrays())]
    else:
        return [data.GetCellData().GetArrayName(i) for i in range(data.GetCellData().GetNumberOfArrays())]


def getArray(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> vtk.vtkAbstractArray:
    """
    Get an array from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to get.
        pointData (bool): Whether to get point data arrays.

    Returns:
        vtk.vtkAbstractArray: The array.
    """
    if pointData:
        return data.GetPointData().GetAbstractArray(arrayName)
    else:
        return data.GetCellData().GetAbstractArray(arrayName)


def getScalarsArrayName(data: vtk.vtkDataObject, pointData: bool = True) -> Optional[str]:
    """
    Get the name of the scalars array from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        pointData (bool): Whether to get point data arrays [default: True].
    Returns:
        str: The name of the scalars array (None if none found)
    """
    aS = data.GetPointData().GetScalars() if pointData else data.GetCellData().GetScalars()
    try:
        return aS.GetName()
    except AttributeError: # in case no scalars set
        return None


def getVectorsArrayName(data: vtk.vtkDataObject, pointData: bool = True) -> Optional[str]:
    aS = data.GetPointData().GetVectors() if pointData else data.GetCellData().GetVectors()
    try:
        return aS.GetName()
    except AttributeError: # in case no scalars set
        return None


def getArrayId(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> Optional[int]:
    """
    Get the index of an array in a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to get.
        pointData (bool): Whether to get point data arrays.

    Returns:
        Optional[int]: The index of the array.
    """
    if pointData:
        for i in range(data.GetPointData().GetNumberOfArrays()):
            if arrayName == data.GetPointData().GetArrayName(i):
                return i
    else:
        for i in range(data.GetCellData().GetNumberOfArrays()):
            if arrayName == data.GetCellData().GetArrayName(i):
                return i
    return None


def renameArray(data: vtk.vtkDataObject, arrayNameOld: str, arrayNameNew: str, pointData: bool = True) -> None:
    """
    Rename an array in a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayNameOld (str): The old name of the array.
        arrayNameNew (str): The new name of the array.
        pointData (bool): Whether to rename point (or cell)data arrays [default: True].
    """
    if pointData:
        data.GetPointData().GetArray(arrayNameOld).SetName(arrayNameNew)
    else:
        data.GetCellData().GetArray(arrayNameOld).SetName(arrayNameNew)


def getArrayAsNumpy(data: vtk.vtkDataObject, arrayName: str, RETURN_3D: bool = False, pointData: bool = True) -> np.ndarray:
    """
    Get an array from a VTK data object as a numpy array.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array.
        RETURN_3D (bool): Whether to return a 3D array [default: False].
        pointData (bool): Whether to get point data arrays [default: True].
    Returns:
        np.ndarray: The array.
    """
    A = numpy_support.vtk_to_numpy(getArray(data, arrayName, pointData=pointData)).copy()
    if RETURN_3D:
        if np.ndim(A) == 2:
            return np.reshape(A, list(__getDimensions(data))+[A.shape[1]], 'F')
        else:
            return np.reshape(A, __getDimensions(data), 'F')
    else:
        return A


def getScalarsAsNumpy(data: vtk.vtkDataObject, RETURN_3D: bool = False, pointData: bool = True) -> np.ndarray:
    """
    Get the scalars as a numpy array.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        RETURN_3D (bool): Whether to return a 3D array [default: False].
        pointData (bool): Whether to get point (or cell) data scalars [default: True].
    Returns:
        np.ndarray: The scalars.
    """
    if pointData:   
        A = numpy_support.vtk_to_numpy(data.GetPointData().GetScalars()).copy()
    else:
        A = numpy_support.vtk_to_numpy(data.GetCellData().GetScalars()).copy()
    if RETURN_3D:
        if np.ndim(A) == 2:
            return np.reshape(A, list(__getDimensions(data))+[A.shape[1]], 'F')
        else:
            return np.reshape(A, __getDimensions(data), 'F')
    return A


def __getDimensions(data):
    dims = [0,0,0]
    data.GetDimensions(dims) 
    return dims


# ======================================================================================================================
#           SET ARRAYS
# ======================================================================================================================
def setArrayFromNumpy(data: vtk.vtkDataObject, npArray: np.ndarray, arrayName: str, SET_SCALAR: bool = False, SET_VECTOR: bool = False, IS_3D: bool = False, pointData: bool = True) -> None:
    """
    Add a numpy array to a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        npArray (np.ndarray): The numpy array.
        arrayName (str): The name of the array.
        SET_SCALAR (bool): Whether to set the array as scalars.
        SET_VECTOR (bool): Whether to set the array as vectors.
        IS_3D (bool): Whether the array is 3D.
        pointData (bool): Whether to add point data arrays [default: True].
    """
    return addNpArray(data, npArray, arrayName, SET_SCALAR, SET_VECTOR, IS_3D, pointData=pointData)
    
def addNpArray(data: vtk.vtkDataObject, npArray: np.ndarray, arrayName: str, SET_SCALAR: bool = False, SET_VECTOR: bool = False, IS_3D: bool = False, pointData: bool = True) -> None:
    """
    Add a numpy array to a VTK data object. TO DEPRECIATE - RENAMED AS setArrayFromNumpy

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        npArray (np.ndarray): The numpy array.
        arrayName (str): The name of the array.
        SET_SCALAR (bool): Whether to set the array as scalars.
        SET_VECTOR (bool): Whether to set the array as vectors.
        IS_3D (bool): Whether the array is 3D.
        pointData (bool): Whether to add point data arrays [default: True].
    """
    if getArrayId(data, arrayName, pointData=pointData) is not None:
        if pointData:
            data.GetPointData().RemoveArray(arrayName)
        else:
            data.GetCellData().RemoveArray(arrayName)
    if IS_3D:
        if np.ndim(npArray) == 4:
            npArray = np.reshape(npArray, (np.prod(npArray.shape[:3]), 3), 'F')
        else:
            npArray = np.reshape(npArray, np.prod(__getDimensions(data)), 'F')
    aArray = numpy_support.numpy_to_vtk(npArray, deep=1)
    aArray.SetName(arrayName)
    if SET_SCALAR:
        if pointData:
            data.GetPointData().SetScalars(aArray)
        else:
            data.GetCellData().SetScalars(aArray)
    elif SET_VECTOR:
        if pointData:
            data.GetPointData().SetVectors(aArray)
        else:
            data.GetCellData().SetVectors(aArray)
    else:
        if pointData:
            data.GetPointData().AddArray(aArray)
        else:
            data.GetCellData().AddArray(aArray)


def setArrayDtype(data: vtk.vtkDataObject, arrayName: str, dtype: np.dtype, SET_SCALAR: bool = False, pointData: bool = True) -> None:
    A = getArrayAsNumpy(data, arrayName, pointData=pointData)
    setArrayFromNumpy(data, A.astype(dtype), arrayName, SET_SCALAR=SET_SCALAR, pointData=pointData)


def setArrayAsScalars(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> None:
    """
    Set an array as scalars. Note: array must already be in data and if a scalars array already exists then it will be overwritten.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array (already in data).
        pointData (bool): Whether to set point data scalars [default: True].
    """
    if pointData:
        data.GetPointData().SetScalars(getArray(data, arrayName, pointData=pointData))
    else:
        data.GetCellData().SetScalars(getArray(data, arrayName, pointData=pointData))


def ensureScalarsSet(data: vtk.vtkDataObject, possibleName: Optional[str] = None, pointData: bool = True) -> str:
    """
    Ensure that scalars are set for a VTK data object. 
    Necessary for some VTK filters. 
    If no name given then first in list taken. 

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        possibleName (Optional[str]): The name of the array to set as scalars.
        pointData (bool): Whether to set point data scalars [default: True].

    Returns:
        str: The name of the scalars array.
    """
    aS = data.GetPointData().GetScalars() if pointData else data.GetCellData().GetScalars()
    try:
        return aS.GetName()
    except AttributeError: # in case no scalars set
        names = getArrayNames(data, pointData=pointData)
        if possibleName is not None:
            if possibleName in names:
                setArrayAsScalars(data, possibleName, pointData=pointData)
                return possibleName
        setArrayAsScalars(data, names[0], pointData=pointData)
        return names[0]


# ======================================================================================================================
#           DELETE ARRAYS
# ======================================================================================================================
def delArray(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> None:
    """
    Delete an array from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to delete.
        pointData (bool): Whether to delete point data arrays [default: True].
    """
    if pointData:
        data.GetPointData().RemoveArray(arrayName)
    else:
        data.GetCellData().RemoveArray(arrayName)


def delArraysExcept(data: vtk.vtkDataObject, arrayNamesToKeep_list: List[str], pointData: bool = True) -> vtk.vtkDataObject:
    """
    Delete all arrays except the specified ones.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayNamesToKeep_list (List[str]): The list of array names to keep.
        pointData (bool): Whether to delete point data arrays [default: True].
    Returns:
        vtk.vtkDataObject: The data object with the specified arrays kept.
    """
    for ia in getArrayNames(data, pointData=pointData):
        if ia not in arrayNamesToKeep_list:
            delArray(data, ia, pointData=pointData)
    return data


# ======================================================================================================================
#           VTK FIELD DATA
# ======================================================================================================================
def addFieldData(data: vtk.vtkDataObject, fieldVal: float, fieldName: str) -> None:
    tagArray = numpy_support.numpy_to_vtk(np.array([float(fieldVal)]))
    tagArray.SetName(fieldName)
    data.GetFieldData().AddArray(tagArray)


def getFieldData(data: vtk.vtkDataObject, fieldName: str) -> np.ndarray:
    return numpy_support.vtk_to_numpy(data.GetFieldData().GetArray(fieldName)).copy()


def getFieldDataDict(data: vtk.vtkDataObject) -> Dict[str, np.ndarray]:
    """
    Get the field data as a dictionary. Note: will skip strings.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        Dict[str, np.ndarray]: The field data.
    """
    dictOut = {}
    for fieldName in getFieldDataNames(data):
        try:
            dictOut[fieldName] = numpy_support.vtk_to_numpy(data.GetFieldData().GetArray(fieldName)).copy()
        except AttributeError: # str
            pass
    return dictOut


def getFieldDataNames(data: vtk.vtkDataObject) -> List[str]:
    """
    Get the field data names from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        List[str]: The field data names.
    """
    names = [data.GetFieldData().GetArrayName(i) for i in range(data.GetFieldData().GetNumberOfArrays())]
    return names


def duplicateFieldData(srcData: vtk.vtkDataObject, destData: vtk.vtkDataObject) -> None:
    """
    Duplicate the field data from one VTK data object to another.

    Args:
        srcData (vtk.vtkDataObject): The source VTK data object.
        destData (vtk.vtkDataObject): The destination VTK data object.
    """
    for i in range(srcData.GetFieldData().GetNumberOfArrays()):
        fName = srcData.GetFieldData().GetArrayName(i)
        try:
            val = numpy_support.vtk_to_numpy(srcData.GetFieldData().GetArray(fName))
            tagArray = numpy_support.numpy_to_vtk(val)
            tagArray.SetName(fName)
            destData.GetFieldData().AddArray(tagArray)
        except AttributeError:
            pass


def deleteFieldData(data: vtk.vtkDataObject) -> vtk.vtkDataObject:
    """
    Remove the field data from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        vtk.vtkDataObject: The data object with the field data removed.
    """
    aNames = [data.GetFieldData().GetArrayName(i) for i in range(data.GetFieldData().GetNumberOfArrays())]
    for fName in aNames:
        print(f" rm {fName}")
        data.GetFieldData().RemoveArray(fName)
    return data


# ======================================================================================================================
#           VTK POINTS
# ======================================================================================================================
def getVtkPointsAsNumpy(data):
    """
    Get the points as a numpy array.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        np.ndarray: The points.
    """
    if isVTI(data):
        return np.array([data.GetPoint(pointID) for pointID in range(data.GetNumberOfPoints())])
    return numpy_support.vtk_to_numpy(data.GetPoints().GetData())


def getPtsAsNumpy(data):
    """
    Get the points as a numpy array.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        np.ndarray: The points.
    """
    return getVtkPointsAsNumpy(data)


def getCellCenters(structuredData):
    cellCentersFilter = vtk.vtkCellCenters()
    cellCentersFilter.SetInputData(structuredData)
    cellCentersFilter.VertexCellsOn()
    cellCentersFilter.Update()
    return cellCentersFilter.GetOutput()

# ======================================================================================================================
#           VTK SOURCE
# ======================================================================================================================
def buildImplicitSphere(centerPt, radius):
    """ returns vtkSphere - for implicit functions etc
        use buildSphereSource if want polydata
    """
    vtksphere = vtk.vtkSphere()
    vtksphere.SetCenter(centerPt[0], centerPt[1], centerPt[2])
    vtksphere.SetRadius(radius)
    return vtksphere

def buildSphereSource(centerPt, radius, res=8):
    """ returns sphere polydata
    """
    vtksphere = vtk.vtkSphereSource()
    vtksphere.SetCenter(centerPt)
    vtksphere.SetRadius(radius)
    vtksphere.SetPhiResolution(res)
    vtksphere.SetThetaResolution(res)
    vtksphere.Update()
    return vtksphere.GetOutput()

def buildCylinderSource(centerPt, radius, height, res=8, norm=None):
    """ returns sphere polydata
    """
    vtkCyl = vtk.vtkCylinderSource()
    vtkCyl.SetCenter(centerPt)
    vtkCyl.SetRadius(radius)
    vtkCyl.SetHeight(height)
    vtkCyl.SetResolution(res)
    vtkCyl.Update()
    cyl = vtkCyl.GetOutput()
    if norm is not None:
        return translatePoly_AxisA_To_AxisB(cyl, [0,1,0], norm)
    return cyl

def buildImplicitBox(faceCP, norm, boxWidth, boxThick):
    """
    Builds a box so that the face cp is given and then a thick in the norm direction
    :param faceCP:
    :param norm:
    :param boxWidth:
    :param boxThick:
    :return:
    """
    norm = ftk.normaliseArray(norm)
    vtkBox = vtk.vtkBox()
    bW, bT = boxWidth / 2.0, boxThick / 2.0
    vtkBox.SetBounds(-bW, bW, -bW, bW, -bT, bT)
    aLabelTransform = vtk.vtkTransform()
    aLabelTransform.PostMultiply()
    aLabelTransform.Identity()
    rad = ftk.angleBetween2Vec(norm, [0, 0, 1])
    rotVec = np.cross(norm, [0, 0, 1])
    deg = ftk.rad2deg(rad)
    tt = np.array(faceCP) + np.array(norm) * bT
    aLabelTransform.RotateWXYZ(-deg, rotVec[0], rotVec[1], rotVec[2])
    aLabelTransform.Translate(tt[0], tt[1], tt[2])
    vtkBox.SetTransform(aLabelTransform)
    return vtkBox

def buildCubeSource(faceCP, norm, boxWidth, boxThick):
    cube = vtk.vtkCubeSource()
    bW, bT = boxWidth / 2.0, boxThick / 2.0
    cube.SetBounds(-bW, bW, -bW, bW, -bT, bT)
    cube.Update()
    aLabelTransform = vtk.vtkTransform()
    aLabelTransform.PostMultiply()
    aLabelTransform.Identity()
    rad = ftk.angleBetween2Vec(norm, [0, 0, 1])
    rotVec = np.cross(norm, [0, 0, 1])
    deg = ftk.rad2deg(rad)
    tt = np.array(faceCP) + np.array(norm) * bT
    aLabelTransform.RotateWXYZ(-deg, rotVec[0], rotVec[1], rotVec[2])
    aLabelTransform.Translate(tt[0], tt[1], tt[2])
    tpd = vtk.vtkTransformPolyDataFilter()
    tpd.SetInputData(cube.GetOutput())
    tpd.SetTransform(aLabelTransform)
    tpd.Update()
    return tpd.GetOutput()


def buildPolyLineBetweenTwoPoints(ptStart, ptEnd, nPts):
    """ build a poly line between start and end points, with nPts
    """
    ptStart = np.array(ptStart)
    vec = np.array(ptEnd) - ptStart
    vecM = np.linalg.norm(vec)
    vec_unit = vec / vecM
    dv = vecM / (nPts - 1)
    vPts = vtk.vtkPoints()
    polyLine = vtk.vtkPolyLine()
    vPts.InsertPoint(0, (ptStart[0], ptStart[1], ptStart[2]))
    polyLine.GetPointIds().InsertId(0, 0)
    for k in range(1, nPts):
        newP = ptStart + (k * dv * vec_unit)
        vPts.InsertPoint(k, (newP[0], newP[1], newP[2]))
        polyLine.GetPointIds().InsertId(k, k)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(vPts)
    polyData.SetLines(cells)
    return polyData


def buildPolyTrianglesAtCp(pts, refVec=None, NORMALS_OUT=True, cp=None): # FIXME - to labels
    if refVec is not None:
        if pts.shape[0] > 3:
            isClockwise = ftk.isClosedPolygonClockwise(pts, refVec)
            if NORMALS_OUT:
                if isClockwise:
                    pts = pts[::-1]
            else:
                if not isClockwise:
                    pts = pts[::-1]
    if cp is None:
        cp = np.mean(pts, 0)
    nPts, _ = pts.shape
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(nPts+1)
    triCellArray = vtk.vtkCellArray()
    polyData = vtk.vtkPolyData()
    for k in range(nPts):
        tri = vtk.vtkTriangle()
        tri.GetPointIds().SetId(0, k)
        id2 = k + 1
        if k == (nPts-1):
            id2 = 0
        tri.GetPointIds().SetId(1, id2)
        tri.GetPointIds().SetId(2, nPts)
        triCellArray.InsertNextCell(tri)
        # points.InsertNextPoint(pts[k])
        points.SetPoint(k, pts[k])
    # points.InsertNextPoint(cp)
    points.SetPoint(k+1, cp)
    polyData.SetPoints(points)
    polyData.SetPolys(triCellArray)
    return polyData


def _getOptimalPlaneSize_Resolution(data, subDivide=100):
    PLANE_SIZE = getMaximumBounds(data)
    RESOLUTION = PLANE_SIZE / subDivide
    return PLANE_SIZE, RESOLUTION


def buildPlaneCentredOnRoi(roiVTK, PLANE_SIZE=None, RESOLUTION=None, subDivide=100):
    if PLANE_SIZE is None:
        PLANE_SIZE, RESOLUTION = _getOptimalPlaneSize_Resolution(roiVTK, subDivide)
    pts = getVtkPointsAsNumpy(roiVTK)
    return buildPlaneCentredOnO(roiVTK.GetCenter(), pts[0], ftk.fitPlaneToPoints(pts)[:3], PLANE_SIZE, RESOLUTION)


def buildPlaneCentredOnSphere(sphereVTK, structVTK, vecArrayName='Velocity_m_per_s',
                              PLANE_SIZE=0.07, RESOLUTION=0.001):
    structPts = getVtkPointsAsNumpy(structVTK)
    cID = ftk.getIdOfPointClosestToX(sphereVTK.GetCenter(), structPts)
    norm = getArrayAsNumpy(structVTK, vecArrayName)[cID]
    return buildPlanePtAndNorm(sphereVTK.GetCenter(), norm, PLANE_SIZE, RESOLUTION)


def buildPlanePtAndNorm(X, norm, PLANE_SIZE=0.07, RESOLUTION=0.001):
    norm = ftk.normaliseArray(norm)
    cc = ftk.buildCircle3D(X, norm, PLANE_SIZE, 25)
    v1 = ftk.normaliseArray(cc[0] - X)
    v2 = np.cross(norm, v1)
    v3 = np.cross(norm, v2)
    nDiv = int(PLANE_SIZE / RESOLUTION)
    newPlane = buildPlaneSource(X, X + PLANE_SIZE * v2, X + PLANE_SIZE * v3, [nDiv, nDiv])
    return filterTransformPolyData(newPlane, disp=np.array(X) - np.array(newPlane.GetCenter()))


def buildPlaneCentredOnO(O, pointInplane, norm, PLANE_SIZE=0.07, RESOLUTION=0.001):
    v1 = ftk.normaliseArray(pointInplane - O)
    nDiv = int(PLANE_SIZE / RESOLUTION)
    v2 = np.cross(v1, norm)
    newPlane = buildPlaneSource(O, O + PLANE_SIZE * v1, O + PLANE_SIZE * v2, [nDiv, nDiv])
    return filterTransformPolyData(newPlane, disp=np.array(O) - np.array(newPlane.GetCenter()))


def buildPlaneSource(origin, pt1, pt2, nDivXY):
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(origin)
    plane.SetPoint1(pt1)
    plane.SetPoint2(pt2)
    plane.SetResolution(nDivXY[0], nDivXY[1])
    plane.Update()
    return plane.GetOutput()


def buildPolyLineFromXYZ_spline(xyz, splineDist, LOOP=False):
    pp = buildPolyLineFromXYZ(xyz, LOOP=LOOP)
    pp = filterVtpSpline(pp, splineDist)
    return pp


def buildPolyLineFromXYZ(xyz, LOOP=False):
    """ build a poly line
        - if LOOP - then close with extra lineseg between last and first points
    """
    vPts = vtk.vtkPoints()
    polyLine = vtk.vtkPolyLine()
    vPts.InsertPoint(0, (xyz[0][0], xyz[0][1], xyz[0][2]))
    polyLine.GetPointIds().InsertId(0, 0)
    for k in range(1, len(xyz)):
        vPts.InsertPoint(k, (xyz[k][0], xyz[k][1], xyz[k][2]))
        polyLine.GetPointIds().InsertId(k, k)
    if LOOP:
        polyLine.GetPointIds().InsertId(len(xyz), 0)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(vPts)
    polyData.SetLines(cells)
    return polyData


def buildPolydataFromXYZ(xyz):
    xyz = ftk.__forcePts_nx3(xyz)
    myVtkPoints = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    for k in range(xyz.shape[0]):
        try:
            ptID = myVtkPoints.InsertNextPoint(xyz[k, 0], xyz[k, 1], xyz[k, 2])
        except IndexError:
            break
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(ptID)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(myVtkPoints)
    polyData.SetVerts(vertices)
    return polyData


# ======================================================================================================================
#           CLIPPING & CUTTING
# ======================================================================================================================
def clippedByCircle(data, centerPt, normal, radius, COPY=False):
    data2 = getDataCutByPlane(data, normal, centerPt)
    pOut = getPolyDataClippedBySphere(data2, centerPt, radius)
    if COPY:
        return copyPolyData(pOut)
    return pOut

def sliceByPlane(data, pt, norm): # THIS IS DEPRECIATED
    return getDataCutByPlane(data, norm, pt)

def getDataCutByPlane(data, normal, planePt):
    vtkplane = vtk.vtkPlane()
    vtkplane.SetOrigin(planePt[0], planePt[1], planePt[2])
    vtkplane.SetNormal(normal[0], normal[1], normal[2])
    vtkcutplane = vtk.vtkCutter()
    vtkcutplane.SetInputData(data)
    vtkcutplane.SetCutFunction(vtkplane)
    vtkcutplane.Update()
    return vtkcutplane.GetOutput()


def getPolyDataClippedByROI(data, roi, INSIDE=False, axialDisplacement=0.02,
                            closestPt=None, refNorm=None, boxWidth=None, boxWidthFactor=3.0): # FIXME
    """ If no closest point given will return largest.
        refNorm points into volume
    """
    try:
        R = getPolyDataMeanFromCenter(roi)
        X = roi.GetCenter()
    except AttributeError:
        X = roi
        R = 0.025
    try:
        len(refNorm)
        normT = ftk.fitPlaneToPoints(getPtsAsNumpy(roi))[:3]
        norm = ftk.setVecAConsitentWithVecB(normT, refNorm)
    except TypeError:
        norm = ftk.fitPlaneToPoints(getPtsAsNumpy(roi))[:3]
    if boxWidth is None:
        boxWidth = boxWidthFactor * R
    if closestPt is None:
        if refNorm is not None:
            closestPt = 'CP-NORM'
    return getPolyDataClippedByBox(data, X, norm, boxWidth, axialDisplacement,
                                   INSIDE=INSIDE, closestPt=closestPt)


def getPolyDataClippedByBox(data, cp, norm, boxWidth, boxThick, INSIDE=False,
                            closestPt=None, RETURN_FULL=False):
    """ Note - norm moves the box opposite so if inside then flip norm
        If no closest point given will return largest
        If closestPt == 'CP-NORM' then will use cp and norm and boxThick to calc closest pt
    """
    norm = ftk.normaliseArray(norm)
    vtkBox = vtk.vtkBox()
    bW, bT = boxWidth / 2.0, boxThick / 2.0
    vtkBox.SetBounds(-bW, bW, -bW, bW, -bT, bT)
    aLabelTransform = vtk.vtkTransform()
    aLabelTransform.Identity()
    rad = ftk.angleBetween2Vec(norm, [0, 0, 1])
    rotVec = np.cross(norm, [0, 0, 1])
    deg = ftk.rad2deg(rad)
    aLabelTransform.RotateWXYZ(deg, rotVec[0], rotVec[1], rotVec[2])
    tt = cp - norm * bT
    aLabelTransform.Translate(-tt[0], -tt[1], -tt[2])
    vtkBox.SetTransform(aLabelTransform)
    vtkcutbox = vtk.vtkClipPolyData()
    vtkcutbox.SetClipFunction(vtkBox)
    vtkcutbox.SetInputData(data)
    if INSIDE:
        vtkcutbox.InsideOutOn()
    vtkcutbox.Update()
    clipVol = vtkcutbox.GetOutput()
    if RETURN_FULL:
        return clipVol
    if (type(closestPt)==str) and (closestPt == 'CP-NORM'):
        closestPt = cp+(norm*3.0*bT)
    try:
        len(closestPt)
        # return getConnectedRegionClosestToX(clipVol, closestPt)
        return getConnectedRegionMinDistToX(clipVol, closestPt)
    except TypeError:
        return getConnectedRegionLargest(clipVol)


def getPolyDataClippedBySphere(data, centerPt, radius, CRINKLECLIP=False):
    vtksphere = buildImplicitSphere(centerPt, radius)
    if CRINKLECLIP:
        vtkcutsphere = vtk.vtkExtractGeometry()
    else:
        vtkcutsphere = vtk.vtkClipPolyData()
    vtkcutsphere.SetInputData(data)
    if CRINKLECLIP:
        vtkcutsphere.SetImplicitFunction(vtksphere)
        vtkcutsphere.ExtractInsideOn()
        vtkcutsphere.ExtractBoundaryCellsOn()
    else:
        vtkcutsphere.SetClipFunction(vtksphere)
        vtkcutsphere.InsideOutOn()
    vtkcutsphere.Update()
    return vtkcutsphere.GetOutput()


def clippedByPolyData(data, polyData):
    implicitPolyDataDistance = vtk.vtkImplicitPolyDataDistance()
    implicitPolyDataDistance.SetInput(polyData)
    #
    signedDistances = vtk.vtkFloatArray()
    signedDistances.SetNumberOfComponents(1)
    signedDistances.SetName("SignedDistances")
    # Evaluate the signed distance function at all of the grid points
    for pointId in range(data.GetNumberOfPoints()):
        p = data.GetPoint(pointId)
        signedDistance = implicitPolyDataDistance.EvaluateFunction(p)
        signedDistances.InsertNextValue(signedDistance)
    # add the SignedDistances to the grid
    data.GetPointData().SetScalars(signedDistances)
    # use vtkClipDataSet to slice the grid with the polydata
    clipper = vtk.vtkClipDataSet()
    clipper.SetInputData(data)
    clipper.InsideOutOn()
    clipper.SetValue(0.0)
    clipper.Update()
    return clipper.GetOutput()


def doesLinePierceTri(p0, p1, triCell):
    # Perform intersection.
    tol = 1e-7
    x = [0, 0, 0]  # Intersection.
    xp = [0, 0, 0]  # Parametric coordinates of intersection.
    t = vtk.mutable(0)  # Line position, 0 <= t <= 1.
    subId = vtk.mutable(0)  # subId? No idea what it is, usually not needed.
    hasIntersection = triCell.IntersectWithLine(p0, p1, tol, t, x, xp, subId)
    return hasIntersection, x


def doesLinePiercePolygon(p0, p1, polygon):
    nTris = polygon.GetNumberOfCells()
    for k2 in range(nTris):
        tf, x = doesLinePierceTri(p0, p1, polygon.GetCell(k2))
        if tf:
            return k2
    return None


def clippedByPlane(data, centrePt, planeNormal):
    return clipDataByPlane(data, centrePt, planeNormal)


def clipDataByPlane(data, centrePt, planeNormal):
    plane = vtk.vtkPlane()
    plane.SetOrigin(centrePt[0], centrePt[1], centrePt[2])
    plane.SetNormal(planeNormal[0], planeNormal[1], planeNormal[2])
    vtkcutplane = vtk.vtkClipDataSet()
    vtkcutplane.SetInputData(data)
    vtkcutplane.SetClipFunction(plane)
    vtkcutplane.GenerateClipScalarsOn()
    vtkcutplane.Update()
    return vtkcutplane.GetOutput()


def clippedByPlaneClosedSurface(data, centrePt, planeNormal):
    plane = vtk.vtkPlane()
    plane.SetOrigin(centrePt[0], centrePt[1], centrePt[2])
    plane.SetNormal(planeNormal[0], planeNormal[1], planeNormal[2])
    capPlanes = vtk.vtkPlaneCollection()
    capPlanes.AddItem(plane)
    clip = vtk.vtkClipClosedSurface()
    clip.SetClippingPlanes(capPlanes)
    clip.SetInputData(data)
    clip.GenerateFacesOn()
    clip.Update()
    return clip.GetOutput()


def clippedBySphere(data, centerPt, radius):
    vtksphere = buildImplicitSphere(centerPt, radius)
    vtkcutsphere = vtk.vtkClipDataSet()
    vtkcutsphere.SetInputData(data)
    vtkcutsphere.SetClipFunction(vtksphere)
    vtkcutsphere.InsideOutOn()
    vtkcutsphere.Update()
    return vtkcutsphere.GetOutput()


def clippedByScalar(data, arrayName, clipValue, INSIDE_OUT=False):
    vtkClipper = vtk.vtkClipDataSet()
    vtkClipper.SetInputData(data)
    vtkClipper.SetValue(clipValue)
    vtkClipper.SetInputArrayToProcess(0, 0, 0, 0, arrayName)
    if INSIDE_OUT:
        vtkClipper.InsideOutOn()
    vtkClipper.Update()
    return vtkClipper.GetOutput()


def clipVolumeToEightPolydataBoxes(data, RETURN_ptIDs):
    '''
    Clips same ordering as outline filter
    6-7
    4-5
    | |
    2-3
    0-1
    :param data:
    :param RETURN_ptIDs: much faster for downstream operations
    :return: 8 polydata surfs
    '''
    cp = data.GetCenter()
    d = 0.00
    if RETURN_ptIDs:
        setArrayFromNumpy(data, np.arange(0, data.GetNumberOfPoints()), 'pIDs')
    halfPX = clipDataByPlane(data, [cp[0]+d,cp[1],cp[2]], [1, 0, 0])
    halfNX = clipDataByPlane(data, [cp[0]-d,cp[1],cp[2]], [-1, 0, 0])
    quartPXPY = clipDataByPlane(halfPX, [cp[0],cp[1]+d,cp[2]], [0, 1, 0])
    quartPXNY = clipDataByPlane(halfPX, [cp[0],cp[1]-d,cp[2]], [0, -1, 0])
    quartNXPY = clipDataByPlane(halfNX, [cp[0],cp[1]+d,cp[2]], [0, 1, 0])
    quartNXNY = clipDataByPlane(halfNX, [cp[0],cp[1]-d,cp[2]], [0, -1, 0])
    c0 = clipDataByPlane(quartNXNY, [cp[0],cp[1],cp[2]-d], [0, 0, -1])
    c1 = clipDataByPlane(quartPXNY, [cp[0],cp[1],cp[2]-d], [0,0,-1])
    c2 = clipDataByPlane(quartNXPY, [cp[0],cp[1],cp[2]-d], [0,0,-1])
    c3 = clipDataByPlane(quartPXPY, [cp[0],cp[1],cp[2]-d], [0,0,-1])
    c4 = clipDataByPlane(quartNXNY, [cp[0],cp[1],cp[2]+d], [0, 0,1])
    c5 = clipDataByPlane(quartPXNY, [cp[0],cp[1],cp[2]+d], [0,0,1])
    c6 = clipDataByPlane(quartNXPY, [cp[0],cp[1],cp[2]+d], [0,0,1])
    c7 = clipDataByPlane(quartPXPY, [cp[0],cp[1],cp[2]+d], [0,0,1])
    if RETURN_ptIDs:
        return [getArrayAsNumpy(i, "pIDs").astype(int) for i in [c0,c1,c2,c3,c4,c5,c6,c7]]
    else:
        vtpBoxes = [filterExtractSurface(i) for i in [c0,c1,c2,c3,c4,c5,c6,c7]]
        if data.IsA('vtkPolyData'):
            return vtpBoxes
        vtpBoxes = [decimateTris(filterTriangulate(i), 0.9) for i in vtpBoxes]
        return vtpBoxes


def roi_line_to_roi_plane(roiLine, resolution):
    R = getPolyDataMeanFromCenter(roiLine)
    plane = buildPlaneCentredOnRoi(roiLine, R*3.0, resolution)
    planeClip = clipPlaneToROI(plane, roiLine)
    return planeClip


def clipPlaneToROI(fullPlane, ROI):
    """
    :param fullPlane: a plane covering ROI
    :param ROI: the ROI
    :return: plane cliped to pixels within the ROI stencil (polydata)
    """
    SCALE = False
    if ROI.GetNumberOfCells() != 1:
        raise AttributeError('ROI should be single cell polyline')
    maxBounds = getMaximumBounds(ROI)
    if maxBounds < 1.0:
        SCALE = True
        scalef = 1000.0 / maxBounds
        ROI = filterTransformPolyData(ROI, scale=[scalef,scalef,scalef])
        ROI = filterVtpSpline(ROI, getMaximumBounds(ROI)*0.001)
        fullPlane = filterTransformPolyData(fullPlane, scale=[scalef,scalef,scalef])
    else:
        ROI = filterVtpSpline(ROI, maxBounds*0.001)
    loop = vtk.vtkImplicitSelectionLoop()
    loop.SetLoop(ROI.GetPoints())
    extract = vtk.vtkExtractGeometry()
    extract.SetInputData(fullPlane)
    extract.SetImplicitFunction(loop)
    connect = vtk.vtkConnectivityFilter()
    connect.SetInputConnection(extract.GetOutputPort())
    connect.SetExtractionModeToClosestPointRegion()
    connect.SetClosestPoint(ROI.GetPoints().GetPoint(0))
    connect.Update()
    clipOut = filterExtractSurface(connect.GetOutput())
    if clipOut.GetNumberOfPoints() == 0:
        raise ValueError("Error - try with different size plane")
    if SCALE:
        clipOut = filterTransformPolyData(clipOut, scale=[1.0/scalef,1.0/scalef,1.0/scalef])
    return clipOut





# ======================================================================================================================
#           IMAGE DATA
# ======================================================================================================================
def vtiToVts(data):
    sg = vtk.vtkImageDataToPointSet()
    sg.AddInputData(data)
    sg.Update()
    return sg.GetOutput()


def vtsToVti(dataVts):#, MAKE_ISOTROPIC=False):
    return filterResampleToImage(dataVts)


def getVtsOrigin(dataVts):
    return dataVts.GetPoints().GetPoint(0)


def getVtsResolution(dataVts):
    o,p1,p2,p3 = [0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]
    i0,i1,j0,j1,k0,k1 = dataVts.GetExtent()
    dataVts.GetPoint(i0,j0,k0, o)
    dataVts.GetPoint(i0+1,j0,k0, p1)
    dataVts.GetPoint(i0,j0+1,k0, p2)
    dataVts.GetPoint(i0,j0,k0+1, p3)
    di = abs(ftk.distTwoPoints(p1, o))
    dj = abs(ftk.distTwoPoints(p2, o))
    dk = abs(ftk.distTwoPoints(p3, o))
    return [di, dj, dk]


def getResolution_VTI(data):
    return data.GetSpacing()


def getDimsResOriginFromOutline(outline, res, pad):
    try:
        if len(res) == 3:
            di, dj, dk = res[0], res[1], res[2]
        else:
            di, dj, dk = res[0], res[0], res[0]
    except TypeError:
        di, dj, dk = res, res, res
    origin = outline.GetPoints().GetPoint(0)
    DI = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(1))
    DJ = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(2))
    DK = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(4))
    nR, nC, nK = int(DI/di)+1+pad, int(DJ/dj)+1+pad, int(DK/dk)+1+pad
    return [nR,nC,nK], [di,dj,dk], [i-j*pad/2 for i,j in zip(origin,[di,dj,dk])]


def buildRawImageDataFromPolyData(polyData, res, pad=1):
    return buildRawImageDataFromOutline(getOutline(polyData), res, pad)


def buildRawImageDataFromOutline(outline, res, pad=1):
    dd, rr, oo = getDimsResOriginFromOutline(outline, res, pad)
    img = buildRawImageData(dd, rr, oo)
    return img


def buildRawImageDataFromOutline_dims(outline, dims):
    origin = outline.GetPoints().GetPoint(0)
    DI = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(1))
    DJ = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(2))
    DK = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(4))
    di = DI / dims[0]
    dj = DJ / dims[1]
    dk = DK / dims[2]
    img = buildRawImageData(dims, [di, dj, dk], origin)
    return img


def duplicateImageData(imData):
    return buildRawImageData(__getDimensions(imData),
                             imData.GetSpacing(), 
                             imData.GetOrigin())


def buildRawImageData(dims, res, origin=[0 ,0 ,0]):
    newImg = vtk.vtkImageData()
    newImg.SetSpacing(res[0] ,res[1] ,res[2])
    newImg.SetOrigin(origin[0], origin[1], origin[2])
    newImg.SetDimensions(dims[0] ,dims[1] ,dims[2])
    return newImg


def surf2ImageBW(dataSurf, arrayName, res, nDilate=0, nMed=0):
    imBW = buildRawImageDataFromOutline(getOutline(dataSurf), res, pad=10)
    IDs = filterGetEnclosedPts(imBW, dataSurf, 'ID')
    inside = np.zeros(imBW.GetNumberOfPoints())
    inside[IDs] = 1.0
    setArrayFromNumpy(imBW, inside, arrayName, SET_SCALAR=True)
    # dilate
    if nDilate > 0:
        for _ in range(nDilate):
            imBW = filterDilateErode(imBW, [3,3,3], valDilate=1, valErode=0)
    if nMed > 1:
        imBW = filterVtiMedian(imBW, nMed)
    return imBW


def getVarValueAtI_ImageData(imData, X, arrayName):
    """
    Useful to get the vel value at a location from imdata
    :param imData:
    :param X:
    :param arrayName:
    :return: tuple
    """
    iXID = imData.FindPoint(X)
    n = imData.GetPointData().GetArray(arrayName).GetTuple(iXID)
    return n


def getImageX(data, pointID):
    """
    Get X from image matching pointID. NOTE: opposite: iXID = imData.FindPoint(X)
    :param data: image data
    :param pointID: int
    :return: tuple - the point x,y,z
    """
    return data.GetPoint(pointID)


def imageX_ToStructuredCoords(imageData, xyz_list):
    """
    Note - this is no good if extracted a VOI from image already
    in this :

        id2 = ii.FindPoint(xyz)
        ijk = vtkfilters.imageIndex_ToStructuredCoords(ii, [id2])
    """
    # return a list of ijk
    ijk_list = []
    for iX in xyz_list:
        ijk = [0, 0, 0]
        pcoords = [0.0, 0.0, 0.0]
        res = imageData.ComputeStructuredCoordinates(iX, ijk, pcoords)
        if res == 0:
            continue
        ijk_list.append(ijk)
    return ijk_list


def imageIndex_ToStructuredCoords(imageData, index_list):
    dd = __getDimensions(imageData)
    return [np.unravel_index(i, shape=dd, order='F') for i in index_list]


def getNeighbours26_fromImageIndex(imageData, index, delta=1, RETURN_STRUCTCOORDS=False):
    """
    Get the 26 neighbours from an image index
    :param imageData: image data
    :param index: int
    :param delta: int
    :param RETURN_STRUCTCOORDS: bool
    :return: list of ints
    """
    dims = __getDimensions(imageData)
    strucCoord = imageIndex_ToStructuredCoords(imageData, [index])[0]
    newStructCoords = []
    for k0 in range(0-delta, 1+delta):
        for k1 in range(0-delta, 1+delta):
            for k2 in range(0-delta, 1+delta):
                newIjk = (strucCoord[0] + k0, strucCoord[1] + k1, strucCoord[2] + k2)
                if (min(newIjk)<0) or (newIjk[0]>=dims[0]) or (newIjk[1]>=dims[1]) or (newIjk[2]>=dims[2]):
                    continue
                if newIjk == strucCoord:
                    continue
                newStructCoords.append(newIjk)
    if RETURN_STRUCTCOORDS:
        return newStructCoords
    return imageStrucCoords_toIndex(imageData, newStructCoords)


def imageStrucCoords_toIndex(imageData, strucCoords_list):
    """
    Convert structured coordinates to image indices
    :param imageData: image data
    :param strucCoords_list: list of tuples
    :return: list of ints
    """
    if len(strucCoords_list) == 3:
        try:
            strucCoords_list[0][0]
        except TypeError:
            strucCoords_list = [strucCoords_list]
    return [imageData.ComputePointId(ijk) for ijk in strucCoords_list]


def imageStrucCoords_toX(imageData, strucCoords_list):
    # Be awre - this is not considering any transform
    return [getImageX(imageData, i) for i in imageStrucCoords_toIndex(imageData, strucCoords_list)]


def filterFlipImageData(vtiObj, axis):
    flipper = vtk.vtkImageFlip()
    flipper.SetFilteredAxes(axis)
    flipper.SetInputData(vtiObj)
    flipper.Update()
    return flipper.GetOutput()
    
# ======================================================================================================================
#           POLY DATA
# ======================================================================================================================
def getPolyDataMeanFromCenter(data):
    return np.mean(ftk.distPointPoints(data.GetCenter(), getPtsAsNumpy(data)))



# ======================================================================================================================
#           COPY DATA
# ======================================================================================================================
def copyPolyData(data):
    dataOut = vtk.vtkPolyData()
    dataOut.DeepCopy(data)
    return dataOut


def copyData(data):
    if data.IsA('vtkImageData'):
        dataOut = vtk.vtkImageData()
    elif data.IsA('vtkPolyData'):
        dataOut = vtk.vtkPolyData()
    elif data.IsA('vtkUnstructuredGrid'):
        dataOut = vtk.vtkUnstructuredGrid()
    dataOut.DeepCopy(data)
    return dataOut



# ======================================================================================================================
#           VTK FILTERS
# ======================================================================================================================
def contourFilter(data: vtk.vtkDataObject, isoValue: float) -> vtk.vtkPolyData:
    """
    Find the triangles that lie along the 'isoValue' contour.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        isoValue (float): The iso value.

    Returns:
        vtk.vtkPolyData: The filtered data.
    """
    cF = vtk.vtkContourFilter()
    cF.SetInputData(data)
    cF.SetValue(0, isoValue)
    cF.Update()
    return cF.GetOutput()


def cleanData(data: vtk.vtkDataObject, tolerance: float = 0.0, DO_POINT_MERGING: bool = True) -> vtk.vtkPolyData:
    """ Cleans PolyData - merge points, remove pts not in cell, remove cells
        with no points etc.
        30.9.14: Set default tol=0.0, should be faster merging as no look up
                 of every pt. See class docs
    """
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(data)
    cleaner.SetAbsoluteTolerance(tolerance)
    cleaner.SetToleranceIsAbsolute(1)
    if not DO_POINT_MERGING:
        cleaner.PointMergingOff()
    cleaner.Update()
    return cleaner.GetOutput()


def reduceNumberOfPoints(data, targetNumberOfPoints):
    totIN = data.GetNumberOfPoints()
    if targetNumberOfPoints >= totIN:
        return data
    IDS = np.random.choice(totIN, size=targetNumberOfPoints, replace=False)
    try:
        id_list = idListToVtkIDs(IDS)
        extract = vtk.vtkExtractPoints()
        extract.SetInputData(data)
        extract.SetPointIds(id_list)
        extract.Update()
        return extract.GetOutput()
    except AttributeError:
        pts = getPtsAsNumpy(data)
        pts_ = pts[IDS]
        return buildPolydataFromXYZ(pts_)


def filterBoolean(dataA, dataB, booleanOperationType):
    """
    Perform a boolean operation on two datasets. Ensure that the data is triangulated.

    Args:
        dataA (vtk.vtkDataObject): The first dataset.
        dataB (vtk.vtkDataObject): The second dataset.
        booleanOperationType (str): The type of boolean operation to perform. Can be 'union', 'intersection', or 'difference'.

    Returns:
        vtk.vtkPolyData: The result of the boolean operation.
    """
    booleanOperation = vtk.vtkBooleanOperationPolyDataFilter()
    booleanOperation.SetInputData(0, dataA)
    booleanOperation.SetInputData(1, dataB)
    if booleanOperationType.lower().startswith('un'):
        booleanOperation.SetOperationToUnion()
    elif booleanOperationType.lower().startswith('inter'):
        booleanOperation.SetOperationToIntersection()
    elif booleanOperationType.lower().startswith('diff'):
        booleanOperation.SetOperationToDifference()
    booleanOperation.Update()
    return booleanOperation.GetOutput()


def tubeFilter(data, radius, nSides=12, CAPS=True):
    """
    Convert a polyline to a tube.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        radius (float): The radius of the tube. If None then will use scalar of polydata
        nSides (int, optional): The number of sides of the tube. Defaults to 12.
        CAPS (bool, optional): Whether to cap the ends of the tube. Defaults to True.

    Returns:
        vtk.vtkPolyData: The filtered data.
    """
    tuber = vtk.vtkTubeFilter()
    tuber.SetInputData(data)
    if radius is None:
        tuber.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    else:
        tuber.SetRadius(radius)
    tuber.SetNumberOfSides(nSides)
    if CAPS:
        tuber.SetCapping(1)
    tuber.Update()
    return tuber.GetOutput()


def filterVtpSpline(data, spacing=None, nPoints=None, smoothFactor=None):
    if (spacing is None) and (nPoints is None):
        raise ValueError("Either spacing or nPoints must be provided")
    p0, pE = data.GetPoints().GetPoint(0), data.GetPoints().GetPoint(data.GetNumberOfPoints() - 1)
    if smoothFactor is not None:
        data = filterVtpSpline(data, nPoints=int(data.GetNumberOfPoints() / float(smoothFactor)))
    sf = vtk.vtkSplineFilter()
    sf.SetInputData(data)
    if nPoints is not None:
        sf.SetNumberOfSubdivisions(nPoints)
        spacing = ftk.distTwoPoints(p0, pE) / nPoints
    else:
        sf.SetSubdivideToLength()
        sf.SetLength(spacing)
    sf.Update()
    cl1 = sf.GetOutput()
    cl1 = cleanData(cl1, 0.05 * spacing)
    d0 = ftk.distTwoPoints(p0, cl1.GetPoints().GetPoint(0))
    d1 = ftk.distTwoPoints(p0, cl1.GetPoints().GetPoint(cl1.GetNumberOfPoints() - 1))
    if d1 < d0:
        xyz = getPtsAsNumpy(cl1)
        cl1 = buildPolyLineFromXYZ(xyz[::-1])
    return cl1


def filterTransformPolyData(polyData, scale=[1.0, 1.0, 1.0], disp=[0.0, 0.0, 0.0], rotate=None, matrix=None, rotateXYZ=None):
    transP = vtk.vtkTransform()
    if matrix:
        try:
            transP.SetMatrix(matrix)
        except TypeError:
            transP = matrix
    else:
        transP.Translate(disp[0], disp[1], disp[2])
        try:
            transP.Scale(scale[0], scale[1], scale[2])
        except TypeError:
            transP.Scale(scale, scale, scale)
        if rotate is not None:
            transP.RotateWXYZ(rotate[0], rotate[1], rotate[2], rotate[3])
        elif rotateXYZ is not None:
            transP.RotateX(rotateXYZ[0])
            transP.RotateY(rotateXYZ[1])
            transP.RotateZ(rotateXYZ[2])
    tpd = vtk.vtkTransformPolyDataFilter()
    tpd.SetInputData(polyData)
    tpd.SetTransform(transP)
    tpd.Update()
    return tpd.GetOutput()


def translatePoly_AxisA_To_AxisB(polyData, vecA, vecB):
    try:
        a1 = ftk.angleBetween2Vec(vecB, vecA)
    except TypeError:
        return polyData # vecA and vecB are basically aligned
    Rvec = np.cross(vecB, vecA)
    rotate = [-1 * ftk.rad2deg(a1), Rvec[0], Rvec[1], Rvec[2]]
    data0 = filterTransformPolyData(polyData, disp=[-1.0 * i for i in polyData.GetCenter()])
    data0R = filterTransformPolyData(data0, rotate=rotate)
    return filterTransformPolyData(data0R, disp=polyData.GetCenter())


def transformPolydataA_to_B_ICP(sourcePoly, target_poly, maxMeanDist, RIGID=False, AFFINE=False, internalIterations=50, maxLandmarks=1000):
    tx = iterativeClosestPointsTransform(sourcePoly, target_poly, maxMeanDist, RIGID=RIGID, 
                                        AFFINE=AFFINE, internalIterations=internalIterations, 
                                        maxLandmarks=maxLandmarks)
    return filterTransformPolyData(sourcePoly, matrix=tx.GetMatrix())


def iterativeClosestPointsTransform(sourcePoly, target_poly, maxMeanDist, RIGID=False, AFFINE=False, internalIterations=50, maxLandmarks=1000):
    """
    Iterative Closest Points Transform

    Args:
        sourcePoly (vtk.vtkPolyData): The source polydata.
        target_poly (vtk.vtkPolyData): The target polydata.
        maxMeanDist (float): The maximum mean distance.
        RIGID (bool, optional): Whether to use rigid transformation. Defaults to False. (default Similarity)
        AFFINE (bool, optional): Whether to use affine transformation. Defaults to False. (default Similarity)
        internalIterations (int, optional): The number of internal iterations. Defaults to 50.
        maxLandmarks (int, optional): The maximum number of landmarks. Defaults to 1000.
    """
    icp = vtk.vtkIterativeClosestPointTransform()
    if RIGID:
        icp.GetLandmarkTransform().SetModeToRigidBody()
    elif AFFINE:
        icp.GetLandmarkTransform().SetModeToAffine()
    else:
        icp.GetLandmarkTransform().SetModeToSimilarity() # Trans, Rot and Scale only
    icp.SetSource(sourcePoly)
    icp.SetTarget(target_poly)
    # icp.DebugOn()
    icp.SetMaximumNumberOfIterations(internalIterations)
    icp.StartByMatchingCentroidsOn()
    icp.SetMaximumMeanDistance(maxMeanDist)
    icp.SetMeanDistanceModeToAbsoluteValue()
    icp.SetMaximumNumberOfLandmarks(maxLandmarks)
    icp.Modified()
    icp.Update()
    return icp
    

def transformImageData(data, matrix, scaleF=[1.0,1.0,1.0]):
    # Returns vts
    transMatrix = vtk.vtkTransform()
    transMatrix.SetMatrix(matrix)
    tfilterMatrix = vtk.vtkTransformFilter()
    tfilterMatrix.SetTransform(transMatrix)
    tfilterMatrix.SetInputData(data)
    tfilterMatrix.Update()
    ##
    transScale = vtk.vtkTransform()
    transScale.Identity()
    transScale.Scale(scaleF)
    tfilterScale = vtk.vtkTransformFilter()
    tfilterScale.SetTransform(transScale)
    tfilterScale.SetInputData(tfilterMatrix.GetOutput())
    tfilterScale.Update()
    return tfilterScale.GetOutput()


def pointToCellData(data): # pointsToCells
    p2c = vtk.vtkPointDataToCellData()
    p2c.SetInputData(data)
    p2c.PassPointDataOn()
    p2c.Update()
    return p2c.GetOutput()


def cellToPointData(data):
    cellToPt_f = vtk.vtkCellDataToPointData()
    cellToPt_f.SetInputData(data)
    cellToPt_f.PassCellDataOn()
    cellToPt_f.Update()
    return cellToPt_f.GetOutput()


def getOutline(dataIn):
    of = vtk.vtkOutlineFilter()
    of.SetInputData(dataIn)
    of.Update()
    return of.GetOutput()


def getMaximumBounds(data):
    oo = getOutline(data)
    dd = 0
    pts = getPtsAsNumpy(oo)
    for k1 in range(len(pts)):
        for k2 in range(k1+1, len(pts)):
            dx = ftk.distTwoPoints(pts[k1], pts[k2])
            if dx > dd:
                dd = dx
    return dd


def appendPolyData(data1, data2):
    appendFilter = vtk.vtkAppendPolyData()
    appendFilter.AddInputData(data1)
    # appendFilter.SetInputData(data1)
    appendFilter.AddInputData(data2)
    # appendFilter.SetInputData(data2)
    appendFilter.Update()
    return appendFilter.GetOutput()


def appendPolyDataList(dataList):
    if len(dataList) == 1:
        return dataList[0]
    appendFilter = vtk.vtkAppendPolyData()
    for iData in dataList:
        appendFilter.AddInputData(iData)
    appendFilter.Update()
    return appendFilter.GetOutput()


def appendImageList(image_list, appendAxis):
    """Combines images into one ."""
    append_filter = vtk.vtkImageAppend()
    append_filter.SetAppendAxis(appendAxis)  
    for iImage in image_list:
        append_filter.AddInputData(iImage)
    append_filter.Update()
    return append_filter.GetOutput()


def appendUnstructured(dataList):
    appendFilter = vtk.vtkAppendFilter()
    for iData in dataList:
        appendFilter.AddInputData(iData)
    appendFilter.Update()
    return appendFilter.GetOutput()


def mergeTwoImageData(ii1, ii2, newRes, arrayName):
    oo12 = appendPolyData(getOutline(ii1), getOutline(ii2))
    oC = getOutline(oo12)
    iiC = buildRawImageDataFromOutline(oC, newRes)
    A1 = getArrayAsNumpy(filterResampleToDataset(ii1, iiC), arrayName)
    A2 = getArrayAsNumpy(filterResampleToDataset(ii2, iiC), arrayName)
    AA = A1 + A2 / 2.0
    setArrayFromNumpy(iiC, AA, arrayName, SET_SCALAR=True)
    return iiC


def multiblockToList(data):
    listOut = []
    for k1 in range(data.GetNumberOfBlocks()):
        pd = data.GetBlock(k1)
        listOut.append(pd)
    return listOut


def idListToVtkIDs(idsList):
    ids = vtk.vtkIdList()
    for i in idsList:
        ids.InsertNextId(int(i))
    return ids


def extractCells(data, vtkCellIds):
    """ returns unstructuredgrid of output cells """
    if type(vtkCellIds) == list:
        vtkCellIds = idListToVtkIDs(vtkCellIds)
    exCells = vtk.vtkExtractCells()
    exCells.SetInputData(data)
    exCells.SetCellList(vtkCellIds)
    exCells.Update()
    return exCells.GetOutput()


def extractSelection(data, vtkSelection):
    """ Data = vtu, vtkSelection made from vtkSelectionNode, vtkSelection
    """
    extractSelection = vtk.vtkExtractSelection()
    extractSelection.SetInputData(0, data)
    extractSelection.SetInputData(1, vtkSelection)
    extractSelection.Update()
    return extractSelection.GetOutput()


def delCellsByEdgeLength(data, edgeLength):
    """ Delete cells with edges greater than edgeLength
        Returns unstructuredGrid
    """
    allIds = list(range(data.GetNumberOfCells()))
    for k0 in range(data.GetNumberOfCells()):
        for k1 in range(data.GetCell(k0).GetNumberOfEdges()):
            p0 = data.GetCell(k0).GetEdge(k1).GetPoints().GetPoint(0)
            p1 = data.GetCell(k0).GetEdge(k1).GetPoints().GetPoint(1)
            if ftk.distTwoPoints(p0, p1) > edgeLength:
                allIds.remove(k0)
                break
    #
    ids = vtk.vtkIdList()
    for i in allIds:
        ids.InsertNextId(i)
    return extractCells(data, ids)


def delCellsByID(data, IDsToDEL):
    """ Delete cells from list of IDs
        Returns unstructuredGrid
    """
    allIds = list(range(data.GetNumberOfCells()))
    for delID in IDsToDEL:
        allIds.remove(delID)
    # have IDs to keep
    ids = vtk.vtkIdList()
    for i in allIds:
        ids.InsertNextId(i)
    return extractCells(data, ids)


def getPolylineLength(data):
    return ftk.cumulativeDistanceAlongLine(getPtsAsNumpy(data))[-1]


def getLoopSubDivided(data, nLoops):
    loopSubDiv = vtk.vtkLoopSubdivisionFilter()
    loopSubDiv.SetInputData(data)
    loopSubDiv.SetNumberOfSubdivisions(nLoops)
    loopSubDiv.Update()
    return loopSubDiv.GetOutput()


def decimateTris(data, factor):
    dF = vtk.vtkDecimatePro()
    dF.SetInputData(data)
    dF.SetTargetReduction(factor)
    dF.Update()
    return dF.GetOutput()


def shrinkWrapData(data, wrappingData=None, DEFAULT_WRAP_RES=100):
    """

    :param data:
    :param wrappingData: if None - then just make a sphere larger
    :return: wrapped data
    """
    sw = vtk.vtkSmoothPolyDataFilter()
    if wrappingData is None:
        X = data.GetCenter()
        R = np.max(ftk.distPointPoints(X, getPtsAsNumpy(data)))
        wrappingData = buildSphereSource(X, R*2.0, DEFAULT_WRAP_RES)
    sw.SetSourceData(data)
    sw.SetInputData(wrappingData)
    sw.Update()
    return sw.GetOutput()


def poissonRecon(data, depth=9):
    surface = vtk.vtkPoissonReconstruction()
    surface.SetDepth(depth)

    sampleSize = data.GetNumberOfPoints() * .00005
    if (sampleSize < 10):
        sampleSize = 10
    if (data.GetPointData().GetNormals()):
        surface.SetInputData(data)
    else:
        #  "Estimating normals using PCANormalEstimation" 
        normals = vtk.vtkPCANormalEstimation()
        normals.SetInputData(data)
        normals.SetSampleSize(sampleSize)
        normals.SetNormalOrientationToGraphTraversal()
        normals.FlipNormalsOff()
        surface.SetInputConnection(normals.GetOutputPort())
    surface.Update()
    return surface.GetOutput()


def pointCloudRemoveOutliers(data):
    locator = vtk.vtkStaticPointLocator()
    locator.SetDataSet(data)
    locator.BuildLocator()
    removal = vtk.vtkStatisticalOutlierRemoval()
    removal.SetInputData(data)
    removal.SetLocator(locator)
    removal.SetSampleSize(20)
    removal.SetStandardDeviationFactor(1.5)
    removal.GenerateOutliersOn()
    removal.Update()
    pp = removal.GetOutput()
    return buildPolydataFromXYZ(getPtsAsNumpy(pp))

def smoothTris(data, iterations=200):
    sF = vtk.vtkSmoothPolyDataFilter()
    sF.SetInputData(data)
    sF.SetNumberOfIterations(iterations)
    sF.Update()
    return sF.GetOutput()

def smoothTris_SINC(data, iterations=20):
    pass_band = 0.001
    feature_angle = 60.0
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputData(data)
    smoother.SetNumberOfIterations(iterations)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(feature_angle)
    smoother.SetPassBand(pass_band)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOff()
    smoother.Update()
    return smoother.GetOutput()

def filterExtractEdges(data):
    ee = vtk.vtkExtractEdges()
    ee.SetInputData(data)
    ee.Update()
    return ee.GetOutput()

def isPolyDataWaterTight(data):
    alg = vtk.vtkFeatureEdges()
    alg.FeatureEdgesOff()
    alg.BoundaryEdgesOn()
    alg.NonManifoldEdgesOff()
    alg.SetInputDataObject(data)
    alg.Update()
    is_water_tight = alg.GetOutput().GetNumberOfCells() < 1
    return is_water_tight

def isPolyDataPolyLine(data):
    for k1 in range(data.GetNumberOfCells()):
        aa = data.GetCell(k1).IsA('vtkPolyLine')
        if not aa:
            return False # if find any non-line - return false
    return True


def calculatePolyDataArea(vtpdata):  # latest version will allow compute on polydata
    nCells = vtpdata.GetNumberOfCells()
    A = 0.0
    for k1 in range(nCells):
        try:
            A += vtpdata.GetCell(k1).ComputeArea()
        except AttributeError:
            # This deals with case of polyline representing the ROI
            return calculatePolyDataArea(buildPolyTrianglesAtCp(getPtsAsNumpy(vtpdata)))
    return A

def getPolyDataCenterPtNormal(data, refNorm=None):
    """ return 2x np array center point, normal for each tri in poly data
    """
    nCells = data.GetNumberOfCells()
    cp, norm = [], []
    for k1 in range(nCells):
        iCell = data.GetCell(k1)
        centerPt, normal = __getTriangleCenterAndNormal(iCell)
        cp.append(centerPt)
        if refNorm is not None:
            normal = ftk.setVecAConsitentWithVecB(np.array(normal), refNorm)
        norm.append(normal)
    return np.array(cp), np.array(norm)

def addMagnitudeArray(data, vecArrayName, vecArrayNameOut):
    magA = np.sqrt(np.sum(np.power(getArrayAsNumpy(data, vecArrayName), 2.0), axis=-1))
    setArrayFromNumpy(data, magA, vecArrayNameOut)


def addNormalVelocities(data, normal, vecArrayName, vecArrayNameOut):
    """ Will add scalar array of normal velocity magnitude
        output array: fDC.varNameVelocityNormal
    """
    normal = normal / np.linalg.norm(normal)
    velArray = getArrayAsNumpy(data, vecArrayName)
    vN = np.dot(velArray, normal)
    setArrayFromNumpy(data, vN, vecArrayNameOut)
    return data


def filterDilateErode(imData, kernal, valDilate, valErode):
    # if binary then for dilate set valDilate=1, valErode=0
    #                for erode  set valDilate=0, valErode=1
    try:
        len(kernal)
    except TypeError:
        kernal = [kernal,kernal,kernal]
    dilateErode = vtk.vtkImageDilateErode3D()
    dilateErode.SetInputData(imData)
    dilateErode.SetDilateValue(valDilate)
    dilateErode.SetErodeValue(valErode)
    dilateErode.SetKernelSize(kernal[0], kernal[1], kernal[2])
    dilateErode.Update()
    return dilateErode.GetOutput()


def filterExtractSurface(data):
    geometryFilter = vtk.vtkGeometryFilter()
    geometryFilter.SetInputData(data)
    geometryFilter.Update()
    return geometryFilter.GetOutput()


def filterExtractTri(data):
    ss = filterExtractSurface(data)
    return filterTriangulate(ss)


def filterTriangulate(data):
    triFilter = vtk.vtkTriangleFilter()
    triFilter.SetInputData(data)
    triFilter.Update()
    return triFilter.GetOutput()


def getVolumeSurfaceAreaOfPolyData(data):
    data = filterTriangulate(data)
    massFilter = vtk.vtkMassProperties()
    massFilter.SetInputData(data)
    massFilter.Update()
    return (massFilter.GetVolume(), massFilter.GetSurfaceArea())


def mergeSurfsByPointsInsideVti(surf1: Union[vtk.vtkDataObject, list], surf2=None, res=0.001):
    """An alternative "boolean union" method. 

    Args:
        surf1 (Union[vtk.vtkDataObject, list]): surfA or list of surfaces to bool union
        surf2 (vtk.vtkDataObject, optional): surfB. Defaults to None if surfA is list.
        res (float, optional): resolution to perform merging. Defaults to 0.001.

    Returns:
        vtk.vtkDataObject: merged surface as polydata. 
    """
    if type(surf1) == list:
        ppfull = appendPolyDataList(surf1)
    else:
        ppfull = appendPolyData(surf1, surf2)
        surf1 = [surf1, surf2]
    oo = getOutline(ppfull)
    ii = buildRawImageDataFromOutline(oo, res, pad=5)
    for k1, iSurf in enumerate(surf1):
        tf1 = filterGetEnclosedPts(ii, iSurf, 'tf')
        if k1 == 0:
            A = tf1
        else:
            A = A|tf1
    A = np.reshape(A, ii.GetDimensions(), 'F')
    addNpArray(ii, A.astype(float), 'Inside', SET_SCALAR=True, IS_3D=True)
    return getConnectedRegionLargest(contourFilter(ii, 0.5))


# ======================================================================================================================
#           TRIANGLE AREA & NORMAL
# ======================================================================================================================
def getTriangleAreaAndNormal(triCell):
    # return area_float, normal_float3
    cellPts = triCell.GetPoints()
    area = triCell.ComputeArea()
    normal = [0, 0, 0]
    triCell.ComputeNormal(cellPts.GetPoint(0), cellPts.GetPoint(1), cellPts.GetPoint(2), normal)
    return (area, normal)


def __getTriangleCenterAndNormal(triCell):
    # return area_float, normal_float3
    cellPts = triCell.GetPoints()
    # cp = triCell.GetCenter()
    cp = np.mean((cellPts.GetPoint(0), cellPts.GetPoint(1), cellPts.GetPoint(2)), 0)
    normal = [0, 0, 0]
    triCell.ComputeNormal(cellPts.GetPoint(0), cellPts.GetPoint(1), cellPts.GetPoint(2), normal)  # this is mag 1.0
    return (cp, normal)


def addNormalsToPolyData(data, REV=False, SPLITTING=True, MANIFOLD=True):
    """
    Add normals to polydata.
    This is a wrapper around vtkPolyDataNormals.
    See the vtk documentation for more details.

    :param data: vtkPolyData
    :param REV: bool - reverse normals
    :param SPLITTING: bool - split normals
    :param MANIFOLD: bool - manifold normals
    :return: vtkPolyData with normals
    """
    normFilter = vtk.vtkPolyDataNormals()
    normFilter.SetInputData(data)
    normFilter.SetFeatureAngle(60.0)
    normFilter.SetNonManifoldTraversal(int(MANIFOLD))
    normFilter.AutoOrientNormalsOn()
    normFilter.SetSplitting(int(SPLITTING))
    if REV:
        normFilter.FlipNormalsOn()
    normFilter.Update()
    return normFilter.GetOutput()


# ======================================================================================================================
#           EDGES
# ======================================================================================================================
def getBoundaryEdges(data):
    """
    Get boundary edges of polydata.
    This is a wrapper around vtkFeatureEdges.
    See the vtk documentation for more details.

    :param data: vtkPolyData
    :return: vtkPolyData with boundary edges
    """
    fef = vtk.vtkFeatureEdges()
    fef.SetInputData(data)
    fef.BoundaryEdgesOn()
    fef.ManifoldEdgesOff()
    fef.NonManifoldEdgesOff()
    fef.FeatureEdgesOff()
    fef.Update()
    return fef.GetOutput()


def getEdges(data, FEATURE=False):
    fef = vtk.vtkFeatureEdges()
    fef.SetInputData(data)
    fef.BoundaryEdgesOn()
    fef.ManifoldEdgesOn()
    fef.NonManifoldEdgesOn()
    if FEATURE:
        fef.FeatureEdgesOn()
    else:
        fef.FeatureEdgesOff()
    fef.Update()
    return fef.GetOutput()


def getConnectedCellIds(dataMesh, searchId):
    connectedCells = vtk.vtkIdList()
    dataMesh.BuildLinks()
    dataMesh.GetPointCells(searchId, connectedCells)
    return connectedCells

# ======================================================================================================================
#           VOLUME FILTERS
# ======================================================================================================================
def extractStructuredSubGrid(data, ijkMinMax=None, sampleRate=(1, 1, 1), TO_INCLUDE_BOUNDARY=False):
    """
    Extract a structured subgrid from a vtkDataObject.
    This is a wrapper around vtkExtractGrid.
    See the vtk documentation for more details.

    :param data: vtkDataObject
    :param ijkMinMax: tuple of ints - min and max indices
    :param sampleRate: tuple of ints - sample rate
    :param TO_INCLUDE_BOUNDARY: bool - include boundary
    :return: vtkDataObject
    """
    if type(sampleRate) == int:
        sampleRate = (sampleRate, sampleRate, sampleRate)
    if ijkMinMax is None:
        ijkMinMax = data.GetExtent()
    if isinstance(data, vtk.vtkImageData):
        return extractVOI(data, ijkMinMax, sampleRate=sampleRate)
    extractGrid = vtk.vtkExtractGrid()
    extractGrid.SetInputData(data)
    extractGrid.SetVOI(ijkMinMax[0], ijkMinMax[1], ijkMinMax[2], ijkMinMax[3],
                       ijkMinMax[4], ijkMinMax[5])
    extractGrid.SetSampleRate(sampleRate[0], sampleRate[1], sampleRate[2])
    if TO_INCLUDE_BOUNDARY:
        extractGrid.IncludeBoundaryOn()
    extractGrid.Update()
    return extractGrid.GetOutput()


def extractVOI(data, ijkMinMax=None, sampleRate=(1, 1, 1)):
    """
    Extract a volume of interest from a vtkImageData.
    This is a wrapper around vtkExtractVOI.
    See the vtk documentation for more details.

    :param data: vtkImageData
    :param ijkMinMax: tuple of ints - min and max indices
    :param sampleRate: tuple of ints - sample rate
    :return: vtkDataObject
    """
    extractGrid = vtk.vtkExtractVOI()
    extractGrid.SetInputData(data)
    if ijkMinMax is None:
        ijkMinMax = data.GetExtent()
    extractGrid.SetVOI(ijkMinMax[0], ijkMinMax[1], ijkMinMax[2], ijkMinMax[3],
                       ijkMinMax[4], ijkMinMax[5])
    extractGrid.SetSampleRate(sampleRate[0], sampleRate[1], sampleRate[2])
    # extractGrid.IncludeBoundaryOn()
    extractGrid.Update()
    return extractGrid.GetOutput()


def extractVOI_fromFov(data, fovData):
    """
    Extract a volume of interest from a vtkImageData.
    This is a wrapper around vtkExtractVOI.
    See the vtk documentation for more details.
    Locally this runs extractVOI using the bounds of the fovData.

    :param data: vtkImageData
    :param fovData: vtkDataObject - volume of interest
    :return: vtkImageData
    """
    fovData = cleanData(fovData) # To prevent surprises
    bounds = fovData.GetBounds()
    if isVTS(data):
        extent = data.GetExtent()
        points = data.GetPoints()
        dims = __getDimensions(data)
        # Initialize min/max indices
        imin, imax = extent[1], extent[0]
        jmin, jmax = extent[3], extent[2]
        kmin, kmax = extent[5], extent[4]
        # Check each point
        for i in range(extent[0], extent[1]+1):
            for j in range(extent[2], extent[3]+1):
                for k in range(extent[4], extent[5]+1):                    
                    idx = (k - extent[4]) * dims[0] * dims[1] + \
                         (j - extent[2]) * dims[0] + \
                         (i - extent[0])
                    point = points.GetPoint(idx)
                    if (point[0] >= bounds[0] and point[0] <= bounds[1] and
                        point[1] >= bounds[2] and point[1] <= bounds[3] and
                        point[2] >= bounds[4] and point[2] <= bounds[5]):
                        imin = min(imin, i)
                        imax = max(imax, i)
                        jmin = min(jmin, j)
                        jmax = max(jmax, j)
                        kmin = min(kmin, k)
                        kmax = max(kmax, k)
        return extractStructuredSubGrid(data, [imin, imax, jmin, jmax, kmin, kmax])
    bb = []
    for k1 in [0, 1]:
        for k2 in [2, 3]:
            for k3 in [4, 5]:
                pt = [bounds[k1], bounds[k2], bounds[k3]]
                bb.append(pt)
    ti, tj, tk = [9999e90, 0], [9999e90, 0], [9999e90, 0]
    for X in bb:
        ijk = [0, 0, 0]
        pp = [0, 0, 0]
        data.ComputeStructuredCoordinates(X, ijk, pp)
        for k0, tt in zip(ijk, [ti, tj, tk]):
            tt[0] = min(tt[0], k0)
            tt[1] = max(tt[1], k0)
    tijk = [ti[0], ti[1], tj[0], tj[1], tk[0], tk[1]]
    return extractVOI(data, tijk)


def filterNullOutsideSurface(vtkObj, surfObj, arrayListToNull=None, tfArray=None):
    """
    Null out arrays outside a surface.
    This uses filterGetPointsInsideSurface to get a mask and then nulls out arrays outside the surface.
    See the vtk documentation for more details.

    :param vtkObj: vtkImageData or similar - data to null
    :param surfObj: vtkPolyData - surface
    :param arrayListToNull: list of strings - arrays to null
    :param tfArray: numpy array - mask
    :return: vtkPolyData
    """
    if tfArray is None:
        tfArray = np.array(filterGetPointsInsideSurface(vtkObj, surfObj))
    if arrayListToNull is None:
        arrayListToNull = getArrayNames(vtkObj)
    for iA in arrayListToNull:
        aO = getArrayAsNumpy(vtkObj, iA)
        aO = np.multiply(aO.T, tfArray)
        # aO *= tfA[:,np.newaxis]
        # print aO.shape
        addNpArray(vtkObj, aO.T, iA)
    return vtkObj


def filterNullInsideSurface(vtkObj, surfObj, arrayListToNull=None, nullVal=0.0):
    """
    Null out arrays inside a surface.
    This uses filterGetPointsInsideSurface to get a mask and then nulls out arrays inside the surface.
    See the vtk documentation for more details.

    :param vtkObj: vtkImageData or similar - data to null
    :param surfObj: vtkPolyData - surface
    :param arrayListToNull: list of strings - arrays to null
    :param nullVal: float - value to null
    :return: vtkPolyData
    """
    tfA = np.array(filterGetPointsInsideSurface(vtkObj, surfObj))
    if arrayListToNull is None:
        arrayListToNull = getArrayNames(vtkObj)
    for iA in arrayListToNull:
        a0 = getArrayAsNumpy(vtkObj, iA)
        a0[tfA==1] = nullVal
        # aO = np.multiply(aO.T, tfA)
        # aO *= tfA[:,np.newaxis]
        # print aO.shape
        addNpArray(vtkObj, a0.T, iA)
    return vtkObj


# ======================================================================================================================
#           RESAMPLE
# ======================================================================================================================
def filterResampleToDataset(src, destData, PASS_POINTS=False):
    """
    Resample data from src onto destData
    This is a wrapper around vtkProbeFilter.
    See the vtk documentation for more details.

    :param src: source vtkObj
    :param destData: destination vtkObj
    :param PASS_POINTS: bool [False] set true to pass point data from 'destData' to output
    :return: destData with interpolated point data from src
    """
    pf = vtk.vtkProbeFilter()
    pf.SetInputData(destData)
    pf.SetSourceData(src)
    if PASS_POINTS:
        pf.PassPointArraysOn()
    pf.Update()
    return pf.GetOutput()


def filterResampleToImage(vtsObj, dims=None, bounder=None):
    """
    Resample a vtkStructuredGrid or similar to an image.
    This is a wrapper around vtkResampleToImage.
    See the vtk documentation for more details.

    :param vtsObj: vtkStructuredGrid or similar
    :param dims: tuple of ints - dimensions of image. Default is to use the bounds of the vtsObj and calculated resolution.
    :param bounder: vtkPolyData - bounding box. Default is to use the bounds of the vtsObj.
    :return: vtkImageData
    """
    rif = vtk.vtkResampleToImage()
    rif.SetInputDataObject(vtsObj)
    if dims is None:
        outline = getOutline(vtsObj)
        res = getVtsResolution(vtsObj)
        img = buildRawImageDataFromOutline(outline, min(res), pad=0)
        return filterResampleToDataset(vtsObj, img)
    try:
        _ = dims[0]
    except TypeError:
        dims = [dims, dims, dims]
    if bounder is not None:
        rif.UseInputBoundsOff()
        rif.SetSamplingBounds(bounder.GetBounds())
    else:
        rif.UseInputBoundsOn()
    rif.SetSamplingDimensions(dims[0],dims[1],dims[2])

    rif.Update()
    return rif.GetOutput()


def getAxesDirectionCosinesForNormal(normalVector, guidingVector=None):
    """
    A good option is to set guidingVec to None for first and then to u for all others
    :param normalVector:
    :param guidingVector:
    :return:
    """
    if guidingVector is None:
        if (abs(normalVector[0]) >= abs(normalVector[1])):
            factor = 1.0 / np.sqrt(normalVector[0] * normalVector[0] + normalVector[2] * normalVector[2])
            u0 = -normalVector[2] * factor
            u1 = 0.0
            u2 = normalVector[0] * factor
        else:
            factor = 1.0 / np.sqrt(normalVector[1] * normalVector[1] + normalVector[2] * normalVector[2])
            u0 = 0.0
            u1 = normalVector[2] * factor
            u2 = -normalVector[1] * factor
        u = np.array([u0, u1, u2])
    else:
        u = ftk.getVectorComponentNormalToRefVec(guidingVector, normalVector)
        if np.isnan(u[0]):
            u = guidingVector
        u = u / np.linalg.norm(u)
    v = np.cross(normalVector, u)
    return u, v, normalVector



def filterResliceImage(vtiObj, X, normalVector, guidingVector=None,
                       slabNumberOfSlices=1,
                       LINEAR_INTERPOLATION=False, MIP=False,
                       OUTPUT_DIM=2):
    """
    This returns a reslice
        add .GetOutput() to get the slice as imagedata
    EXAMPLE:
            ii = vtkfilters.filterResliceImage(vtiObj, X, n, [0,0,1])
            iI = ii.GetOutput()
            axT = ii.GetResliceAxes()
            c = contourFilter(iI, 450)
            c = filterTransformPolyData(c, matrix=axT)
    :param vtiObj: vtiObject to reslice
    :param X: loaction of slice center
    :param normalVector: normal vector defining slice
    :param guidingVector: 3_tuple - inplane vector to define slice x-axis [default None - will choose]
    :param slabNumberOfSlices: int - to make a thick slice [default=1]
    :param LINEAR_INTERPOLATION: bool - set true to have linear interpolation [default cubic]
    :param MIP: bool - set true for thick slice to show MIP [default mean]
    :param OUTPUT_DIM: int - set 3 for volume [default 2]
    :return: vtk.vtkImageReslice object
    """
    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(vtiObj)
    reslice.SetOutputDimensionality(OUTPUT_DIM)
    if OUTPUT_DIM == 3:
        ss = vtiObj.GetSpacing()
        reslice.SetOutputSpacing(ss[0], ss[1], ss[2]*slabNumberOfSlices)
        reslice.SetSlabSliceSpacingFraction(1.0/slabNumberOfSlices)
    reslice.AutoCropOutputOn()
    u, v, normalVector = getAxesDirectionCosinesForNormal(normalVector, guidingVector)
    reslice.SetResliceAxesDirectionCosines(u, v, normalVector)
    reslice.SetResliceAxesOrigin(X)
    if LINEAR_INTERPOLATION:
        reslice.SetInterpolationModeToLinear()
    else:
        reslice.SetInterpolationModeToCubic()
    reslice.SetSlabNumberOfSlices(slabNumberOfSlices)
    if MIP:
        reslice.SetSlabModeToMax() # default is mean
    reslice.Update()
    return reslice


def filterVtiMedian(vtiObj, filterKernalSize=3):
    mf = vtk.vtkImageMedian3D()
    mf.SetInputData(vtiObj)
    mf.SetKernelSize(filterKernalSize,filterKernalSize,filterKernalSize)
    mf.Update()
    return mf.GetOutput()


def filterImageGradient(data, arrayNameToCalcGradient, outputArrayName=None):
    """ 
    Calculate the gradient of an image array.
    (du/dx, du/dy, du/dz, dv/dx, dv/dy, dv/dz, dw/dx, dw/dy, dw/dz)

    :param data: vtkImageData
    :param arrayNameToCalcGradient: string - name of array to calculate gradient
    :param outputArrayName: string - name of output array (default is arrayNameToCalcGradient + '-Gradient')

    :return: vtkImageData with gradient array
    """
    if outputArrayName is None:
        outputArrayName = arrayNameToCalcGradient + '-Gradient'
    gradientFilter = vtk.vtkGradientFilter()
    gradientFilter.SetInputData(data)
    gradientFilter.SetInputArrayToProcess(0, 0, 0, 0, arrayNameToCalcGradient)
    gradientFilter.SetResultArrayName(outputArrayName)
    gradientFilter.Update()
    return gradientFilter.GetOutput()


# def anisotropicDiffusion(vtiObj):
#     filtAD = vtk.vtkImageAnisotropicDiffusion3D()
#     filtAD.SetInputData(vtiObj)
#     filtAD.CornersOn()
#     filtAD.SetNumberOfIterations(5)
#     filtAD.SetDiffusionFactor(0.10)
#     filtAD.SetDiffusionThreshold(10)
#     filtAD.Update()
#     return filtAD.GetOutput()

def filterSurfaceToImageStencil(vtiObj, surf3D, fill_value=1):
    # Create stencil from surface
    poly_to_stencil = vtk.vtkPolyDataToImageStencil()
    poly_to_stencil.SetInputData(surf3D)
    poly_to_stencil.SetOutputOrigin(vtiObj.GetOrigin())
    poly_to_stencil.SetOutputSpacing(vtiObj.GetSpacing())
    poly_to_stencil.SetOutputWholeExtent(vtiObj.GetExtent())
    poly_to_stencil.Update()
    # Create image from stencil
    stencil_to_image = vtk.vtkImageStencilToImage()
    stencil_to_image.SetInputConnection(poly_to_stencil.GetOutputPort())
    stencil_to_image.SetOutsideValue(0)
    stencil_to_image.SetInsideValue(fill_value)
    stencil_to_image.SetOutputScalarType(vtk.VTK_UNSIGNED_CHAR)
    stencil_to_image.Update()
    stencilImage = stencil_to_image.GetOutput()
    return stencilImage


def filterMaskImageBySurface(vtiObj, surf3D, fill_value=1, arrayName="LabelMap"):
    """
    Create a binary mask from a VTK image and a closed surface. 
    The mask is added as an array to the input image.
    
    Args:
        image_data: vtkImageData - The reference image that defines the output dimensions and spacing
        surface: vtkPolyData - The closed surface to create mask from
        fill_value: Value to use for the mask (default=1)
        arrayName: Name of the array to use for the mask (default="LabelMap")
    Returns:
        vtkImageData with same dimensions as input but containing binary mask
    """
    stencilImage = filterSurfaceToImageStencil(vtiObj, surf3D, fill_value=fill_value)
    # Add mask as array to input image
    if arrayName not in getArrayNames(vtiObj):
        addNpArray(vtiObj, getArrayAsNumpy(stencilImage, getScalarsArrayName(stencilImage)), arrayName)
    else:
        A = getArrayAsNumpy(vtiObj, arrayName)
        AS = getArrayAsNumpy(stencilImage, getScalarsArrayName(stencilImage))
        A[AS==fill_value] = fill_value
        setArrayFromNumpy(vtiObj, A, arrayName)
    return vtiObj


def filterGetPointsInsideSurface(data, surfaceData):
    """
    classify points as inside(t) or outside(f)
    :param data: vtkObj
    :param surfaceData: closed polydata
    :return: list of true=INSIDE false=OUTSIDE
    """
    return filterGetEnclosedPts(data, surfaceData, 'tf')
def filterGetPointIDsInsideSurface(vtkObj, surf3D):
    return filterGetEnclosedPts(vtkObj, surf3D, 'ID')
def filterGetPolydataInsideSurface(vtkObj, surf3D):
    return filterGetEnclosedPts(vtkObj, surf3D, 'POLYDATA')
def filterGetEnclosedPts(vtkObj, surf3D, RETURNTYPE="POLYDATA", tol=0.0000000001):
    """
    Get all pts from vtkObj enclosed by surface.
    :param vtkObj: A vtkObj
    :param surf3D: A closed polydata surface
    :param RETURNTYPE: string - Options: 'POLYDATA' | 'tf' | 'ID'
    :param tol: default [0.00001]
    :return: polydata of points | np.array of true/false | list of IDs
    """
    try:
        tol = np.min(vtkObj.GetSpacing()) * 0.0001
    except AttributeError:
        tol=tol
    enclosedPts = vtk.vtkSelectEnclosedPoints()
    enclosedPts.SetInputData(vtkObj)
    enclosedPts.SetSurfaceData(surf3D)
    enclosedPts.SetTolerance(tol)
    # enclosedPts.SetCheckSurface(1)
    enclosedPts.Update()
    if RETURNTYPE.lower() == "polydata":
        vtkpts = vtk.vtkPoints()
        for i in range(vtkObj.GetNumberOfPoints()):
            if enclosedPts.IsInside(i):
                vtkpts.InsertNextPoint(vtkObj.GetPoint(i))
        # Create a new vtkPolyData to hold the inside points
        vtkpts_pd = vtk.vtkPolyData()
        vtkpts_pd.SetPoints(vtkpts)
        return vtkpts_pd
        # tt = filterThreshold(enclosedPts.GetOutput(), "SelectedPoints", 0.5, 2)
        # return polyDataFromVtkObj(tt)
    elif RETURNTYPE.lower() == "tf":
        selectedA = getArrayAsNumpy(enclosedPts.GetOutput(), "SelectedPoints")
        return selectedA > 0.5
    elif RETURNTYPE.lower() == "id":
        selectedA = getArrayAsNumpy(enclosedPts.GetOutput(), "SelectedPoints")
        tf = selectedA > 0.5
        return np.squeeze(np.argwhere(tf))
    return enclosedPts.GetOutput()

def filterGetArrayValuesWithinSurface(data, surf3D, arrayName):
    A = getArrayAsNumpy(data, arrayName=arrayName)
    ids2 = filterGetPointIDsInsideSurface(data, surf3D=surf3D)
    return A[ids2]


def getDataWithThreshold(data, thresholdArrayName, thresholdLower, thresholdUpper):
    """
    Get data within a threshold.
    This is a wrapper around vtkThreshold.
    See the vtk documentation for more details.

    :param data: vtkImageData or similar
    :param thresholdArrayName: string - name of array to threshold
    :param thresholdLower: float - lower threshold
    :param thresholdUpper: float - upper threshold
    :return: vtkUnstructuredGrid
    """
    thresholder = vtk.vtkThreshold()
    thresholder.SetInputData(data)
    thresholder.SetLowerThreshold(thresholdLower)
    thresholder.SetUpperThreshold(thresholdUpper)
    thresholder.SetInputArrayToProcess(0, 0, 0, 0, thresholdArrayName)
    thresholder.Update()
    return thresholder.GetOutput()


def countPointsInVti(vtiObj, objWithPoints, npArray=None, countArrayName="count", weightingArray=None):
    """
    Add cell array "count" to vti with count of points from objWithPoints per cell
        
    
    :param vtiObj: vtkImageData or similar
    :param objWithPoints: vtkPolyData or similar
    :param npArray: numpy array - array to add count points to. default None
    :param countArrayName: string - name of array to add - default "count"
    :param weightingArray: string - name of array to weight points by - default None
    :return: vtkImageData with count array
    """
    cellLocator = vtk.vtkCellLocator()
    cellLocator.SetDataSet(vtiObj)
    cellLocator.BuildLocator()
    if getArrayId(vtiObj, countArrayName, pointData=False) is None:
        A = np.zeros(vtiObj.GetNumberOfCells())
    else:
        A = getArrayAsNumpy(vtiObj, countArrayName, pointData=False)
    if weightingArray is not None:
        weightingArray = getArrayAsNumpy(objWithPoints, weightingArray)
    else:
        weightingArray = np.ones(objWithPoints.GetNumberOfPoints())
    for i in range(objWithPoints.GetNumberOfPoints()):
        x = objWithPoints.GetPoints().GetPoint(i)
        cellId = cellLocator.FindCell(x)
        if npArray is None:
            A[cellId]+=1 * weightingArray[i]
        else:
            A[cellId]+=npArray[i] * weightingArray[i]
    setArrayFromNumpy(vtiObj, A, countArrayName, pointData=False)
    vtiObj = cellToPointData(vtiObj)
    setArrayAsScalars(vtiObj, countArrayName)
    return vtiObj






# ======================================================================================================================
#           VTK CONNECTED REGION FILTERS
# ======================================================================================================================
def __getConnectedRegionLargest_UnStruct(data: vtk.vtkDataObject) -> vtk.vtkPolyData:
    connectFilter = vtk.vtkConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToLargestRegion()
    connectFilter.AddSpecifiedRegion(1)
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionLargest(data: vtk.vtkDataObject) -> vtk.vtkPolyData:
    """
    Get the largest connected region from a vtkDataObject.
    
    :param data: vtkDataObject
    :return: vtkPolyData
    """
    if not data.IsA('vtkPolyData'):
        return __getConnectedRegionLargest_UnStruct(data)
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToLargestRegion()
    connectFilter.AddSpecifiedRegion(1)
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionContaining(data: vtk.vtkDataObject, vtkId: int) -> vtk.vtkPolyData:
    """
    Get the connected region containing a given vtkId.
    
    :param data: vtkDataObject
    :param vtkId: int
    :return: vtkPolyData
    """
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.AddSeed(vtkId)
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionClosestToX(data: vtk.vtkDataObject, X: np.ndarray) -> vtk.vtkDataObject:
    """
    Get the connected region closest to a given point.
    
    :param data: vtkDataObject
    :param X: numpy array - point coordinates
    :return: vtkDataObject - vtkPolyData or vtkUnstructuredGrid
    """
    if isinstance(data, vtk.vtkUnstructuredGrid):
        return getConnectedRegionClosestToX_UnStruct(data, X)
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToClosestPointRegion()
    connectFilter.SetClosestPoint(X[0], X[1], X[2])
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionClosestToX_UnStruct(data: vtk.vtkDataObject, X: np.ndarray) -> vtk.vtkDataObject:
    connectFilter = vtk.vtkConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToClosestPointRegion()
    connectFilter.SetClosestPoint(X[0], X[1], X[2])
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionAll(data: vtk.vtkDataObject, minPts: Optional[int] = None) -> List[vtk.vtkPolyData]:
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToSpecifiedRegions()
    connectFilter.InitializeSpecifiedRegionList()
    output, c1 = [], 0
    while True:
        connectFilter.AddSpecifiedRegion(c1)
        connectFilter.Update()
        thisRegion = vtk.vtkPolyData()
        thisRegion.DeepCopy(connectFilter.GetOutput())
        if thisRegion.GetNumberOfCells() <= 0:
            break
        output.append(thisRegion)
        connectFilter.DeleteSpecifiedRegion(c1)
        c1 += 1
    ##
    output = [cleanData(i, DO_POINT_MERGING=False) for i in output]
    if minPts is not None:
        output = [i for i in output if i.GetNumberOfPoints() >= minPts]
    outputS = sorted(output, key=lambda pp : pp.GetNumberOfPoints(), reverse=True)
    return outputS


def getConnectedRegionMinDistToX(data: vtk.vtkDataObject, X: np.ndarray, minNPts: int = 10) -> vtk.vtkPolyData:
    """
    Like closest to X - but min dist on pt by pt (rather than closest center point
    :param data:
    :param X:
    :param minNPts: default 10
    :return:
    """
    allRegions = getConnectedRegionAll(data, minNPts)
    ID = 0
    minDD = np.min(ftk.distPointPoints(X, getPtsAsNumpy(allRegions[0])))
    for k1 in range(1, len(allRegions)):
        dd = np.min(ftk.distPointPoints(X, getPtsAsNumpy(allRegions[k1])))
        if dd < minDD:
            minDD = dd
            ID = k1
    return allRegions[ID]




