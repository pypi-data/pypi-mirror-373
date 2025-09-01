# -*- coding: utf-8 -*-

"""
@author: Fraser M. Callaghan

Input / Output functions
"""


import os
import sys
import numpy as np
import unicodedata as ud
import pickle
import string
import json
from datetime import date, datetime, timedelta
import codecs
import csv
import shutil
import vtk
from vtk.util import numpy_support # type: ignore
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from typing import List, Dict, Union, Optional, Tuple
import tarfile

def remove_symbols(text: str) -> str:
    """
    Remove symbols from the given text.

    Args:
        text (str): The input text to process.

    Returns:
        str: The text with symbols removed.
    """
    return ''.join(c for c in text if ud.category(c) != 'So')

def remove_not_allowed(text: str, allowed_characters: str = string.printable + 'ßöüäéèà') -> str:
    """
    Remove characters that are not in the allowed set.

    Args:
        text (str): The input text to process.
        allowed_characters (str): The set of characters to keep (default is all printable characters and some special (DE, FR) characters).

    Returns:
        str: The text with disallowed characters removed.
    """
    return "".join(c for c in text if c in allowed_characters)

# =========================================================================
##          Utilities
# =========================================================================
def countFilesInDir(dirName: str) -> int:
    """
    Count the number of files in a directory.

    Args:
        dirName (str): The path to the directory.

    Returns:
        int: The number of files in the directory.
    """
    files = []
    if os.path.isdir(dirName):
        for _, _, filenames in os.walk(dirName):  
            files.extend(filenames)
    return len(files)

def getAllFilesUnderDir(dirName: str) -> List[str]:
    """
    Get all file paths under a directory.

    Args:
        dirName (str): The path to the directory.

    Returns:
        List[str]: A list of full file paths.
    """
    files = []
    if os.path.isdir(dirName):
        for path, _, filenames in os.walk(dirName):
            for ifile in filenames:
                files.append(os.path.join(path, ifile))
    return files

def parseFileToTagsDictionary(fileName: str, equator: str = '=', commentor: str = '#', SPACE_REPLACE: bool = True) -> Dict[str, str]:
    """
    Parse a file to a dictionary of tags.

    Args:
        fileName (str): The name of the file to parse.
        equator (str, optional): The character used to separate keys and values. Defaults to '='.
        commentor (str, optional): The character used to denote comments. Defaults to '#'.
        SPACE_REPLACE (bool, optional): Whether to replace spaces in keys with underscores. Defaults to True.

    Returns:
        dict: A dictionary containing the parsed tags and values.

    Notes:
        - If the file ends with '.json', it will be parsed as a JSON file instead.
        - Comments at the beginning of the file are stored under the 'header' key.
        - Subsequent comments are stored as 'comment0', 'comment1', etc.
        - Empty lines and lines without the equator character are ignored.
        - Keys and values are stored as strings.
    """
    if fileName.endswith('json'):
        return parseJsonToDictionary(fileName)
    myDict, commentNumber = {'header': ''}, 0
    HEADER_FLAG = True
    try:
        with open(fileName, 'r') as f:
            for lineIn in f:
                if (len(lineIn) > 1):
                    if (lineIn[0] == commentor):  #  comments
                        if HEADER_FLAG:
                            myDict['header'] = myDict['header'] + lineIn
                        else:
                            myDict['comment%d'%(commentNumber)] = lineIn[1:]
                            commentNumber += 1
                    else:
                        HEADER_FLAG = False
                        myEquals = lineIn.find(equator)             # Find = sign
                        if myEquals < 0:
                            continue
                        else:
                            myKey = lineIn[:myEquals].strip()
                            if SPACE_REPLACE:
                                myKey = myKey.replace(' ', '_')
                            myValue = lineIn[myEquals+1:].strip()
                            myValue = myValue.rstrip('\n')
                            myDict[myKey] = myValue
    except IOError:
        raise
    if myDict['header'] == '':
        myDict.pop('header')
    return myDict


def writeDictionaryToFile(fileName: str, dictToWrite: Dict[str, str], equator: str = '=', commentor: str = '#', WRITE_COMMENTS: bool = True) -> str:
    """
    Write a dictionary to a file.

    Args:
        fileName (str): The name of the file to write to (if json then calls writeDictionaryToJSON - json.dump with Numpy encoder).
        dictToWrite (dict): The dictionary to write to the file.
        equator (str, optional): The character used to separate keys and values. Defaults to '='.
        commentor (str, optional): The character used to denote comments. Defaults to '#'.
        WRITE_COMMENTS (bool, optional): Whether to write comments to the file. Defaults to True.

    Returns:
        str: The name of the file written to.
    """
    if fileName.endswith('json'):
        return writeDictionaryToJSON(fileName, dictToWrite)
    with open(fileName, 'w') as fid:
        try:
            fid.write('%s'%(dictToWrite['header']))
        except KeyError:
            pass # no header
        for iKey in sorted(dictToWrite.keys()):
            if 'comment' in iKey.lower():
                if WRITE_COMMENTS:
                    fid.write('%s %s\n'%(commentor, remove_not_allowed(str(dictToWrite[iKey]))))
            elif iKey.lower() == 'header':
                continue
            else:
                fid.write('%s %s %s\n'%(iKey, equator, remove_not_allowed(str(dictToWrite[iKey]))))
        return fileName


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.floating, np.complexfloating)):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bytes_):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return str(obj)
        if isinstance(obj, (np.ndarray, list)):
            return [x.item() if isinstance(x, (np.integer, np.floating)) else x for x in obj]
        if obj is None:
            return "None"  # Convert None to string
        # Handle some bespoke general cases
        if hasattr(obj, "to_dict"):  
            return json.dumps(obj.to_dict())
        elif hasattr(obj, "dict"):  
            return json.dumps(obj.dict())
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):  # Convert iterables like lists/tuples
            return json.dumps(list(obj))
        return super(NumpyEncoder, self).default(obj)


def writeDictionaryToJSON(fileName: str, dictToWrite: Dict[str, str]) -> str:
    with open(fileName, 'w') as fp:
        json.dump(dictToWrite, fp, indent=4, sort_keys=True, cls=NumpyEncoder, ensure_ascii=False)
    return fileName


def parseJsonToDictionary(fileName: str) -> Dict[str, str]:
    with open(fileName, 'r') as fid:
        myDict = json.load(fid)
    return myDict


def strListToFloatList(strList: str) -> List[float]:
    """
    Convert a string representation of a list to a list of floats.

    Args:
        strList (str): A string representation of a list of numbers.

    Returns:
        List[float]: A list of float values.
    """
    strList = strList.replace("[","")
    strList = strList.replace("]","")
    return [float(i) for i in strList.split(",")]

def xmlIndent(elem: ET.Element, level: int = 0) -> None:
    """
    Indent an XML element for pretty printing.

    Args:
        elem (ET.Element): The XML element to indent.
        level (int, optional): The current indentation level. Defaults to 0.
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xmlIndent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def __buildFileName(prefix: str, idNumber: int, extn: str, number_of_digits: int = 6) -> str:
    """
    Build a file name from a prefix, ID number, and extension.

    Args:
        prefix (str): The prefix of the file name.
        idNumber (int): The ID number of the file.
        extn (str): The extension of the file.

    Returns:
        str: The file name.
    """
    ids = f'{idNumber:0{number_of_digits}d}'
    if extn[0] != '.':
        extn = '.' + extn
    fileName = prefix + '_' + ids + extn
    return fileName

def findAndReplaceTextInFile(fileIn: str, txtFind: str, txtReplace: str) -> str:
    """
    Find and replace text in a file.

    Args:
        fileIn (str): The input file path.
        txtFind (str): The text to find.
        txtReplace (str): The text to replace with.

    Returns:
        str: The path of the modified file.
    """
    with open(fileIn, 'r') as fid:
        fileData = fid.read()
    fileData = fileData.replace(txtFind, txtReplace)
    with open(fileIn, 'w') as fid:
        fid.write(fileData)
    return fileIn

def readFileToListOfLines(fileName: str, commentSymbol: str = '#') -> List[List[str]]:
    """
    Read a file and return a list of each line.

    Args:
        fileName (str): The path of the file to read.
        commentSymbol (str, optional): The symbol used to denote comments. Defaults to '#'.

    Returns:
        List[List[str]]: A list of lines from the file.

    Notes:
        - Will split on "," if present
        - Will skip starting with #
    """
    with open(fileName, 'r') as fid:
        lines = fid.readlines()
    lines = [l.strip('\n') for l in lines]
    lines = [l for l in lines if len(l) > 0]
    lines = [l for l in lines if l[0]!=commentSymbol]
    lines = [l.split(',') for l in lines]
    return lines
 
def appendFiles(listOfFiles: List[str], carriageReturn: str = '') -> str:
    """
    Append the contents of multiple text files into a single string.

    Args:
        listOfFiles (list): A list of file names to append.
        carriageReturn (str, optional): The string to append after each file's content. Defaults to an empty string.

    Returns:
        str: A single string containing the concatenated contents of all files.
    """
    allText = ''
    for iFile in listOfFiles:
        with open(iFile, 'r') as fid:
            fileData = fid.read()
            allText = allText + fileData + carriageReturn
    return allText

def pickleData(data, pickleFileName: str) -> str:
    """
    Pickle data to a file.

    Args:
        data: The data to pickle.
        pickleFileName (str): The name of the file to pickle to.

    Returns:
        str: The name of the file written to.
    """
    with open(pickleFileName, 'wb') as fid:
        pickle.dump(data, fid, protocol=2)
    return pickleFileName

def unpickleData(pickleFileName: str):
    """
    Unpickle data from a file.

    Args:
        pickleFileName (str): The name of the file to unpickle.

    Returns:
        The unpickled data.
    """
    opts = {}
    if sys.version_info[0] == 3:
        opts = {"encoding":'latin1'}
    with open(pickleFileName, 'rb') as fid:
        return pickle.load(fid, **opts)


def tarGZLocal_AndMove(dirToTarZip: str, tarGZFileName: str, localLocation: str, remoteLocation: Optional[str] = None) -> None:
    """
    Compress and move a directory to a local location and optionally to a remote location.
    Uses Python's tarfile module for cross-platform compatibility.

    Args:
        dirToTarZip (str): The directory to compress and zip.
        tarGZFileName (str): The name of the compressed file.
        localLocation (str): The local location to move the compressed file.
        remoteLocation (str, optional): The remote location to move the compressed file. Defaults to None.
    """
    # Get the parent directory and target directory name
    parent_dir = os.path.dirname(dirToTarZip)
    target_dir = os.path.basename(dirToTarZip)
    output_file = os.path.join(localLocation, tarGZFileName)
    
    # Create tar.gz archive
    with tarfile.open(output_file, "w:gz") as tar:
        # Change to parent directory to get relative paths
        original_dir = os.getcwd()
        os.chdir(parent_dir)
        try:
            tar.add(target_dir)
        finally:
            os.chdir(original_dir)
    
    if remoteLocation is not None:
        shutil.copy(output_file, remoteLocation)
        os.unlink(output_file)


# =========================================================================
# =========================================================================
def addSuffixToName(fileName: str, suffix: str) -> str:
    """
    Add a suffix to the end of a file name (retains extn).

    Args:
        fileName (str): The name of the file to modify.
        suffix (str): The suffix to add to the file name.

    Returns:
        str: The modified file name.
    """
    fileName, fileExt = os.path.splitext(fileName)
    fSplit = fileName.split('_')
    number = fSplit[-1]
    return fileName.replace('_' + number, suffix + '_' + number) + fileExt

def checkIfExtnPresent(fileName: str, extn: str) -> str:
    """
    Check if the extension of a file name is present and add it if it is not.

    Args:
        fileName (str): The name of the file to check.
        extn (str): The extension to check for.

    Returns:
        str: The modified file name with the extension added if it was not present.
    """
    if (extn[0] == '.'):
        extn = extn[1:]

    le = len(extn)
    if (fileName[-le:] != extn):
        fileName = fileName + '.' + extn
    return fileName


# =========================================================================
##          CSV interface
# =========================================================================

def readDataCSV(csvFile: str, nHeaderLines: int = 0, quotechar: str = '"', decimalChar: str = ".", delimeterToUse: Optional[str] = None) -> Tuple[List[str], List[List[str]]]:
    """
    Read data from a CSV file.

    Args:
        csvFile (str): The path of the CSV file to read.
        nHeaderLines (int, optional): The number of header lines to skip. Defaults to 0.
        quotechar (str, optional): The character used to quote fields. Defaults to '"'.
        decimalChar (str, optional): The character used to denote decimal points. Defaults to '.'.
        delimeterToUse (str, optional): The delimiter to use. If not specified, it will be detected automatically.

    Returns:
        Tuple[List[str], List[List[str]]]: A tuple containing the headers and the data.

    Notes:
        - Assumes Headers: then cols of floats
        - Try to automatically determine detectDelimiter
        - Read file (skip header lines)
        Return last headers row as list of headers (if so) & list of lists of each row
        Can pass output to np.array() then have columns of data
            e.g. : data = np.array(data, dtype=float)
    """
    def __fixDecimal(irow: List[str]) -> List[str]:
        if decimalChar != ".":
            rowOut = []
            for ii in irow:
                i2 = ii.replace(decimalChar, ".")
                try:
                    float(i2)
                    rowOut.append(i2)
                except ValueError:
                    rowOut.append(ii)
            return rowOut
        return irow
    
    def doReading(delimeterToUse_: str, headers: List[str], infile, nHeaderLines: int, quotechar: str) -> Tuple[List[str], List[List[str]]]:
        reader = csv.reader(infile, delimiter=delimeterToUse_, quotechar=quotechar)
        # ASSUME ALWAYS SAME ROW FORMAT
        rowsList = []
        rowCount = 0
        for row in reader:
            rowCount += 1
            if rowCount <= nHeaderLines:
                headers = row
                continue
            row = __fixDecimal(row)
            rowsList.append(row)
        return headers, rowsList
    if delimeterToUse is None:
        try:
            delimeterToUse = detectDelimiter(csvFile, nHeaderLines)
        except UnicodeDecodeError:
            delimeterToUse = detectDelimiter(csvFile, nHeaderLines, 'utf16')
    headers = []
    try:
        with open(csvFile, 'rU') as infile:
            headers, rowsList = doReading(delimeterToUse, headers, infile, nHeaderLines, quotechar)
    except (csv.Error, UnicodeDecodeError):
        with codecs.open(csvFile, 'rU', 'utf-16') as infile:
            headers, rowsList = doReading(delimeterToUse, headers, infile, nHeaderLines, quotechar)
    return headers, rowsList


def writeCSVFile(data: List[List[str]], header: List[str], csvFile: str, FIX_NAN: bool = False) -> str:
    """
    Write data to a CSV file.

    Args:
        data (List[List[str]]): The data to write to the CSV file.
        header (List[str]): The header for the CSV file.
        csvFile (str): The path of the CSV file to write to.
        FIX_NAN (bool, optional): Whether to fix NaN values. Defaults to False.

    Returns:
        str: The path of the CSV file written to.
    """
    with open(csvFile, 'w') as fout:
        csvWriter = csv.writer(fout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #first write column headers
        if header is not None:
            csvWriter.writerow(header)
        for iRow in data:
            if FIX_NAN:
                iRow = ['' if i=='nan' else i for i in iRow]
            csvWriter.writerow(iRow)
    return csvFile


def detectDelimiter(csvFile: str, nHeader: int = 0, encoding: Optional[str] = None) -> str:
    """
    Detect the delimiter used in a CSV file.

    Args:
        csvFile (str): The path of the CSV file to detect the delimiter of.
        nHeader (int, optional): The number of header lines to skip. Defaults to 0.
        encoding (str, optional): The encoding of the file. Defaults to None.

    Returns:
        str: The detected delimiter.
    """
    with open(csvFile, 'r', encoding=encoding) as myCsvfile:
        c0 = 0
        for row in myCsvfile:
            while c0 <= nHeader:
                c0 += 1
                continue
            if row.find(",")!=-1:
                return ","
            if row.find(";")!=-1:
                return ";"
            if row.find("\t")!=-1:
                return "\t"
    return ","


# =========================================================================
##          PLY interface
# =========================================================================

def writePlyFile(fullfileName: str, xyzPoints: List[List[float]], uvwPoints: Optional[List[List[float]]] = None, comment: List[str] = ["Written via fIO module"], header: bool = True) -> str:
    """
    Write points and norms to PLY file
    :param fullfileName:
    :param xyzPoints:
    :param uvwPoints:
    :param comment:
    :param header:
    :return:
    """
    # FORMAT EXAMPLE :
    # ply
    # format ascii 1.0           { ascii/binary, format version number }
    # comment made by Greg Turk  { comments keyword specified, like all lines }
    # comment this file is a cube
    # element vertex 8           { define "vertex" element, 8 of them in file }
    # property float x           { vertex contains float "x" coordinate }
    # property float y           { y coordinate is also a vertex property }
    # property float z           { z coordinate, too }
    # element face 6             { there are 6 "face" elements in the file }
    # property list uchar int vertex_index { "vertex_indices" is a list of ints }
    # end_header                 { delimits the end of the header }
    # 0 0 0                      { start of vertex list }
    # 0 0 1
    # 0 1 1
    # 0 1 0
    # 1 0 0
    # 1 0 1
    # 1 1 1
    # 1 1 0
    # 4 0 1 2 3                  { start of face list }
    # 4 7 6 5 4
    # 4 0 4 5 1
    # 4 1 5 6 2
    # 4 2 6 7 3
    # 4 3 7 4 0
    # -------------------
    nPts = len(xyzPoints)
    with open(fullfileName, 'w') as fid:
        if header:
            fid.write('ply\n')
            fid.write('format ascii 1.0\n')
            for icomment in comment:
                fid.write('comment ' + icomment + '\n')
            fid.write('element vertex %d\n' % (nPts))
            fid.write('property float x\n')
            fid.write('property float y\n')
            fid.write('property float z\n')
            if uvwPoints is not None:
                fid.write('property float nx\n')
                fid.write('property float ny\n')
                fid.write('property float nz\n')
            fid.write('end_header\n')

        if uvwPoints is not None:
            for k in range(nPts):
                fid.write('%.7f %.7f %.7f %.7f %.7f %.7f\n' % \
                          (xyzPoints[k][0], xyzPoints[k][1], xyzPoints[k][2], \
                           uvwPoints[k][0], uvwPoints[k][1], uvwPoints[k][2]))
        else:
            for k in range(nPts):
                fid.write('%.7f %.7f %.7f\n' % \
                          (xyzPoints[k][0], xyzPoints[k][1], xyzPoints[k][2]))
        #
    #
    return fullfileName



# =========================================================================
## vtkIO and PVD interface
# =========================================================================
def writeVTKFile(data: vtk.vtkDataObject, fileName: str, STL_ASCII: bool = False) -> str:
    """
    Writes a VTK object to a file. Uses the extension to determine the type of file to write.

    Args:
        data (vtk.vtkDataObject): The VTK object to write to a file.
        fileName (str): The full file name to write to.
        STL_ASCII (bool, optional): Set to True to write STL file in ASCII [default False -> write binary] (only used for STL).

    Returns:
        str: The full file name.
    """
    writer = None
    fileName = str(fileName)
    if fileName.endswith('vtp'):
        writer = vtk.vtkXMLPolyDataWriter()
    elif fileName.endswith('vts'):
        writer = vtk.vtkXMLStructuredGridWriter()
    elif fileName.endswith('vtu'):
        writer = vtk.vtkXMLUnstructuredGridWriter()
    elif fileName.endswith('stl'):
        writer = vtk.vtkSTLWriter()
        if STL_ASCII:
            writer.SetFileTypeToASCII()
        else:
            writer.SetFileTypeToBinary()
    elif fileName.endswith('vti'):
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetDataModeToBinary()
    elif fileName.endswith('mhd'):
        writer = vtk.vtkMetaImageWriter()
    elif fileName.endswith('mha'):
        writer = vtk.vtkMetaImageWriter()
    elif fileName.endswith('nii'):
        return writeNifti(data, fileName)
    ##
    if not writer:
        raise IOError('Extension not recognised (%s)'%(fileName))
    writer.SetFileName(fileName)
    writer.SetInputData(data)
    writer.Write()
    return fileName


def readVTKFile(fileName: str) -> vtk.vtkDataObject:
    """
    Read a VTK file - the extension is used to determine the type of file to read.

    Args:
        fileName (str): The path of the VTK file to read.

    Returns:
        vtk.vtkDataObject: The VTK data object.
    """
    if not os.path.isfile(fileName):
        raise IOError('## ERROR: %s file not found'%(fileName))
    if fileName.endswith('vtp'):
        reader = vtk.vtkXMLPolyDataReader()
    elif fileName.endswith('vts'):
        reader = vtk.vtkXMLStructuredGridReader()
    elif fileName.endswith('vtu'):
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif fileName.endswith('stl'):
        reader = vtk.vtkSTLReader()
        reader.ScalarTagsOn()
    elif fileName.endswith('nii') or fileName.endswith('nii.gz'):
        reader = vtk.vtkNIFTIImageReader()
    elif fileName.endswith('vti'):
        reader = vtk.vtkXMLImageDataReader()
    elif fileName.endswith('vtk'):
        reader = vtk.vtkPolyDataReader()
    elif fileName.endswith('vtm'):
        reader = vtk.vtkXMLMultiBlockDataReader()
    elif fileName.endswith('nrrd'):
        reader = vtk.vtkNrrdReader()
    elif fileName.endswith('mha') or fileName.endswith('mhd'):
        reader = vtk.vtkMetaImageReader()
    elif fileName.endswith('png'):
        reader = vtk.vtkPNGReader()
    elif fileName.endswith('jpg') or fileName.endswith('jpeg'):
        reader = vtk.vtkJPEGReader()
    elif fileName.endswith('tif') or fileName.endswith('tiff'):
        reader = vtk.vtkTIFFReader()
    elif fileName.endswith('ply'):
        reader = vtk.vtkPLYReader()
    elif fileName.endswith('pvd'):
        raise IOError(' PVD - should use readPVD()')
    else:
        raise IOError(fileName + ' not correct extension')
    reader.SetFileName(fileName)
    reader.Update()
    return reader.GetOutput()


# =========================================================================
def writeNifti(data: vtk.vtkDataObject, fileName: str) -> str:
    """
    Write a NIfTI file.

    Args:
        data (vtk.vtkDataObject): The VTK data object to write.
        fileName (str): The path of the NIfTI file to write to.

    Returns:
        str: The path of the NIfTI file written to.
    """
    writer = vtk.vtkNIFTIImageWriter()
    writer.SetFileName(fileName)
    writer.SetInputData(data)
    writer.Write()
    return fileName

def readNifti(fileName: str) -> vtk.vtkDataObject:
    """
    Read a NIfTI file.

    Args:
        fileName (str): The path of the NIfTI file to read.

    Returns:
        vtk.vtkDataObject: The VTK data object.
    """
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(fileName)
    reader.Update()
    return reader.GetOutput()

def readNRRD(fileName: str) -> vtk.vtkDataObject:
    """
    Read a NRRD file.

    Args:
        fileName (str): The path of the NRRD file to read.

    Returns:
        vtk.vtkDataObject: The VTK data object.
    """
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(fileName)
    reader.Update()
    return reader.GetOutput()
# =========================================================================


# =========================================================================
##          PVD Stuff
# =========================================================================
def _writePVD(rootDirectory: str, filePrefix: str, outputSummary: Dict[int, Dict[str, Union[str, float]]]) -> str:
    """
    Write a PVD file. For internal use only.

    Args:
        rootDirectory (str): The root directory.
        filePrefix (str): The file prefix.
        outputSummary (Dict[int, Dict[str, Union[str, float]]]): The output summary.
    """
    fileOut = os.path.join(rootDirectory, filePrefix + '.pvd')
    with open(fileOut, 'w') as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
        f.write('<Collection>\n')
        for timeId in sorted(outputSummary.keys()):
            sTrueTime = outputSummary[timeId]['TrueTime']
            tFileName = str(outputSummary[timeId]['FileName'])
            f.write('<DataSet timestep="%7.5f" file="%s"/>\n' % (sTrueTime, tFileName))
        f.write('</Collection>\n')
        f.write('</VTKFile>')
    return fileOut


def _makePVDOutputDict(vtkDict: Dict[Union[str, float], vtk.vtkDataObject], filePrefix: str, fileExtn: str, subDir: str = '') -> Dict[int, Dict[str, Union[str, float]]]:
    """
    Make a PVD output dictionary. For internal use only.

    Args:
        vtkDict (Dict[Union[str, float], vtk.vtkDataObject]): The dictionary of VTK data objects.
        filePrefix (str): The file prefix.
        fileExtn (str): The file extension.
        subDir (str, optional): The subdirectory. Defaults to ''.

    Returns:
        Dict[int, Dict[str, Union[str, float]]]: The output summary.
    """
    outputSummary = {}
    myKeys = vtkDict.keys()
    myKeys = sorted(myKeys)
    for timeId in range(len(myKeys)):
        fileName = __buildFileName(filePrefix, timeId, fileExtn)
        trueTime = myKeys[timeId]
        outputMeta = {'FileName': os.path.join(subDir, fileName), 'TimeID': timeId, 'TrueTime': trueTime}
        outputSummary[timeId] = outputMeta
    return outputSummary

def __writePVDData(vtkDict: Dict[Union[str, float], vtk.vtkDataObject], rootDir: str, filePrefix: str, fileExtn: str, subDir: str = '') -> None:
    """
    Write PVD data. For internal use only.

    Args:
        vtkDict (Dict[Union[str, float], vtk.vtkDataObject]): The dictionary of VTK data objects.
        rootDir (str): The root directory.
        filePrefix (str): The file prefix.
        fileExtn (str): The file extension.
        subDir (str, optional): The subdirectory. Defaults to ''.
    """
    myKeys = vtkDict.keys()
    myKeys = sorted(myKeys)
    for timeId in range(len(myKeys)):
        fileName = __buildFileName(filePrefix, timeId, fileExtn)
        fileOut = os.path.join(rootDir, subDir, fileName)
        if type(vtkDict[myKeys[timeId]]) == str:
            os.rename(vtkDict[myKeys[timeId]], fileOut)
        else:
            writeVTKFile(vtkDict[myKeys[timeId]], fileOut)

def writeVTK_PVD_Dict(vtkDict: Dict[Union[str, float], vtk.vtkDataObject], rootDir: str, filePrefix: str, fileExtn: str, BUILD_SUBDIR: bool = True) -> str:
    """
    Write dict of time:vtkObj to pvd file
        If dict is time:fileName then will copy files

    Args:
        vtkDict (Dict[Union[str, float], vtk.vtkDataObject]): The dictionary of VTK data objects.
        rootDir (str): The root directory.
        filePrefix (str): make filePrefix.pvd
        fileExtn (str): file extension (e.g. vtp, vti, vts etc)
        BUILD_SUBDIR (bool, optional): to build subdir (filePrefix.pvd in root, then data in root/filePrefix/). Defaults to True.
    
    Returns:
        str: full file name
    """
    filePrefix = os.path.splitext(filePrefix)[0]
    subDir = ''
    fullPVD = os.path.join(rootDir, checkIfExtnPresent(filePrefix, 'pvd'))
    if os.path.isfile(fullPVD) & (type(list(vtkDict.values())[0]) != str):
        deleteFilesByPVD(fullPVD, QUIET=True)
    if BUILD_SUBDIR:
        subDir = filePrefix
        if not os.path.isdir(os.path.join(rootDir, subDir)):
            os.mkdir(os.path.join(rootDir, subDir))
    outputSummary = _makePVDOutputDict(vtkDict, filePrefix, fileExtn, subDir)
    __writePVDData(vtkDict, rootDir, filePrefix, fileExtn, subDir)
    return _writePVD(rootDir, filePrefix, outputSummary)


def pvdAddTimeToFieldData(pvdf_or_vtkDict: Union[str, Dict[Union[str, float], vtk.vtkDataObject]]) -> Union[str, Dict[Union[str, float], vtk.vtkDataObject]]:
    """
    Add time to field data.

    Args:
        pvdf_or_vtkDict (Union[str, Dict[Union[str, float], vtk.vtkDataObject]]): The PVD file path or dictionary of VTK data objects.

    Returns:
        Union[str, Dict[Union[str, float], vtk.vtkDataObject]]: The PVD file path or dictionary of VTK data objects.
    """
    rr, ff, ee = pvdGetDataFileRoot_Prefix_and_Ext(pvdf_or_vtkDict)
    pvdf_or_vtkDict = readPVD(pvdf_or_vtkDict)
    for iTime in sorted(pvdf_or_vtkDict.keys()):
        timeArray = vtk.vtkFloatArray()
        timeArray.SetNumberOfValues(1)
        timeArray.SetValue(0, iTime)
        timeArray.SetName("Time")
        pvdf_or_vtkDict[iTime].GetFieldData().AddArray(timeArray)
    if rr is not None:
        return writeVTK_PVD_Dict(pvdf_or_vtkDict, rr, ff, ee)
    else:
        return pvdf_or_vtkDict



def writeZipFromVTK_PVD_Dict(vtkDict: Dict[Union[str, float], vtk.vtkDataObject], fileExt: str, zipFileOut: str) -> None:
    """
    Write a ZIP file from a dictionary of VTK data objects.

    Args:
        vtkDict (Dict[Union[str, float], vtk.vtkDataObject]): The dictionary of VTK data objects.
        fileExt (str): The file extension.
        zipFileOut (str): The output ZIP file path.
    """
    # first save times to field data
    pvdAddTimeToFieldData(vtkDict)
    # write as normal, then zip, then del.
    r, f = os.path.split(zipFileOut)
    f = os.path.splitext(f)[0]
    pvdOut = writeVTK_PVD_Dict(vtkDict, r, f, fileExt)
    if zipFileOut[-4:] == '.zip':
        zipFileOut = zipFileOut[:-4]
    shutil.make_archive(zipFileOut, 'zip', os.path.join(r, f))
    deleteFilesByPVD(pvdOut)


def deleteFilesByPVD(pvdFile: str, FILE_ONLY: bool = False, QUIET: bool = False) -> int:
    """
    Delete files referenced by a PVD file.

    Args:
        pvdFile (str): The PVD file path.
        FILE_ONLY (bool, optional): Whether to delete only the files. Defaults to False.
        QUIET (bool, optional): Whether to suppress warnings. Defaults to False.

    Returns:
        int: 0 if successful, 1 if error.
    """
    if FILE_ONLY:
        try:
            os.remove(pvdFile)
        except (IOError, OSError):
            print('    warning - file not found %s' % (pvdFile))
            return 1
        return 0
    try:
        pvdDict = readPVDFileName(pvdFile)
        for iKey in pvdDict.keys():
            try:
                os.remove(pvdDict[iKey])
            except OSError:
                pass  # ignore this as may be shared by and deleted by another pvd
        os.remove(pvdFile)
    except (IOError, OSError):
        if (not QUIET)&("pvd" not in pvdFile):
            print('    warning - file not found %s' % (pvdFile))
    try:
        head, _ = os.path.splitext(pvdFile)
        os.rmdir(head)
    except (IOError, OSError):
        if not QUIET:
            print('    warning - dir not found %s' % (head))
    return 0


def readPVDFileName(fileIn: str, vtpTime: float = 0.0, timeIDs: List[int] = [], RETURN_OBJECTS_DICT: bool = False) -> Union[Dict[float, str], Dict[float, vtk.vtkDataObject]]:
    """
    Read PVD file, return dictionary of fullFileNames - keys = time
    So DOES NOT read file
    If not pvd - will return dict of {0.0 : fileName}
    
    Args:
        fileIn: str - PVD file path
        vtpTime: float - time to read
        timeIDs: list of int - time IDs to read
        RETURN_OBJECTS_DICT: bool - return dictionary of vtkDataObjects
    
    Returns:
        dict of fullFileNames - keys = time
    """
    _, ext = os.path.splitext(fileIn)
    if ext != '.pvd':
        if RETURN_OBJECTS_DICT:
            return {vtpTime: readVTKFile(fileIn)}
        else:
            return {vtpTime: fileIn}
    #
    vtkDict = pvdGetDict(fileIn, timeIDs)
    if RETURN_OBJECTS_DICT:
        kk = vtkDict.keys()
        return dict(zip(kk, [readVTKFile(vtkDict[i]) for i in kk]))
    else:
        return vtkDict

def readImageFileToDict(imageFile: str) -> Dict[float, vtk.vtkDataObject]:
    """
    Read an image file and return a dictionary of VTK data objects.

    Args:
        imageFile (str): The image file path.

    Returns:
        Dict[float, vtk.vtkDataObject]: A dictionary of VTK data objects (keys = time).
    """
    return readPVD(imageFile)

def readPVD(fileIn: str, timeIDs: List[int] = []) -> Dict[float, vtk.vtkDataObject]:
    """
    Read a PVD file and return a dictionary of VTK data objects.

    Args:
        fileIn (str): The PVD file path.
        timeIDs (List[int], optional): A list of time step IDs to include. Defaults to an empty list.

    Returns:
        Dict[float, vtk.vtkDataObject]: A dictionary of VTK data objects (keys = time).
    """
    return readPVDFileName(fileIn, timeIDs=timeIDs, RETURN_OBJECTS_DICT=True)

def pvdGetDict(pvd: Union[str, ET.Element, Dict[float, str]], timeIDs: List[int] = []) -> Dict[float, str]:
    """
    Get a dictionary of time steps and their corresponding file names from a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.
        timeIDs (List[int], optional): A list of time step IDs to include. Defaults to an empty list.

    Returns:
        Dict[float, str]: A dictionary mapping time steps to file names.
    """
    if type(pvd) == str:
        root = ET.parse(pvd).getroot()
    elif type(pvd) == dict:
        return pvd
    else:
        root = pvd
    nTSteps = len(root[0])
    if len(timeIDs) == 0:
        timeIDs = range(nTSteps)
    else:
        for k1 in range(len(timeIDs)):
            if timeIDs[k1] < 0:
                timeIDs[k1] = nTSteps + timeIDs[k1]
    pvdTimesFilesDict = {}
    rootDir = os.path.dirname(pvd)
    for k in range(nTSteps):
        if k not in timeIDs:
            continue
        a = root[0][k].attrib
        fullVtkFileName = os.path.join(rootDir, a['file'])
        pvdTimesFilesDict[float(a['timestep'])] = fullVtkFileName
    return pvdTimesFilesDict

def pvdGetClosestTimeToT(pvd: Union[str, ET.Element, Dict[float, str]], T: float) -> float:
    """
    Get the time step closest to a given time from a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.
        T (float): The target time.

    Returns:
        float: The closest time step.
    """
    pvdDict = pvdGetDict(pvd)
    tt = list(sorted((pvdDict.keys())))
    return tt[pvdGetIdOfT(pvdDict, T)]

def pvdGetTimes(pvd: Union[str, ET.Element, Dict[float, str]]) -> List[float]:
    """
    Get a list of time steps from a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.

    Returns:
        List[float]: A list of time steps.
    """
    pvdDict = pvdGetDict(pvd)
    tt = list(sorted((pvdDict.keys())))
    return tt

def pvdGetIdOfT(pvd: Union[str, ET.Element, Dict[float, str]], T: float) -> int:
    """
    Get the ID of the time step closest to a given time from a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.
        T (float): The target time.

    Returns:
        int: The ID of the closest time step.
    """
    pvdDict = pvdGetDict(pvd)
    return np.argmin(abs(np.array(sorted(pvdDict.keys()))-T))

def pvdGetFileAtT(pvd: Union[str, ET.Element, Dict[float, str]], T: float) -> str:
    """
    Get the file name corresponding to the time step closest to a given time from a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.
        T (float): The target time.

    Returns:
        str: The file name corresponding to the closest time step.
    """
    pvdDict = pvdGetDict(pvd)
    return pvdDict[pvdGetClosestTimeToT(pvdDict, T)]

def pvdGetNumberTimePoints(pvd: Union[str, ET.Element, Dict[float, str]]) -> int:
    """
    Get the number of time points in a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.

    Returns:
        int: The number of time points.
    """
    return len(readPVDFileName(pvd).keys())

def pvdGetDataFileRoot_Prefix_and_Ext(pvd: Union[str, ET.Element, Dict[float, str]]) -> Tuple[str, str, str]:
    """
    Get the root directory, prefix, and extension of the data files referenced in a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.

    Returns:
        Tuple[str, str, str]: A tuple containing the root directory, prefix, and extension.
    """
    h, t = os.path.split(pvd)
    t = os.path.splitext(t)[0]
    try:
        ff = pvdGetFileAtT(pvd, 0)
    except FileNotFoundError:
        ff = pvd
    return h, t, os.path.splitext(ff)[1]

def pvdGetDataClosestTo(pvd: Union[str, ET.Element, Dict[float, str]], refT: float) -> vtk.vtkDataObject:
    """
    Get the data object corresponding to the time step closest to a given reference time from a PVD file.

    Args:
        pvd (Union[str, ET.Element, Dict[float, str]]): The PVD file path, XML element, or dictionary.
        refT (float): The reference time.

    Returns:
        vtk.vtkDataObject: The data object corresponding to the closest time step.
    """
    closestT = pvdGetClosestTimeToT(pvd, refT)
    xID = pvdGetIdOfT(pvd, closestT)
    dd = readPVD(pvd, [xID])
    return dd[closestT]

def pvdMultiply(pvdFile: str, nCycles: int, outputFileName: Optional[str] = None) -> str:
    """
    Multiply the time steps in a PVD file by a given number of cycles.

    Args:
        pvdFile (str): The input PVD file path.
        nCycles (int): The number of cycles to multiply the time steps by.
        outputFileName (Optional[str], optional): The output PVD file path. Defaults to None.

    Returns:
        str: The output PVD file path.
    """
    pvdTree = ET.parse(pvdFile)
    collectionTag = pvdTree.find('Collection')
    fileList = []
    timeList = []
    for elem in pvdTree.iter(tag='DataSet'):
        timeList.append(float(elem.attrib['timestep']))
        fileList.append(elem.attrib['file'])
    fileList = [x for (y, x) in sorted(zip(timeList, fileList))]  # @UnusedVariable
    timeList.sort()
    nTS = len(timeList)
    nominalInterval = float(timeList[-1]) + (float(timeList[-1]) - float(timeList[-2]))
    timeMax = (nCycles + 1) * nominalInterval
    try:
        if not (nCycles).is_integer():
            timeMax = nCycles * nominalInterval
            nCycles = int(np.ceil(nCycles))
        else:
            nCycles = int(nCycles)
    except AttributeError:
        pass
    for k1 in range(1, nCycles):
        for k2 in range(nTS):
            newTime = (nominalInterval * k1) + float(timeList[k2])
            timeList.append(str(newTime))
            fileList.append(fileList[k2])
    for i in range(nTS, nTS * (nCycles)):
        elem = ET.Element("DataSet")
        if float(timeList[i]) < timeMax:
            elem.attrib["file"] = fileList[i]
            elem.attrib["timestep"] = timeList[i]
            collectionTag.append(elem)
    if outputFileName is None:
        outputFileName = pvdFile[:-4] + '_' + str(nCycles) + 'cycles.pvd'
    collectionTag = pvdTree.find('Collection');xmlIndent(collectionTag)
    pvdTree.write(outputFileName, 'UTF-8', xml_declaration=True)
    return outputFileName

def pvdReverse(pvdFileIn: str, suffix: str = "REV", outfile: Optional[str] = None) -> str:
    """
    Reverse the time steps in a PVD file.

    Args:
        pvdFileIn (str): The input PVD file path.
        suffix (str, optional): The suffix to append to the output file name. Defaults to "REV".
        outfile (Optional[str], optional): The output file path. Defaults to None.

    Returns:
        str: The output PVD file path.
    """
    pvdFileOut = pvdFileIn[:-4] + suffix + '.pvd'
    pvdTree = ET.parse(pvdFileIn)
    root = pvdTree.find('Collection')
    fileList = []
    timeList = []
    for i in root:
        fileList.append(i.attrib['file'])
        timeList.append(i.attrib['timestep'])
    sortId = np.argsort(np.array(timeList))
    sortRevId = sortId[::-1]
    for i in range(len(root)):
        root[i].attrib['timestep'] = timeList[i]
        root[i].attrib['file'] = fileList[sortRevId[i]]
    root.set('updated', 'yes')
    collectionTag = pvdTree.find('Collection');
    xmlIndent(collectionTag)
    pvdTree.write(pvdFileOut, 'UTF-8', xml_declaration=True)
    if outfile is not None:
        pvdD = readPVD(pvdFileOut)
        _,_,e = pvdGetDataFileRoot_Prefix_and_Ext(pvdFileOut)
        outR, outP = os.path.split(outfile)
        outP = os.path.splitext(outP)[0]
        deleteFilesByPVD(pvdFileOut,FILE_ONLY=True)
        pvdFileOut = writeVTK_PVD_Dict(pvdD, outR, outP, e, True)
    return pvdFileOut

def pvdRestart_t(pvdFile: str, timeStart: float, outputFile: Optional[str] = None) -> str:
    """
    Restart a PVD file from a given time.

    Args:
        pvdFile (str): The input PVD file path.
        timeStart (float): The start time.
        outputFile (Optional[str], optional): The output PVD file path. Defaults to None.

    Returns:
        str: The output PVD file path.
    """
    idStart = pvdGetIdOfT(pvdFile, timeStart)
    return pvdRestart(pvdFile, idStart, outputFile)

def pvdRestart(pvdFile: str, idStart: int, outputFile: Optional[str] = None) -> str:
    """
    Restart a PVD file from a given time step ID.

    Args:
        pvdFile (str): The input PVD file path.
        idStart (int): The start time step ID.
        outputFile (Optional[str], optional): The output PVD file path. Defaults to None.

    Returns:
        str: The output PVD file path.
    """
    pvdTree = ET.parse(pvdFile)
    collectionTag = pvdTree.find('Collection')
    count = -1
    for iDataset in collectionTag.findall('DataSet'):
        count += 1
        if count < idStart:
            collectionTag.remove(iDataset)
    if not outputFile:
        outputFile = pvdFile[:-4] + '_' + str(idStart) + 'start.pvd'
    collectionTag = pvdTree.find('Collection')
    xmlIndent(collectionTag)
    pvdTree.write(outputFile, 'UTF-8', xml_declaration=True)
    return outputFile

def pvdClip(pvdFile: str, idEnd: int, outputFile: Optional[str] = None) -> str:
    """
    Clip a PVD file to a given time step ID.

    Args:
        pvdFile (str): The input PVD file path.
        idEnd (int): The end time step ID.
        outputFile (Optional[str], optional): The output PVD file path. Defaults to None.

    Returns:
        str: The output PVD file path.
    """
    pvdTree = ET.parse(pvdFile)
    collectionTag = pvdTree.find('Collection')
    count = -1
    for iDataset in collectionTag.findall('DataSet'):
        count += 1
        if count > idEnd:
            collectionTag.remove(iDataset)
    if not outputFile:
        outputFile = pvdFile[:-4] + '_' + str(idEnd) + 'end.pvd'
    collectionTag = pvdTree.find('Collection')
    xmlIndent(collectionTag)
    pvdTree.write(outputFile, 'UTF-8', xml_declaration=True)
    return outputFile

def pvdResetTimes(pvdFile: str, startTime: float, endTime: float, pvdFileOut: str) -> str:
    """
    Reset the time steps in a PVD file to a given range.

    Args:
        pvdFile (str): The input PVD file path.
        startTime (float): The start time.
        endTime (float): The end time.
        pvdFileOut (str): The output PVD file path.

    Returns:
        str: The output PVD file path.
    """
    pvdTree = ET.parse(pvdFile)
    root = pvdTree.find('Collection')
    fileList = []
    timeList = []
    newTimes = np.linspace(startTime, endTime, len(root))
    for k1, i in enumerate(root):
        fileList.append(i.attrib['file'])
        timeList.append('%5.5f'%(newTimes[k1]))
    for i in range(len(root)):
        root[i].attrib['timestep'] = timeList[i]
        root[i].attrib['file'] = fileList[i]
    root.set('updated', 'yes')
    collectionTag = pvdTree.find('Collection');
    xmlIndent(collectionTag)
    pvdTree.write(pvdFileOut, 'UTF-8', xml_declaration=True)
    return pvdFileOut

def pvdResetStartPoint_Id(pvdFile: str, startID: int, pvdFileOut: str) -> str:
    """
    Reset the start point of a PVD file to a given time step ID.

    Args:
        pvdFile (str): The input PVD file path.
        startID (int): The start time step ID.
        pvdFileOut (str): The output PVD file path.

    Returns:
        str: The output PVD file path.
    """
    times = list(readPVDFileName(pvdFile).keys())
    startTime =times[startID]
    return pvdResetStartPoint(pvdFile, startTime, pvdFileOut, QUIET=True)

def pvdResetStartPoint(pvdFile: str, startTime: float, pvdFileOut: str, QUIET: bool = True) -> str:
    """
    Reset the start point of a PVD file to a given time.

    Args:
        pvdFile (str): The input PVD file path.
        startTime (float): The start time.
        pvdFileOut (str): The output PVD file path.
        QUIET (bool, optional): Whether to suppress output. Defaults to True.

    Returns:
        str: The output PVD file path.
    """
    pvdTree = ET.parse(pvdFile)
    root = pvdTree.find('Collection')
    fileList = []
    timeList = []
    for i in root:
        fileList.append(i.attrib['file'])
        timeList.append(float(i.attrib['timestep']))
    idStart = int(np.argmin([abs(i-startTime) for i in timeList]))
    if not QUIET:
        print('Ressetting start ID to %d'%(idStart))
    for k1, ID in enumerate(range(idStart, len(root))):
        root[k1].attrib['timestep'] = '%5.5f'%(timeList[k1])
        root[k1].attrib['file'] = fileList[ID]
    for k2 in range(idStart):
        root[k1+1+k2].attrib['timestep'] = '%5.5f'%(timeList[k2+k1+1])
        root[k1+1+k2].attrib['file'] = fileList[k2]
    root.set('updated', 'yes')
    collectionTag = pvdTree.find('Collection');
    xmlIndent(collectionTag)
    pvdTree.write(pvdFileOut, 'UTF-8', xml_declaration=True)
    return pvdFileOut

def pvdAddStartPointAtEndForPeriodicy(pvdFile: str, pvdFileOut: str) -> str:
    """
    Add a start point at the end of a PVD file for periodicity.

    Args:
        pvdFile (str): The input PVD file path.
        pvdFileOut (str): The output PVD file path.

    Returns:
        str: The output PVD file path.
    """
    pvdTree = ET.parse(pvdFile)
    root = pvdTree.find('Collection')
    nSteps = len(root)
    fileList = []
    timeList = []
    for i in root:
        fileList.append(i.attrib['file'])
        timeList.append(float(i.attrib['timestep']))
    fileList.append(root[0].attrib['file'])
    lastTime = timeList[-1] + timeList[-1] - timeList[-2]
    timeList.append(lastTime)
    #
    for iDataset in root.findall('DataSet'):
        root.remove(iDataset)
    #
    for k1 in range(len(fileList)):
        elem = ET.Element("DataSet")
        elem.attrib["file"] = fileList[k1]
        elem.attrib["timestep"] = '%5.5f'%(timeList[k1])
        root.append(elem)
    root.set('updated', 'yes')
    collectionTag = pvdTree.find('Collection');xmlIndent(collectionTag)
    pvdTree.write(pvdFileOut, 'UTF-8', xml_declaration=True)
    return pvdFileOut

def buildPVD_WaterFallRestarts(pvdFileIn: str, pvdFileOut: str, restartEvery: int, nCycle: int = 1, TO_REV: bool = False) -> List[str]:
    """
    Build a waterfall of restarted PVD files.

    Args:
        pvdFileIn (str): The input PVD file path.
        pvdFileOut (str): The output PVD file path.
        restartEvery (int): The number of time steps between restarts.
        nCycle (int, optional): The number of cycles. Defaults to 1.
        TO_REV (bool, optional): Whether to reverse the time steps. Defaults to False.

    Returns:
        List[str]: A list of output PVD file paths.
    """
    h, pvdFileOut = os.path.split(pvdFileOut)
    pvdFileOut = os.path.splitext(pvdFileOut)[0]
    pvdNCycleFile = pvdMultiply(pvdFileIn, nCycle)
    restartIds = range(0, len(readPVDFileName(pvdNCycleFile))-1, restartEvery)
    allFilesList = []
    outputSummary = {}
    for k1 in restartIds:
        if TO_REV:
            ttf = pvdNCycleFile[:-4]+'-R.pvd'
            ttf = pvdRestart(ttf, int(k1))
            outputFile = pvdReverse(ttf, outfile=ttf)
        else:
            outputFile = pvdRestart(pvdNCycleFile, int(k1))
        outputSummary[int(k1)] = {'TrueTime':int(k1), 'FileName':os.path.split(outputFile)[1]}
        allFilesList.append(outputFile)
    wrappingPVDFile = _writePVD(h, pvdFileOut, outputSummary)
    return allFilesList

