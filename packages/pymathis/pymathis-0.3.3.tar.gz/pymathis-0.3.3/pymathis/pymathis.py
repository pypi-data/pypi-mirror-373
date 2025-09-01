import ctypes as ct
from ctypes import wintypes
import os, platform

def LoadDll(DLLPath,C_FILE_Path):
    """
    This function loads and initiates the communication with MATHIS
    :param DLLPath: the is the absolute or relative path to the smartmathis dll
    :param C_FILE: this is the absolute or relative path the case (results are written in the same folder)
    :return: the opened smartmathis dll object
    """
    try: #this try/except is only for debuging process when using the code in an pip unpacked manner
        # Load the DLL depending on the os
        if platform.system() == "Windows":
            dll = ct.CDLL(os.path.join(os.path.dirname(DLLPath),'smartmathis.dll'))
        else:
            dll = ct.CDLL(os.path.join(os.path.dirname(DLLPath), 'smartmathis.so'))
        # Initialize solver
        init_solver(dll,C_FILE_Path)
    except:
        # Load the DLL
        if platform.system() == "Windows":
            dll = ct.CDLL(os.path.join(DLLPath,'smartmathis.dll'))
        else:
            dll = ct.CDLL(os.path.join(DLLPath, 'smartmathis.so'))
        # Initialize solver
        init_solver(dll,C_FILE_Path)
    return dll

def CloseDll(dll):
    """
    The function just closes the .out file so it can be cleaned or used within the same python code
    :param dll: the opened smartmathis dll
    :return: the *.out file is properly closed
    """
    dll.STOP_SMARTMATHIS()
    # the lines below might not be required finally because the dll cleans all variable itself in the last release
    # if platform.system() == "Windows":
    #     handle = dll._handle
    #     del dll
    #     ct.windll.kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
    #     ct.windll.kernel32.FreeLibrary(handle)
    # else:
    #     ct.CDLL("libdl.so.2", mode=ct.RTLD_GLOBAL).dlclose(dll._handle)

def give_passive_ctrl(dll,valuein, tag):
    """
    This function gives the value of each passive controller to mathis
    :param dll: the opened smartmathis dll
    :param valuein: Controller value
    :param tag: Controller index in the mathis passive controllers list
    :return: none
    """
    # Set the argument and return types
    dll.GET_PASSIVE_CTRL_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_int)]
    dll.GET_PASSIVE_CTRL_SMARTMATHIS.restype = None
    tag += 1
    return dll.GET_PASSIVE_CTRL_SMARTMATHIS(ct.c_double(valuein), ct.c_int(tag))

def get_probe_ctrl(dll,tag):
    """
    This function enables to fetch a probe value from mathis
    :param dll: the opened smartmathis dll
    :param tag: the Probe index in the mathis probe controllers list
    :return: the probe value in a numerical format
    """
    # Set the argument and return types
    dll.GIVE_PROBE_CTRL_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_int)]
    dll.GIVE_PROBE_CTRL_SMARTMATHIS.restype = ct.c_double
    tag += 1
    valueout = 0
    valueout = ct.c_double(valueout)
    value_p = ct.pointer(valueout)
    dll.GIVE_PROBE_CTRL_SMARTMATHIS(value_p, ct.c_int(tag))
    return valueout.value

def get_probe_ID(dll,tag):
    """
    This function fetches the Probe's name for each index in mathis' case
    :param dll: the opened smartmathis dll
    :param tag: The probe index in the mathis probe controllers list
    :return: The Probe name in a string format
    """
    # Set the argument and return types
    dll.GIVE_PROBE_ID_SMARTMATHIS.argtypes = [ct.POINTER(ct.ARRAY(ct.c_char,256)), ct.POINTER(ct.c_int)]
    dll.GIVE_PROBE_ID_SMARTMATHIS.restype = ct.POINTER(ct.ARRAY(ct.c_char,256))
    tag += 1
    valueout = ct.create_string_buffer(b'',256)
    value_p = ct.byref(valueout)
    dll.GIVE_PROBE_ID_SMARTMATHIS(value_p, ct.c_int(tag))
    return valueout.value.decode("utf-8").replace(' ','')

def get_passive_ID(dll,tag):
    """
    This function fetches the passiv controller's name for each position in mathis' case
    :param dll: the opened smartmathis dll
    :param tag: the controller index in the mathis passive controllers list
    :return: The controller name in a string format
    """
    # Set the argument and return types
    dll.GIVE_PASSIVE_ID_SMARTMATHIS.argtypes = [ct.POINTER(ct.ARRAY(ct.c_char,256)), ct.POINTER(ct.c_int)]
    dll.GIVE_PASSIVE_ID_SMARTMATHIS.restype = ct.POINTER(ct.ARRAY(ct.c_char,256))
    tag += 1
    valueout = ct.create_string_buffer(b'',256)
    value_p = ct.byref(valueout)
    dll.GIVE_PASSIVE_ID_SMARTMATHIS(value_p, ct.c_int(tag))
    return valueout.value.decode("utf-8").replace(' ','')

def get_passive_number(dll):
    """
    This function gets the total number of passive controllers in mathis case
    :param dll: the opened smartmathis dll
    :return: integer format
    """
    # Set the return type
    dll.GIVE_PASSIVE_NUMBER_SMARTMATHIS.restype = ct.c_int
    return dll.GIVE_PASSIVE_NUMBER_SMARTMATHIS()

def get_probe_number(dll):
    """
    This function gets the total number of probes in mathis case
    :param dll: the opened smartmathis dll
    :return: integer format
    """
    # Set the return type
    dll.GIVE_PROBE_NUMBER_SMARTMATHIS.restype = ct.c_int
    return dll.GIVE_PROBE_NUMBER_SMARTMATHIS()

def init_solver(dll,file):
    """
    This function initiates mathis dll, the *.data is thus validate through this function
    :param dll: the opened smartmathis dll
    :param file: the *.data and associate path
    :return: none or mathis error message if present
    """
    # Set the argument type
    dll.INIT_SOLVER_SMARTMATHIS.argtypes = [ct.c_char_p]
    dll.INIT_SOLVER_SMARTMATHIS(file.encode('utf-8'))

def give_weather(dll,vmeteo = 0.,wdir = 0.,text = 20.,hr = 50.,sunrad = 0.,diffrad = 0.,tsky = 0.,tground = 12.,patm = 101300.):
    """
    This function provides MATHIS with outdoor weather conditions for the next timestep calculation
    :param dll: the opened smartmathis dll
    :param vmeteo: wind speed (m/s)
    :param wdir: wind direction () 
    :param text: air temperature (C)
    :param hr: relative humidity (%)
    :param sunrad: normal direct radiation flux (W/m2
    :param diffrad: horizontal diffuse radiation flux (W/m2)
    :param tsky: equivalent sky vault temperature (C)
    :param tground: ground temperature  at a given depth (C)
    :param patm: atmospheric pressure at reference altitude (Pa)
    :return: none
     """
    dll.GET_METEO_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
    dll.GET_METEO_SMARTMATHIS(ct.c_double(vmeteo),ct.c_double(wdir),ct.c_double(text),ct.c_double(hr),ct.c_double(sunrad),ct.c_double(diffrad),ct.c_double(tsky),ct.c_double(tground),ct.c_double(patm))

def solve_timestep(dll,tasked, dtasked):
    """
    This function asks mathis to solve next time step up to the t+dt
    :param dll: the opened smartmathis dll
    :param tasked: current time (in second)
    :param dtasked: time step (can be different from DTETA in the *.data, but must be in second)
    :return: none
    """
    # Set the argument types
    dll.SOLVE_TIMESTEP_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
    dll.SOLVE_TIMESTEP_SMARTMATHIS(ct.c_double(tasked), ct.c_double(dtasked))

def get_obj_value(dll,objtype,objid,valuename,tag = 0,Verbose = True):
    """
    Function for recovering various quantities calculated by MATHIS without using probe controllers
    :param dll:  the opened smartmathis dll
    :param objtype: type of MATHIS object - currently, only the 'LOC', 'BRANCH' or 'WALL' types are implemented
    :param objid: id of MATHIS object
    :param valuename: name of the asked object value.
        For objtype='LOC': 'DP' (Pa), 'RA' (vol/h), 'RHO' (kg/m3), 'T' (C), 'MH2OLIQ' (kg).
        For objtype='BRANCH':'QV' (m3/h), 'QM' (kg/s), 'RHOFLOW' (kg/m3), 'DPFLOW' (Pa), 'QV1' (m3/h), 'QV2' (m3/h)
        For objtype='WALL': 'TP1', (°C), 'TP2' (°C), 'HRP1' (%), 'HRP2' (%), 'QC1' (W), 'QC2' (W) , 'T' (C), 'HR' (%),  'YW' (kg/kg), 'YWMEAN' (kg/kg), 'XPOS' (m)
    :param tag: index to be considered for certain tabulated quantities (e.g. T, HR, YW, YWMEAN or 'XPOS' of WALL)
    :return: float format
    """
    # Set the argument types
    tag += 1
    dll.GIVE_OBJ_VALUE_SMARTMATHIS.argtypes = [ct.c_char_p,ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_int),ct.POINTER(ct.c_int)]
    dll.GIVE_OBJ_VALUE_SMARTMATHIS.restype = ct.c_double
    err=ct.c_int(0)
    objvalue=dll.GIVE_OBJ_VALUE_SMARTMATHIS(objtype.encode('utf-8'),objid.encode('utf-8'),valuename.encode('utf-8'),ct.c_int(tag),ct.byref(err))
    if err.value != 0 and Verbose:
        print('get_obj_value_smartmathis exited with code error: ',err.value)
        if err.value == 1: print(objtype,' is unknown')
        if err.value == 2: print(objid, ' is unknown')
        if err.value == 3: print(valuename, ' is unknown')
        if err.value == 4: print('tag = ',tag, ' is out of range')
    return objvalue

def get_obj_number(dll,objtype):
    """
    This function gets the total number of objects in mathis case
    :param dll: the opened smartmathis dll
    :param objtype: type of MATHIS object: 'LOC', 'BRANCH','BOUND','WALL','CTRL','HSRC','PERSON','SPEC' or 'CTRL'
    :return: integer format
    """
    dll.GIVE_OBJ_NUMBER_SMARTMATHIS.argtypes = [ct.c_char_p,ct.POINTER(ct.c_int)]
    dll.GIVE_OBJ_NUMBER_SMARTMATHIS.restype = ct.c_int
    err = ct.c_int(0)
    objvalue = dll.GIVE_OBJ_NUMBER_SMARTMATHIS(objtype.encode('utf-8'),ct.byref(err))
    if err.value != 0:
        print('get_obj_number_smartmathis exited with code error: ', err.value,' - ',objtype, ' is unknown')
    return objvalue

def get_obj_ID(dll,objtype, tag=0,Verbose = True):
    """
    This function gets the ID of the object type from the given index in mathis case
    :param dll: the opened smartmathis dll
    :param objtype: type of MATHIS object: 'LOC', 'BRANCH','BOUND','WALL','CTRL','HSRC','PERSON','SPEC' or 'CTRL'
    :param tag: index position of the object type in mathis
    :return: string format or error message with the total number of object type available for the Case
    """
    # Set the argument and return types
    tag += 1
    dll.GIVE_OBJ_ID_SMARTMATHIS.argtypes = [ct.POINTER(ct.ARRAY(ct.c_char, 256)),ct.c_char_p,ct.POINTER(ct.c_int),ct.POINTER(ct.c_int)]
    dll.GIVE_OBJ_ID_SMARTMATHIS.restype = ct.POINTER(ct.ARRAY(ct.c_char,256))
    err = ct.c_int(0)
    valueout = ct.create_string_buffer(b'', 256)
    value_p = ct.byref(valueout)
    dll.GIVE_OBJ_ID_SMARTMATHIS(value_p,objtype.encode('utf-8'), ct.c_int(tag), ct.byref(err))
    if err.value != 0:
        ID = 'Index Error'
        if Verbose:
            print('get_obj_ID_smartmathis exited with code error: ', 1)
            print('Total instances of '+objtype+' is '+str(err.value))
    else:
        ID = valueout.value.decode("utf-8").replace(' ', '')
    return ID

if __name__ == '__main__':
    print('Mathis exchange function')