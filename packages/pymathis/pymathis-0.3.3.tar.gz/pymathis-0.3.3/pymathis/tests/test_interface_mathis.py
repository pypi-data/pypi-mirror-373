import os
import pymathis.pymathis as pm
import pickle


def MakeTestRun():
    # Paths and case name
    C_FILE_Path = os.getcwd()
    C_FILE = 'ProbeAndCtrlTEST.data'

    #lets go in the right folder and initialise connection with MATHIS
    os.chdir(C_FILE_Path)
    SmartMathis =pm.LoadDll(pm.__file__,C_FILE)
    # Lets fetch the available actuators and their IDs, initialization value is set to 0
    n_passive = pm.get_passive_number(SmartMathis)
    PassiveCtrl_ID = {pm.get_passive_ID(SmartMathis, i):[0] for i in range(n_passive)}
    # lets fetch the probes and their IDs
    n_probe = pm.get_probe_number(SmartMathis)
    Probe_ID = {pm.get_probe_ID(SmartMathis, i):[] for i in range(n_probe)}
    # Simulation parameters (start, end, time step) and time loop
    t = 0
    dt = 1
    t_final = 3600*4
    VentOn = 0
    while t < t_final:
        # lets set each controller's position
        for i,key in enumerate(PassiveCtrl_ID):
            pm.give_passive_ctrl(SmartMathis,PassiveCtrl_ID[key][-1], i)
        # Ask MATHIS to compute the current time step
        pm.solve_timestep(SmartMathis, t, dt)

        # lets fetch the new probes' value
        for i,key in enumerate(Probe_ID):
            Probe_ID[key].append(pm.get_probe_ctrl(SmartMathis,i))

        # Lets give the new actuators set points considering the probes values :
        # here is a simple action in which every 1/2hours 10 people are moving either inside or outside
        for key in PassiveCtrl_ID.keys():
            if key == 'CtrlNBPersonne':
                if t%3600<1800: PassiveCtrl_ID[key].append(10)  # 10 people in
                else: PassiveCtrl_ID[key].append(0)             # 0 people in
        # if CO2 probe give values above 800ppm, extracted airlow is at full capacity (define in the cas.data file)
        # a nd below 600ppm, its stopped
        if Probe_ID['SondeCO2'][-1]>800 and not VentOn:
            PassiveCtrl_ID['CtrlDebit'][-1] = 1 #it's a multiplier of the airflow define in the *.data file
            VentOn = 1
        elif Probe_ID['SondeCO2'][-1]<600 and VentOn:
            PassiveCtrl_ID['CtrlDebit'][-1] = 0
            VentOn = 0

        # updating time iteration
        t = t + dt
        # prompt consol report
        if t%1800==0: print('Time : ',t)
    pm.CloseDll(SmartMathis)
    return Probe_ID,PassiveCtrl_ID

def ComputeDiff(Ref,var):
    check = []
    for ii,val in enumerate(var):
        if val!=0:
            check.append((val - Ref[ii])/val*100)
        elif Ref[ii]!=0:
            check.append((val - Ref[ii]) / Ref[ii] * 100)
        else:
            check.append(0)
    return check


def CheckRes(Probe_ID,PassiveCtrl_ID,epsilon=1e-3):
    with open('ProbeAndCtrlTEST.pickle', 'rb') as f:
        TesRes = pickle.load(f)
    for key in Probe_ID:
        check = ComputeDiff(TesRes['Probe'][key],Probe_ID[key])
        if max(check)>epsilon:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(TesRes['Probe'][key])
            plt.plot(Probe_ID[key])
            plt.show()
            return False
    for key in PassiveCtrl_ID:
        check =ComputeDiff(TesRes['PassiveCtrl'][key],PassiveCtrl_ID[key])
        if max(check)>epsilon:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(TesRes['Probe'][key],label = 'Previous Res')
            plt.plot(Probe_ID[key],label = 'Current Res')
            plt.legend()
            plt.show()
            return False
    return True

def CleanFolder():
    list = os.listdir(os.getcwd())
    for file in list:
        if 'ProbeAndCtrlTEST.data' in file and len(file)>len('ProbeAndCtrlTEST.data'):
            os.remove(file)

if __name__ == '__main__':
    Probe_ID,PassiveCtrl_ID = MakeTestRun()
    if CheckRes(Probe_ID, PassiveCtrl_ID,epsilon=1e-5):
        print('Check completed : OK :)')
    else:
        print('Check failed...sorry')
    CleanFolder()
