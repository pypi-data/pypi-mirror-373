from pymathis.Mathis_Objects import Building as MathisCase
import os
import multiprocessing as mp
import psutil, copy
import matplotlib.pyplot as plt


"""Example of parametric run on the previoulsy made standalone case
                     _______________________________
          Outlet <--|    Room2      |    Room1      |
                    |               |               |<--air inlet
envelope leakage -->|            internal           |<-- envelope leakage
                    |              door      source |
                    |_________________________\/____|

Simple example with three parameters being controlled by timetable on fixed period
sources of H2O and CO2 are released for 24h every 24h
internal door is opened for 12h each 12h
External conditions are constant
It is run 10 times using parallel computing with increasing fan extraction airflow rate
"""

def GetInitialCase():
    AlreadyMadeCaseName = 'StandaloneCase'
    Path2OldCase = os.path.join(os.getcwd(), 'StandaloneCase')
    if not os.path.isfile(os.path.join(Path2OldCase, AlreadyMadeCaseName+'.data')):
        print('WARNING : This example requires the Example_for_Standalone_Runs.py to be run in the first place')
        return exit()
    MyCase = MathisCase(os.path.join(Path2OldCase, AlreadyMadeCaseName))
    MyCase.Misc.JOBNAME = 'ParametricRun'
    MyCase.Path2Case = os.path.join(os.getcwd(), 'ParametricRuns')
    if not os.path.isdir(MyCase.Path2Case):
        os.mkdir( MyCase.Path2Case)
    return MyCase

def MaketheRun(Case,OutletFan,runNo):
    Case.Path2Case =os.path.join(Case.Path2Case,'run_'+str(runNo))
    Case.Misc.JOBNAME += '_'+str(runNo)
    Case.Branch['Internal_door'].SECTION = OutletFan
    Case.Branch['Vent_Outlet'].QV0=OutletFan
    Case.MakeInputFile()
    Case.run(Verbose = False)

def MakeGraph(path,CaseName,OutletFans):
    Liste = os.listdir(path)
    VarOfInterest={'CO2':{},'HR':{}}
    for name in Liste:
        if os.path.isdir(os.path.join(path,name)) and name.startswith('run'):
            runNo = name[name.find('_')+1:]
            Case = MathisCase(os.path.join(path,name,CaseName+'_'+runNo))
            Res = Case.ReadResults(GiveDict=True)
            VarOfInterest['CO2'][runNo] = Res['loc_YCO2']['Room2']
            VarOfInterest['HR'][runNo] = Res['loc_HR']['Room2']
    Time = Res['loc_YCO2']['Time']
    fig, axs = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    fig.suptitle('Variables in Room 2')
    for run in VarOfInterest['CO2'].keys():
        axs[0].plot(Time,VarOfInterest['CO2'][run],label = str(OutletFans[int(run)])+' (m3/h)')
        axs[1].plot(Time, VarOfInterest['HR'][run], label= str(OutletFans[int(run)])+' (m3/h)')
    axs[0].legend()
    axs[0].grid('on')
    axs[0].set_ylabel('CO2 (ppm)')
    axs[1].set_ylabel('HR (%)')
    axs[1].grid('on')
    plt.show()


if __name__ == '__main__':
    Case = GetInitialCase()
    OutletFans = [5,10,15,20,25,30,35,40]
    nbPhysicalCPUs = psutil.cpu_count(logical=False)
    pool = mp.Pool(processes=int(nbPhysicalCPUs))
    for idx,doorSection in enumerate(OutletFans):
        pool.apply_async(MaketheRun, args=(copy.deepcopy(Case),doorSection,idx))
    pool.close()
    pool.join()
    MakeGraph(Case.Path2Case,Case.Misc.JOBNAME,OutletFans)
