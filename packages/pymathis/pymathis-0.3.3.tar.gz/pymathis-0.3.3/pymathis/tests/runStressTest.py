"""
Author : Xavier Faure
xavier.faure@cstb.fr
Date : 08/01/2025
"""

#prgm générique pour lancer et vérifier les stress test de mathis (sharepoint CMN)

import os,json,psutil,yaml,copy
import multiprocessing as mp
from pymathis.Mathis_Objects import Building as MathisCase


def makePathCor(OBJ,path):
    try: a = OBJ.__dict__.keys()
    except: return
    for ai in a:
        if ai.endswith('FILE'):
            value = getattr(OBJ, ai)
            if value=='null': continue
            setattr(OBJ, ai, os.path.join(path, value))
    #return OBJ

def LaunchTest(filename,LocalCaseName,MathisPath,ExternalProcess,Verbose = True):
    path = os.path.dirname(filename)
    MyCase = MathisCase(filename+'.data')
    MyCase.Path2Case = os.path.join(os.getcwd(),LocalCaseName)
    MyCase.Path2Mathis = MathisPath
    MyCase.Misc.JOBNAME = LocalCaseName
    #maj des adresses de fichier pour prendre les CL du dossier de reference
    keysLists = MyCase.__dict__.keys()
    for key in keysLists:
        if isinstance(getattr(MyCase, key),dict):
            obj = getattr(MyCase, key)
            for key in obj.keys():
                makePathCor(obj[key],path)
        elif isinstance(getattr(MyCase, key),str) : pass
        else:  makePathCor(getattr(MyCase, key),path)
    MyCase.MakeInputFile()
    MyCase.run(ExternalProcess = ExternalProcess,Verbose=Verbose)
    MyCase.Misc.JOBNAME = LocalCaseName+'.data'
    return MyCase.ReadResults()

def getRefCase(filename):
    RefCase = MathisCase(filename)
    return RefCase.ReadResults()

def MakeATECKindCheck(Obj,ObjRef,Name,DataFileName):
    OutPut = {}
    for key in Obj.keys():
        #if isinstance(Obj[key],dict):
            OutPut[key] = {'Description' : Obj[key]['Description'],'Unit' : Obj[key]['Unit'],'Error ABS':{},'Error REL':{}}
            for subkey in Obj[key]['Values'].keys():
                delta = float(Obj[key]['Values'][subkey])-float(ObjRef[key]['Values'][subkey])
                OutPut[key]['Error REL'][subkey] = (delta/float(ObjRef[key]['Values'][subkey])*100 if float(ObjRef[key]['Values'][subkey])>0 else 0)
                OutPut[key]['Error ABS'][subkey] = (delta)
        # else:
        #     delta = float(Obj[key]) - float(ObjRef[key])
        #     OutPut[key] = (delta/float(ObjRef[key])*100 if float(ObjRef[key])>0 else 0)
    with open(os.path.join(os.getcwd(),DataFileName+'_'+Name+'StressResults.json'), 'w', encoding='utf-8') as f:
        json.dump(OutPut, f, ensure_ascii=False, indent=4)

def MakeVarChecks(Obj,ObjRef,DataFileName,Verbose):
    keyList = Obj.__dict__.keys()
    output = {}
    for key in keyList:
        var = getattr(Obj, key)
        if isinstance(var, dict):
            try:
                varref = getattr(ObjRef, key)
                if 'Data' in var.keys():
                    err = [var['Data'][idx] - va for idx, va in enumerate(varref['Data'])]
                    errel = [round((var['Data'][idx] - va)/va*100,1) if abs(va)>0 else 0 for idx, va in enumerate(varref['Data']) ]
                    if sum([abs(e) for e in err]) > 0:
                        testunite = var['Unit'].split(' ')
                        output[key] = {
                            'Unit':testunite[-1], 'Er_Min': min(err), 'Er_Max':max(err), 'Er_Mean': sum(err)/len(err),
                            'ErRel_Min': min(errel), 'ErRel_Max':max(errel), 'ErRel_Mean': sum(errel)/len(errel)} #todo ajouter les erreurs moyennes horaires ?
                else:
                    MakeATECKindCheck(var,varref,key,DataFileName)
            except AttributeError:
                if Verbose: print("'" + key + "' is not an attribute of the Reference")
    with open(os.path.join(os.getcwd(),DataFileName + '-StressResults.csv'), 'w') as outfile:
        if not output:
            outfile.write('No Error found on any variable - Congrats :)')
        else:
            outfile.write('Variable;Unit;Error Min;Error Max;Error Mean;ErrorRel Min (%);ErrorRel Max (%);ErrorRel Mean (%)\n')
            for key in output.keys():
                outfile.write(str(key)+';'+output[key]['Unit']+';'+str(output[key]['Er_Min'])+';'+str(output[key]['Er_Max'])+\
                              ';'+str(output[key]['Er_Mean'])+';'+str(output[key]['ErRel_Min'])+';'+str(output[key]['ErRel_Max'])+\
                              ';'+str(output[key]['ErRel_Mean'])+'\n')

def setenv():
    with open('localPathFile.yml', "r") as f:
        config = yaml.safe_load(f)
    er = 0
    if not os.path.isdir(config['localPath']):
        print("[Error] - localPath doesn't exists")
        er = 1
    return config,er

def MakeOneCheck(Casefolder, Casename,config,Verbose):
    filename = os.path.join(config['localPath'],Casefolder,Casename)
    localSim = LaunchTest(filename, Casename, config['MathisPath'], ExternalProcess=config['ExternalProcess'], Verbose=Verbose)
    Reference = getRefCase(filename)
    MakeVarChecks(localSim, Reference, Casename,Verbose)
    print('[ENDED] - '+Casename+' is done. Take a look at the output files !')

if __name__ == '__main__':
    config,er = setenv()
    CaseFolderName = [file for file in os.listdir(config['localPath']) if os.path.isdir(os.path.join(config['localPath'],file)) and file.startswith('cas')]
    if 'All' not in config['CaseName']:
        CaseFolderName = [file for file in CaseFolderName if file.startswith(config['CaseName'])]
        CaseName = [config['CaseName']]
        Verbose = True
    else:
        CaseName = ['cas_'+case[4:][:case[4:].find('_')] for case in CaseFolderName]
        Verbose = False
    if not CaseFolderName:
        print("[Error] - CaseFolderName not found")
        er=1
    if not er:
        nbPhysicalCPUs = psutil.cpu_count(logical=False)-1
        pool = mp.Pool(processes=int(nbPhysicalCPUs))
        for idx, CaseFolder in enumerate(CaseFolderName):
            pool.apply_async(MakeOneCheck, args=(CaseFolder, CaseName[idx],config,Verbose))
        pool.close()
        pool.join()


