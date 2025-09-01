"""
this Module creates the different Mathis objects for further assembly in the input *.data file
"""

import os, re, copy, platform, f90nml
from subprocess import check_call
import pymathis.pymathis as pm
import time
import json

# =========================
# Class for MATHIS OBJECTS
# =========================

class Misc():
    """
    Simulation parameters are given in the MISC class
    """

    def __init__(self,**kwargs):
        """
        Misc Object initialization, all default values are loaded and the one given in kwargs are changed
        :param kwargs:
        """
        #initialization is made with the given attributes to be changed
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
        This function returns a dictionary off all modified attributes compared to default values
        """
        list = self.__dict__.keys()
        list2write = [(key, getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['MISC'][key]]
        return dict(list2write)

class Loc():
    """
    LOC object in MATHIS
    """

    def __init__(self, **kwargs):
        # initialization is made with the given attributes to be changed
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
            function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['LOC'][key]]
        return dict(list2write)

class Branch():
    """
    Create a BRANCH object for MATHIS
    """

    def __init__(self, **kwargs):
        """
        initialization is made with the given attributes to be changed
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
        function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['BRANCH'][key]]
        return dict(list2write)

class HSRC():
    """
    Create a HSRC object for MATHIS
    """

    def __init__(self, **kwargs):
        """
        initialization is made with the given attributes to be changed
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
        function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['HSRC'][key]]
        return dict(list2write)

class Person():
    """
    Create a Person (occupant) object for MATHIS
    """

    def __init__(self, **kwargs):
        """
        initialization is made with the given attributes to be changed
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
        function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['PERSON'][key]]
        return dict(list2write)

class Species():
    """
    Create a SPEC object for MATHIS
    """

    def __init__(self, **kwargs):
        """
        initialization is made with the given attributes to be changed"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['SPEC'][key]]
        return dict(list2write)

class Material():
    """
    Create a MAT object for MATHIS
    """

    def __init__(self, **kwargs):
        """
        initialization is made with the given attributes to be changed
        :param kwargs: attributes to be changed

        """

        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
        function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['MAT'][key]]
        return dict(list2write)

class Surf():
    """
    Create a SURF object for MATHIS
    """

    def __init__(self, **kwargs):
        """
        initialization is made with the given attributes to be changed
        :param kwargs: attributes to be changed
        """

        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """
        function to get only the modified attribute compared to the default values
        """
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) !=DefaultMathisInputDict['SURF'][key]]
        return dict(list2write)

class Wall():
    """"
    Create a WALL object for MATHIS
    """

    def __init__(self, **kwargs):
        """initialization is made with the given attributes to be changed"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """function to get only the modified attribute compared to the default values"""
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['WALL'][key]]
        return dict(list2write)

class Ext():
    """Create a EXT object for MATHIS"""

    def __init__(self,**kwargs):
        """initialization is made with the given attributes to be changed"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """function to get only the modified attribute compared to the default values"""
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['EXT'][key]]
        return dict(list2write)

class Bound():
    """Create a BOUND object for MATHIS"""

    def __init__(self,**kwargs):
        """initialization is made with the given attributes to be changed"""
        for key, value in kwargs.items():
            if key != 'Default': setattr(self, key, value)

    def getModifiedValues(self):
        """function to get only the modified attribute compared to the default values"""
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['BOUND'][key]]
        return dict(list2write)

class Ctrl():
    """Create a CTRL object for MATHIS"""

    def __init__(self, **kwargs):
        """initialization is made with the given attributes to be changed"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """function to get only the modified attribute compared to the default values"""
        list = self.__dict__.keys()
        list2write = [(key,getattr(self,key)) for key in list if getattr(self,key) != DefaultMathisInputDict['CTRL'][key]]
        return dict(list2write)

class Mod():
    """Create a Mod object for MATHIS"""

    def __init__(self, **kwargs):
        """initialization is made with the given attributes to be changed"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def getModifiedValues(self):
        """function to get only the modified attribute compared to the default values"""
        list = self.__dict__.keys()
        # MOD can get multiple arguments depending on the dll being used,
        # thus the list2write has to handle non attribute values in the default dict of the class
        list2write = []
        for key in list:
            if key in DefaultMathisInputDict.keys():
                if getattr(self,key) != DefaultMathisInputDict['MOD'][key]: list2write.append((key,getattr(self,key)))
            else:
                list2write.append((key, getattr(self, key)))
        return dict(list2write)

class Building():
    """Creates the building class object that deals with all other Mathis' Objects"""
    def __init__(self,Name, Verbose = True):
        """
        Building Object initialization, if the file Name exists it will be loaded otherwise a new object
        with default values will be created
        :param Name: Building Oject Name, it will be the Name.data file created as Mathis input
        """
        if not Name.endswith('.data') and not Name.endswith('.json'): Name = Name + '.data'
        if not os.path.isfile(Name):
            if Verbose: print("[INFO] No existing file found with name '"+os.path.basename(Name)+"'. A new empty Case is created")
            self.Path2Case = os.getcwd()
            self.Path2Mathis = 'null'
            self.Version = DefaultMathisInputDict['Version']
            a = Misc(**DefaultMathisInputDict['MISC'])
            a.JOBNAME = Name
            self.Misc = a
            self.Ext = Ext(**DefaultMathisInputDict['EXT'])
            self.Loc = {}
            self.Branch = {}
            self.HSRC = {}
            self.Person = {}
            self.Bound = {}
            self.Species = {}
            self.Material = {}
            self.Surf = {}
            self.Wall = {}
            self.Ctrl = {}
            self.Mod = {}
            self.ObjOrder = {}
        else:
            if Name.endswith('.json'):
                CaseDict = loadFromJson(Name)
            else:
                CaseDict = loadExistingFile(Name)
            if Verbose: print('[INFO] Case loaded from file : ' + os.path.basename(Name))
            self.Path2Case = os.path.dirname(Name)
            self.Path2Mathis = 'null'
            self.Version = DefaultMathisInputDict['Version']
            self.ObjOrder = CaseDict['ObjOrder']
            TempDict = makeValueChecks(CaseDict['MISC'] if 'MISC' in CaseDict.keys() else [], 'MISC')
            self.Misc = Misc(**TempDict)
            self.Misc.JOBNAME = os.path.basename(Name)
            if 'EXT' in CaseDict.keys():
                TempDict = makeValueChecks(CaseDict['EXT'], 'EXT')
                self.Ext = Ext(**TempDict)
            self.Loc = {}
            self.Branch = {}
            self.HSRC = {}
            self.Person = {}
            self.Bound = {}
            self.Species = {}
            self.Material = {}
            self.Surf = {}
            self.Wall = {}
            self.Ctrl = {}
            self.Mod = {}
            if 'LOC' in CaseDict.keys():
                if type(CaseDict['LOC']) == list:
                    for a in CaseDict['LOC']:
                        self.addLoc(**a)
                else:
                    self.addLoc(**CaseDict['LOC'])
            if 'BRANCH' in CaseDict.keys():
                if type(CaseDict['BRANCH'])==list:
                    for a in CaseDict['BRANCH']:
                        self.addBranch(**a)
                else:
                    self.addBranch(**CaseDict['BRANCH'])
            if 'HSRC' in CaseDict.keys():
                if type(CaseDict['HSRC'])==list:
                    for a in CaseDict['HSRC']:
                        self.addHSRC(**a)
                else:
                    self.addHSRC(**CaseDict['HSRC'])
            if 'PERSON' in CaseDict.keys():
                if type(CaseDict['PERSON'])==list:
                    for a in CaseDict['PERSON']:
                        self.addPerson(**a)
                else:
                    self.addPerson(**CaseDict['PERSON'])
            if 'BOUND' in CaseDict.keys():
                if type(CaseDict['BOUND'])==list:
                    for a in CaseDict['BOUND']:
                        self.addBound(**a)
                else:
                    self.addBound(**CaseDict['BOUND'])
            if 'SPEC' in CaseDict.keys():
                if type(CaseDict['SPEC'])==list:
                    for a in CaseDict['SPEC']:
                        self.addSpecies(**a)
                else:
                    self.addSpecies(**CaseDict['SPEC'])
            if 'MAT' in CaseDict.keys():
                if type(CaseDict['MAT'])==list:
                    for a in CaseDict['MAT']:
                        self.addMaterial(**a)
                else:
                    self.addMaterial(**CaseDict['MAT'])
            if 'SURF' in CaseDict.keys():
                if type(CaseDict['SURF'])==list:
                    for a in CaseDict['SURF']:
                        self.addSurf(**a)
                else:
                    self.addSurf(**CaseDict['SURF'])
            if 'WALL' in CaseDict.keys():
                if type(CaseDict['WALL'])==list:
                    for a in CaseDict['WALL']:
                        self.addWall(**a)
                else:
                    self.addWall(**CaseDict['WALL'])
            if 'CTRL' in CaseDict.keys():
                if type(CaseDict['CTRL'])==list:
                    for a in CaseDict['CTRL']:
                        self.addCtrl(**a)
                else:
                    self.addCtrl(**CaseDict['CTRL'])
            if 'MOD' in CaseDict.keys():
                if type(CaseDict['MOD'])==list:
                    for a in CaseDict['MOD']:
                        self.addMod(**a)
                else:
                    self.addMod(**CaseDict['MOD'])
    def setMisc(self,**kwargs):
        """
        This function enable to change the Misc Object attributes value
        :param kwargs: any possible attribute of Misc Object
        :return: the new Misc Object with new values
        """
        TempDict = makeValueChecks(kwargs, 'MISC')
        for key, value in TempDict.items():
            setattr(self.Misc, key, value)

    def setExt(self,**kwargs):
        """
        This function enable to change the Ext Object attributes value
        :param kwargs: any possible attribute of Misc Object
        :return: the new Misc Object with new values
        """
        TempDict = makeValueChecks(kwargs, 'EXT')
        for key, value in TempDict.items():
            setattr(self.Ext, key, value)

    def addLoc(self,**kwargs):
        """
        This function enables to add a Loc Object with any attributes allocated related to Loc Object
        :param kwargs: any possible attribute of Loc Object
        :return: a now Loc Object, a message is raised if the Loc ID already exist, it wont be created
        """
        TempDict = makeValueChecks(kwargs,'LOC')
        a = Loc(**TempDict)
        if a.ID in self.Loc.keys():
            return print('[INFO] - It seems that this LOC ID already exists : '+a.ID)
        self.Loc[a.ID] = a
        self.ObjOrder = AppendObjOrder('LOC', a.ID, self.ObjOrder)

    def addBranch(self,**kwargs):
        """
        This function enables to add a Branch Object with any attributes allocated related to Branch Object
        :param kwargs: any possible attribute of Branch Object
        :return: a now Branch Object, a message is raised if the Branch ID already exist, it wont be created
        """
        TempDict = makeValueChecks(kwargs,'BRANCH')
        a = Branch(**TempDict)
        if a.ID in self.Branch.keys():
            return print('[INFO] - It seems that this BRANCH ID already exists : '+a.ID)
        self.Branch[a.ID] = a
        self.ObjOrder = AppendObjOrder('BRANCH', a.ID, self.ObjOrder)

    def addHSRC(self, **kwargs):
        """
        This function enables to add a HSRC Object with any attributes allocated related to HSRC Object
        :param kwargs: any possible attribute of HSRC Object
        :return: a now HSRC Object, a message is raised if the HSRC ID already exist, it wont be created
        """
        TempDict = makeValueChecks(kwargs,'HSRC')
        a = HSRC(**TempDict)
        if a.ID in self.HSRC.keys():
            return print('[INFO] - It seems that this HSRC ID already exists : '+a.ID)
        self.HSRC[a.ID] = a
        self.ObjOrder = AppendObjOrder('HSRC', a.ID, self.ObjOrder)

    def addPerson(self, **kwargs):
        """
        This function enables to add a Person Object with any attributes allocated related to Person Object
        :param kwargs: any possible attribute of Person Object
        :return: a now Person Object, a message is raised if the Person ID already exist, it wont be created
        """
        TempDict = makeValueChecks(kwargs,'PERSON')
        a = Person(**TempDict)
        if a.ID in self.Person.keys():
            return print('[INFO] - It seems that this PERSON ID already exists : '+a.ID)
        self.Person[a.ID] = a
        self.ObjOrder = AppendObjOrder('PERSON', a.ID, self.ObjOrder)

    def addSpecies(self, **kwargs):
        """
        This function enables to add a Species Object with any attributes allocated related to Species Object
        :param kwargs: any possible attribute of Species Object
        :return: a now Species Object, a message is raised if the Species ID already exist, it wont be created
        """
        TempDict = makeValueChecks(kwargs,'SPEC')
        a = Species(**TempDict)
        if a.ID in self.Species.keys():
            return print('[INFO] - It seems that this SPECIES ID already exists : '+a.ID)
        self.Species[a.ID] = a
        self.ObjOrder = AppendObjOrder('SPEC', a.ID, self.ObjOrder)

    def addMaterial(self, **kwargs):
        TempDict = makeValueChecks(kwargs,'MAT')
        a = Material(**TempDict)
        if a.ID in self.Material.keys():
            return print('[INFO] - It seems that this MATERIAL ID already exists : '+a.ID)
        self.Material[a.ID] = a
        self.ObjOrder = AppendObjOrder('MAT', a.ID, self.ObjOrder)

    def addSurf(self, **kwargs):
        TempDict = makeValueChecks(kwargs,'SURF')
        a = Surf(**TempDict)
        if a.ID in self.Surf.keys():
            return print('[INFO] - It seems that this SURF ID already exists : '+a.ID)
        self.Surf[a.ID] = a
        self.ObjOrder = AppendObjOrder('SURF', a.ID, self.ObjOrder)

    def addWall(self, **kwargs):
        TempDict = makeValueChecks(kwargs,'WALL')
        a = Wall(**TempDict)
        if a.ID in self.Wall.keys():
            return print('[INFO] - It seems that this WALL ID already exists : '+a.ID)
        self.Wall[a.ID] = a
        self.ObjOrder = AppendObjOrder('WALL', a.ID, self.ObjOrder)

    def addCtrl(self, **kwargs):
        TempDict = makeValueChecks(kwargs,'CTRL')
        a = Ctrl(**TempDict)
        if a.ID in self.Ctrl.keys():
            return print('[INFO] - It seems that this CTRL ID already exists : '+a.ID)
        self.Ctrl[a.ID] = a
        self.ObjOrder = AppendObjOrder('CTRL', a.ID, self.ObjOrder)
    def addBound(self, **kwargs):
        TempDict = makeValueChecks(kwargs,'BOUND')
        a = Bound(**TempDict)
        if a.ID in self.Bound.keys():
            return print('[INFO] - It seems that this BOUND ID already exists : '+a.ID)
        self.Bound[a.ID] = a
        self.ObjOrder = AppendObjOrder('BOUND', a.ID, self.ObjOrder)

    def addMod(self, **kwargs):
        TempDict = makeValueChecks(kwargs,'MOD')
        a = Mod(**TempDict)
        if a.ID in self.Mod.keys():
            return print('[INFO] - It seems that this MOD ID already exists : '+a.ID)
        self.Mod[a.ID] = a
        self.ObjOrder = AppendObjOrder('MOD', a.ID, self.ObjOrder)

    def MakeInputFile(self):
        """
        This function enables to build the .data file required to launch MATHIS either using the dll or using the standalone .exe application

        """
        if not self.Misc.JOBNAME.endswith('.data'): self.Misc.JOBNAME = self.Misc.JOBNAME+'.data'
        if self.Path2Case.endswith('.data'): self.Path2Case = self.Path2Case[:-5]
        file = CreateFile(self.Path2Case,self.Misc.JOBNAME)
        Dict4Export = {}
        # Write the MISC
        Misc = self.Misc.getModifiedValues()
        CreateObj(file, 'MISC', **Misc)
        Dict4Export['MISC'] = Misc
        # Write the EXT
        try:
            Ext = self.Ext.getModifiedValues()
            CreateObj(file,'EXT', **Ext)
            Dict4Export['EXT'] = Ext
        except:
            CreateObj(file,'EXT')
        # Write the LOC
        Dict4Export['LOC'] = WriteObject(file,'LOC', self.Loc, self.ObjOrder)
        # Write the Bound
        Dict4Export['BOUND'] = WriteObject(file, 'BOUND', self.Bound, self.ObjOrder)
        # Write the Branch
        Dict4Export['BRANCH'] = WriteObject(file,'BRANCH', self.Branch, self.ObjOrder)
        # Write the HSRC
        Dict4Export['HSRC'] = WriteObject(file,'HSRC', self.HSRC, self.ObjOrder)
        # Write the Person
        Dict4Export['PERSON'] = WriteObject(file,'PERSON', self.Person, self.ObjOrder)
        # Write the Species
        Dict4Export['SPEC'] = WriteObject(file,'SPEC', self.Species, self.ObjOrder)
        # Write the Materials
        Dict4Export['MAT'] = WriteObject(file,'MAT', self.Material, self.ObjOrder)
        # Write the Surfaces
        Dict4Export['SURF'] = WriteObject(file,'SURF', self.Surf, self.ObjOrder)
        # Write the Walls
        Dict4Export['WALL'] = WriteObject(file,'WALL', self.Wall, self.ObjOrder)
        # Write the Ctrl
        Dict4Export['CTRL'] = WriteObject(file,'CTRL', self.Ctrl, self.ObjOrder)
        # Write the Ctrl
        Dict4Export['MOD'] = WriteObject(file,'MOD', self.Mod, self.ObjOrder)
        #end of writing
        file.close()
        #writing other format files
        CleanedDict = {key : Dict4Export[key] for key in Dict4Export.keys() if Dict4Export[key]}
        WriteJsonFile(self.Path2Case, self.Misc.JOBNAME[:-5]+'.json', CleanedDict)

    def run(self, ExternalProcess = False, Verbose = True):
        """
        This function enables to run the mathis case either using the dll of in an external process the external
        process option is used mainly for parallell computing when laucnhing a bunch of case but it requires the path
        to mathis.exe
        :param ExternalProcess : bool to use a check call cmd instead of the dll
        :param Verbose : computation progression given in consol or not

        """
        if ExternalProcess:
            os.chdir(self.Path2Case)
            if Verbose: print('Starting Case : ' + self.Misc.JOBNAME)
            try:
                # if mathis path is given
                if platform.system() == "Windows":
                    if not self.Path2Mathis.endswith('.exe'): self.Path2Mathis += '/Mathis.exe'
                else:
                    if not self.Path2Mathis.endswith('athis'): self.Path2Mathis += '/mathis'
                cmd = [self.Path2Mathis, os.path.join(self.Path2Case, self.Misc.JOBNAME), '-l']
                if Verbose:
                    if os.path.isfile(self.Path2Mathis): print('Simulation is using : '+ self.Path2Mathis)
                    check_call(cmd[:-1])
                else:
                    check_call(cmd, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
                return 1
            except:
                try:
                    # if mathis is a global variable
                    cmd = ['mathis', os.path.join(self.Path2Case, self.Misc.JOBNAME), '-l']
                    if Verbose:
                        print('Simulation is using the executable set as global Variable')
                        check_call(cmd)
                    else:
                        check_call(cmd, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
                    return 1
                except:
                    print(
                        'Humm, seems there is an issue with this case : '+self.Misc.JOBNAME+'.\n'
                        'Please check that your Case.Path2Mathis is given or that mathis.exe (or mathis in linux) is set as a global/system variable in your system.\n'
                        'If the problem persists, it means the mathis case has itself a singular error (see case.out file). \n')
                    return 0
        else:
            C_FILE_Path = self.Path2Case
            C_FILE = self.Misc.JOBNAME
            cpt = '--------------------'
            cpt1 = '                    '
            if Verbose: print('\nData file launched : ' + C_FILE)
            time.sleep(0.01)
            # lets go in the right folder and initialise connection with MATHIS
            os.chdir(C_FILE_Path)
            SmartMathis = pm.LoadDll(pm.__file__, C_FILE)
            time.sleep(0.01)
            TimeunitConverter = {'S': 1, 'M': 60, 'H': 3600, 'J': 86400, 'D': 86400}
            TimeUnit = self.Misc.TIMEUNIT[0]
            t = self.Misc.TETA0*TimeunitConverter[TimeUnit]
            dt = round(self.Misc.DTETA*TimeunitConverter[TimeUnit],0)
            t_final = self.Misc.TETAEND*TimeunitConverter[TimeUnit]
            start = time.time()
            while t <= t_final:
                # Ask MATHIS to compute the current time step
                pm.solve_timestep(SmartMathis, t, dt)
                if Verbose:
                    done = t / t_final
                    print('\r', end='')
                    ptcplt = '.' if t % 2 else ' '
                    msg = cpt[:int(20 * done)] + ptcplt + cpt1[int(20 * done):] + str(round(100 * done, 1))
                    print('Computation completed by ' + msg + ' %', end='', flush=True)
                t = t + dt
            if Verbose:
                print('\n')
                print('CPUTime (sec) : '+str(round(time.time()-start,1)))
            pm.CloseDll(SmartMathis)
            time.sleep(0.01)

    def ReadResults(self, GiveDict = False, Vars = [], Steps = 1, StartTime = 0, Verbose = True):
        """
        Function that fetch the results from reading the *.res and *.head files
        :param GiveDict: bool = True, results will be given in a dictionary format, = False results will be given as object with all possible variable as attributes
        :param Vars: List of variable that would be read only
        :param Steps: index growth to fetch data (every Steps withtin the data .res files), useful to get hours values for smaller time step's simulation
        :param StartTime : Start Time at which the results are to be kept
        :return: Results object or dictionary format
        """
        #check if results are available
        if not os.path.isfile(os.path.join(self.Path2Case,self.Misc.JOBNAME)):
            return print('[ERROR] - Hmmm, it seems that there are no result files in the case path. Use the Case.run() function to launch your case')
        if Verbose: print('[INFO] Reading output files for Case '+self.Misc.JOBNAME+'...')
        FileList = os.listdir(self.Path2Case)
        Data = {}
        Headers = {}
        Version = []
        for file in FileList:
            try:
                if self.Misc.JOBNAME in file[:len(self.Misc.JOBNAME)]:
                    if '.out' in file:
                        Warnings, CPUTime, Version = readDotOutFile(self.Path2Case,file)
                        continue
                    if '.head' in file :
                        header = readDataFile(self.Path2Case,file,'headers')
                        if header: Headers[file[len(self.Misc.JOBNAME) + 1:-5]] = header
                        continue
                    if Vars:
                        if not [var for var in Vars if var in file]:
                            continue
                    if '.res' in file[-4:]:
                        if file.endswith('ATEC.res'):
                            Data['ATEC'] = readDataFile(self.Path2Case,file,'ATEC')
                            continue
                        if file.endswith('RMQAI.res'):
                            Data['RMQAI'] = readDataFile(self.Path2Case,file,'RMQAI')
                            continue
                        data,unit = readDataFile(self.Path2Case,file,'Data',IdxG = Steps, StartTime=StartTime)
                        Data[file[len(self.Misc.JOBNAME) + 1:-4]] = {'Data':data,'Unit':unit}
                    if '.mesh' in file[-5:]:
                        Headers[file[len(self.Misc.JOBNAME)+1:-5]+'Mesh'] = ['x (m)']
                        data,unit =  readDataFile(self.Path2Case, file, 'Data')
                        Data[file[len(self.Misc.JOBNAME) + 1:-5]+'Mesh'] = {'Data':data,'Unit':unit}
            except:
                print('Error when reading file : '+file)
        if not Version: Version = self.Version
        # Dict with all single variable as e key
        globalDict = {}
        for key in Data.keys():
            if 'Data' not in Data[key].keys(): continue
            if not Data[key]['Data'] : continue
            for subkey in Headers.keys():
                if subkey in key:
                    if len(key)>len(subkey):
                        if key[len(subkey)] == '_' :
                            for idx,name in enumerate(Headers[subkey]):
                                globalDict[key+'_'+name] = {'Data': Data[key]['Data'][idx+1], 'Time':Data[key]['Data'][0], 'Unit' : Data[key]['Unit']}
                    elif len(key) == len(subkey):
                        for idx, name in enumerate(Headers[subkey]):
                            if subkey=='ext':
                                unit = Data[key]['Unit'][:Data[key]['Unit'].find('value')] + name.replace('_',' ').replace('(','').replace(')','')
                                keyname = key + '_' + name.split('_')[0]
                            else:
                                unit = Data[key]['Unit']
                                keyname = key + '_' + name
                            try : globalDict[keyname] =  {'Data': Data[key]['Data'][idx+1], 'Time':Data[key]['Data'][0], 'Unit' : unit}
                            except : globalDict[keyname] = {'Data': Data[key]['Data'][idx], 'Unit' : unit} # for the mesh file, there is no time column
        try :
            globalDict['Warnings'] = Warnings
            globalDict['CPUTime'] = CPUTime
            globalDict['Version'] = Version
        except: pass
        try : globalDict['ATEC'] = Data['ATEC']
        except: pass
        try : globalDict['RMQAI'] = Data['RMQAI']
        except: pass

        # Dict with variable type dict with keys of variable
        globDict = {}
        for key in Data.keys():
            if 'Data' not in Data[key].keys(): continue
            if not Data[key]['Data']: continue
            header_key = []
            for head in Headers.keys():
                if head in key and len(Headers[head])>0:
                    if len(key)>len(head):
                        if key[len(head)] == '_':
                            header_key = head
                    elif len(key)==len(head): header_key = head
            if not header_key : continue
            globDict[key] = {}
            if len(Data[key]) <= 1:
                globDict[key] = Data[key]['Data'][0]
                continue
            if 'Mesh' in key: globDict[key]['Data'] = Data[key]['Data'][0]
            else: globDict[key]['Time'] = Data[key]['Data'][0]
            globDict[key]['Unit'] = Data[key]['Unit']
            for idx,var in enumerate(Data[key]['Data'][1:]):
                globDict[key][Headers[header_key][idx]]=var
        try:
            globDict['Warnings'] = Warnings
            globDict['CPUTime'] = CPUTime
            globDict['Version'] = Version

        except: pass
        try: globDict['ATEC'] = globalDict['ATEC'] = Data['ATEC']
        except: pass
        try: globDict['RMQAI'] = globalDict['RMQAI'] = Data['RMQAI']
        except: pass
        if GiveDict:
            return globDict
        else:
            return Results(**globalDict)


class Results():
    """
    Class object to store de results and make them easy to plot
    """

    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

#----------------------------------------------------------
## External functions to handle the building object methods
#----------------------------------------------------------

def AppendObjOrder(type, ID, ObjOrder):
    if type in ObjOrder.keys():
        if ID not in ObjOrder[type]:
            ObjOrder[type].append(ID)
    else:
        ObjOrder[type] = [ID]
    return  ObjOrder

def makeValueChecks(kwargs, ObjType):
    TempDict = copy.deepcopy(DefaultMathisInputDict[ObjType])
    for key, value in kwargs.items():
        if key not in TempDict.keys() and ObjType != 'MOD':
            print("[WARNING] - the key '"+key+"' does not exist for "+ObjType+" Object type. It will be ignored. "+DefaultMathisInputDict['Version'])
        else: TempDict[key] = value
    return TempDict

def convert_to_tuple(obj):
    """Function used to convert all matrix contained in a json file in tuples for json.load"""
    if isinstance(obj, list):
        if all(isinstance(i, list) for i in obj):
            return [tuple(item) for item in obj]
        else:
            return [convert_to_tuple(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_tuple(value) for key, value in obj.items()}
    else:
        return obj
def loadFromJson(filename):
    """
    Function that create a Building object from a JSON file
    :param Path: path to results folder
    :param file: file name
    """
    # Load the dictionary from the JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f,object_hook=convert_to_tuple)
    return data
def WriteJsonFile(path, filename, Dict):
    """Function that saves the Building object in a JSON file"""
    filename = os.path.join(path, filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(Dict, f, ensure_ascii=False, indent=4)

def readDotOutFile(Path,file):
    """
    Function that fecth the warning messages in the .out file
    :param Path: path to results folder
    :param file: file name
    :return: dictionary of warnings messages
    """
    Warnings = {'Time':[],'ITER':[], 'MAXLOC':[], 'MAXRES':[], 'Msg':[]}
    CPUTime = 0
    with open(os.path.join(Path, file), 'r',encoding='utf-8-sig') as f:
        lines = f.read()
    Version = lines[2].replace('\n', ' -- ') + lines[3].replace('\n', '')
    NBWarn = lines.split('WARNING')
    if len(NBWarn)>1: Warnings = fetchInfos(NBWarn, Warnings)
    NBWarn = lines.split('Flow Solver')
    if len(NBWarn)>1: Warnings = fetchInfos(NBWarn, Warnings, FlowCase=1)
    # lets fetch the total computation time
    for line in reversed(lines.split('\n')):
        if line.startswith('Calculation end'):
            try: CPUTime = float(line.split()[-2])
            except: CPUTime = -999
            break
        if line.startswith('Convergence problem'):
            CPUTime = -999
            break
    return Warnings, CPUTime, Version

def fetchInfos(NbWarn,Warnings, FlowCase = 0):
    for idx,warn in enumerate(NbWarn[1:]):
        warnlines = warn.split('\n')
        if FlowCase:
            Warnings['Msg'].append('Flow Solver Issue')
            startingIndex = 0
        else:
            Warnings['Msg'].append(warnlines[0][2:])
            startingIndex = 1
        for warnline in warnlines[startingIndex:]:
            if len(warnline)==0:continue
            if warnline.startswith('Convergence problem'): break
            if warnline.startswith('t='):
                Warnings['Time'].append(warnline)
                break
            else:
                pattern = r'([^=]+)\s*=\s*([^\s]+)'
                matches = re.findall(pattern, warnline)
                matches = [(key.strip(), value) for key, value in matches]
                for ele in matches:
                    #ets remove the substring in bracket if present
                    try : SubKey = ele[0][:ele[0].index('(')]
                    except : SubKey = ele[0]
                    if SubKey in Warnings.keys():
                        Warnings[SubKey].append(ele[1])
                    else:
                        Warnings[SubKey] = [ele[1]]
    return Warnings

def read_namelist(file_path,default = False):
    temp_file = file_path
    if not default:
        temp_file = os.path.join(os.path.dirname(file_path),'temp_file_path.data')
        with open(file_path, 'r',encoding='utf-8') as f:
            lines = f.readlines()
        with open(temp_file, 'w',encoding='utf-8') as f:
            for line in lines:
                if not line.startswith('*'):
                    #line = line.replace('à', 'a')
                    f.write(line)

    namelists = f90nml.read(temp_file)
    if not default: os.remove(temp_file)

    # Dictionnaire pour stocker les namelists en majuscules
    namelists_dict = {}
    ObjOrderLists = {}
    if default:
        with open(temp_file, 'r',encoding='utf-8') as f:
            lines = f.readlines()
        namelists_dict['Version'] = lines[2].replace('\n',' -- ')+lines[3].replace('\n','')

    for name, content in namelists.items():
        name_upper = name.upper()
        content_upper = {k.upper(): convert_matrix_to_tuples(v) for k, v in content.items()}

        if name_upper not in namelists_dict:
            namelists_dict[name_upper] = content_upper
            try: ObjOrderLists[name_upper] = [content_upper['ID']]
            except: pass
        else:
            if isinstance(namelists_dict[name_upper], dict):
                namelists_dict[name_upper] = [namelists_dict[name_upper]]
            namelists_dict[name_upper].append(content_upper)
            ObjOrderLists[name_upper].append(content_upper['ID'])

    if default: return namelists_dict
    else: return namelists_dict,ObjOrderLists

def convert_matrix_to_tuples(value):
    if isinstance(value, list) and all(isinstance(row, list) for row in value):
        # Transposer la matrice
        transposed_matrix = list(zip(*value))
        return [tuple(row) for row in transposed_matrix]
    if isinstance(value,str):
        value = value.replace(' ','')
    return value

def getDefaultMathisValues():
    """
        fetch the defaults variables and values of mathis
        :return: dictionary of defaults attributes and values
        """
    loadDefault = True
    DefaultFileDir = os.path.dirname(pm.__file__)
    DefaultFilePath = os.path.join(DefaultFileDir, 'default.out')
    if platform.system() == "Windows":
        smartmathisName = "smartmathis.dll"
    else:
        smartmathisName = "smartmathis.so"
    if os.path.isfile(DefaultFilePath):
        # if time.ctime(os.path.getmtime('default.out'), "%Y-%m-%d %H:%M:%S") < time.ctime(os.path.getmtime(os.path.join(os.path.dirname(pm.__file__),'smartmathis.dll'))):
        if os.path.getmtime(DefaultFilePath) > os.path.getmtime(os.path.join(DefaultFileDir, smartmathisName)):
            loadDefault = False
    if loadDefault:
        if platform.system() == "Windows":
            cmd = ['python.exe', os.path.join(DefaultFileDir, 'getDefaultMathisVal.py')]
        else:
            cmd = ['python', os.path.join(DefaultFileDir, 'getDefaultMathisVal.py')]
        check_call(cmd, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"), cwd=DefaultFileDir)
    outputDict = read_namelist(DefaultFilePath, default=True)
    return outputDict

def readDataFile(path,file,Datatype,IdxG = 1,StartTime = 0):
    """
    function the reads the .res and .head file in the result folder.
    used in ReadResults()
    :param path: path to the result folder
    :param file: file name
    :param Datatype: if it's a head format or a data format
    :param IdxG: index steps to fetch values
    :param StartTime : starting time at which the results are to be kept
    :return:
    """
    with open(os.path.join(path, file), 'r',encoding='utf-8') as f:
        lines = f.read()
    if 'headers' == Datatype:
        return [name for name in lines.split('\n') if name][1:]  # time is always in the first column
    elif 'Data' == Datatype:
        data = []
        Unit = ''
        for idx, line in enumerate(lines.split('\n')):
            if idx==0:
                if ' -- ' in line: line = line[:line.find(' -- ')]
                Unit = line
            if idx>0 and line:
                if (idx-1) % IdxG != 0: continue #because time 0 correspond to line 1 !
                # lets skip the first line
                try: values = [float(val) for val in line.split('  ') if val] # 2 spaces seems to be the separator
                except:
                    try: values = [float(val) for val in line.split(' ') if val] # 1 spaces seems to be the separator
                    except: values = [float(val) for val in line.split('\t') if val]
                if values[0]>=StartTime:
                    data.append(values)
        return [list(i) for i in zip(*data)], Unit
    else:
        lines = lines.split('\n')
        try: return oldATECWay(lines)
        except: return newATECWay(lines)

def newATECWay(lines):
    # with open(file, 'r', encoding='utf-8') as file:
    #     my_xml = file.read()
    # dict = xmltodict.parse(my_xml)
    OutPut = {}
    for idx, line in enumerate(lines):
        if idx>1 and len(line)>2:
            test = line.split(';')
            if len(test) == 1 and ' - ' in test[0]:
                #key = line.replace(' - ', '_')
                keys = line.split(' - ')
                OutPut[keys[0]] = {'Values': {}, 'Description': keys[1], 'Unit': keys[2]}
            else:
                if checkDataType(test[0]) == str:
                    subkeys = test
                    OutPut[keys[0]]['Values'] = {subkey: 0 for subkey in subkeys}
                else:
                    for ii, val in enumerate(test):
                        OutPut[keys[0]]['Values'][subkeys[ii]] = float(val)
    return OutPut
def oldATECWAY(lines):
    ATEC = {lines[0].replace(':','') : float(lines[1])}
    for idx, line in enumerate(lines):
        if idx>1 and len(line)>2:
            test = line.split('\t')
            if len(test)==1:
                key = line.replace(':','')
                ATEC[key] = {}
            else:
                if checkDataType(test[0])==str:
                    subkeys = test
                    ATEC[key] = {subkey:0 for subkey in subkeys}
                else:
                    for ii,val in enumerate(test):
                        ATEC[key][subkeys[ii]] = val
    return ATEC

def checkDataType(data):
    output = str
    try:
        val = float(data)
        output = float
    except: pass
    return output


def loadExistingFile(file):
    """
    function that enables to load a previous case, it can still present issues as all format of handwritten older datacase cannot be considered
    :param file : fail name to load
    :return : dictionary of all object found to further convert those in mathis objects
    """
    outputDict,ObjOrderLists = read_namelist(file)
    outputDict['ObjOrder'] = ObjOrderLists
    return outputDict

def WriteObject(file,type,OBJ,ObjOrder):
    """function linked to the MakeInputFile function"""
    output = []
    if type not in ObjOrder.keys(): return output
    for a in ObjOrder[type]:
        b = OBJ[a].getModifiedValues()
        CreateObj(file, type, **b)
        output.append(b)
    return output[0] if len(output)==1 else output

def write2file(file,header,kwargs):
    """
    This function is made to write the input data file needed for mathis. It's an internal function used in CreateObj()
    :param file: the opened object file
    :param header: the type of object concerned
    :param kwargs: list of attribute
    :return: none
    """
    line2write = '&'+header+' '
    for key, value in kwargs.items():
        if type(value) == str:
            line2write += " " + key + "='" + value +"'"
        elif type(value) == list:
            if type(value[0]) == str:
                line2write += " " + key + "='" + value[0] +"'"
                for val in value[1:]:
                    line2write += ",'"+val+"'"
            elif type(value[0]) == tuple:
                line2write = dealWithTuple(line2write,key,value)
            else:
                line2write += " " + key + "=" + str(value[0])
                for val in value[1:]:
                    line2write += ","+str(val)

        elif type(value) == tuple:
            line2write += " " + key + "=" + str(value[0]) + ',' + str(value[1])
        else:
            line2write += " " + key + "=" + str(value)
        line2write += ' \n'
    line2write += '  /\n'
    file.write(line2write)
    return file

def dealWithTuple(line2write, key, value):
    line2write += ' \n'
    for idx,cpl in enumerate(value):
        for idxy,val in enumerate(cpl):
            line2write += key +'('+str(idx+1)+','+str(idxy+1)+') = '+str(val)+'  '
        line2write += ' \n'
    return line2write

def CreateFile(Path2Case,filename):
    """
    This function create and open the file for the *.data
    :param filename: name of the *.data file
    :return: none
    """
    if not os.path.isdir(Path2Case):
        os.mkdir(Path2Case)
    else:
        for fname in os.listdir(Path2Case):
            if fname.startswith(filename):
                os.remove(os.path.join(Path2Case, fname))
    file = open(os.path.join(Path2Case,filename), 'w')
    return file

def CreateObj(file,Type,**kwargs):
    """
    This function is used to create the corresponding object in the *.data
    :param file: opened file
    :param Type: the type of object to create
    :param kwargs: list of attribute for the object to be created
    :return: the .*data file is appended by the created object with its attributes
    """
    file = write2file(file, Type, kwargs)
    return file


DefaultMathisInputDict = getDefaultMathisValues()

if __name__ == '__main__':
    '''This module creates object handled by mathis'''