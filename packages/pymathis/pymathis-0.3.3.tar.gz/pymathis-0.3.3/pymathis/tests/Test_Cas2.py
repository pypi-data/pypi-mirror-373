"""
Author : Xavier Faure
xavier.faure@cstb.fr
Date : 08/01/2025
"""

#prgm de test du cas 1 dans le dossier stresstest de mathis (sharepoint CMN)

from pymathis.Mathis_Objects import Building as MathisCase
import os
import matplotlib.pyplot as plt

def makePathCor(OBJ):
    try: a = OBJ.__dict__.keys()
    except: return
    for ai in a:
        if ai.endswith('FILE'):
            value = getattr(OBJ, ai)
            if value=='null': continue
            setattr(OBJ, ai, os.path.join(path, value))
    #return OBJ

filename = "C:\\Users\\FAURE\\CSTBGroup\\C2A - projets\\MATHIS\\pymathis\\stressTest\\dataFile\\cas_2_hyg\\cas_2_hyg.data"
path = os.path.dirname(filename)
MyCase = MathisCase(filename)
MyCase.Path2Case = os.path.join(os.getcwd(),'cas_2_hyg')
MyCase.Misc.JOBNAME = 'cas_2_hyg.data'
#maj des adresses de fichier pour prendre les CL du dossier de reference
keysLists = MyCase.__dict__.keys()
for key in keysLists:
    if isinstance(getattr(MyCase, key),dict):
        obj = getattr(MyCase, key)
        for key in obj.keys():
            makePathCor(obj[key])
    elif isinstance(getattr(MyCase, key),str) : pass
    else:  makePathCor(getattr(MyCase, key))

MyCase.Mod['MoistLeak'].MODTYPE = 'C:/Users/FAURE/Documents/DevInfos/MATHIS_Projet/moisture_leak/moisture_leak/x64/Release/moisture_leak'
# MyCase.MakeInputFile()
# MyCase.run()
Res = MyCase.ReadResults()
RefCase = MathisCase(filename)
ResRef = RefCase.ReadResults()

keyList = Res.__dict__.keys()
for key in keyList:
    var = getattr(Res, key)
    if isinstance(var,dict):
        varref = getattr(ResRef, key)
        if 'Data' in var.keys():
            err= [var['Data'][idx]-va for idx,va in enumerate(varref['Data'])]
            if sum(err)>0: print(key+' a un erreur cumulé de '+str(round(sum(err),2)))


