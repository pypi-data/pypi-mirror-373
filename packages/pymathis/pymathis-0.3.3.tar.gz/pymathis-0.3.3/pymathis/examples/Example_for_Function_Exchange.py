from pymathis.Mathis_Objects import Building as MathisCase
import os
import pymathis.pymathis as pm
import matplotlib.pyplot as plt

"""
Example of function exchange cas between MAthis and python
The example is identical as the StandAloneCase
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

The Outlet will be controlled by the amount of CO2 level in Room1.
Above 900ppm and down to 600ppm, the airflow is fixed to 60m3/h and 10 otherwise

WARNING : It requires the Example_Fort_Standalone_Runs.py to be run in the first place
"""
def runFunctionExchange(MyCase):
    #lets go in the wright folder and initialize connection with MATHIS
    os.chdir(MyCase.Path2Case)
    SmartMathis =pm.LoadDll(pm.__file__,MyCase.Misc.JOBNAME)

    # Simulation parameters (start, end, time step) and time loop
    t = 0
    dt = MyCase.Misc.DTETA
    t_final = MyCase.Misc.TETAEND
    VentOn = 0
    ProbeCO2 = []
    #lets first fetch the index of the controler and probes, might be several, the index is initiate inside Mathis
    for ii in range(pm.get_passive_number(SmartMathis)):
        if pm.get_passive_ID(SmartMathis,ii) == 'Exhaust_flow_rate_ctrl':
            Exhaust_FlowRate_ctrl_Idx = ii
    for ii in range(pm.get_probe_number(SmartMathis)):
        if pm.get_probe_ID(SmartMathis,ii) == 'CO2_Probe':
            CO2_Probe_Idx = ii
    Vmax = 0
    pm.give_passive_ctrl(SmartMathis, 10, Exhaust_FlowRate_ctrl_Idx)
    #lets loop from starting to ending time
    while t < t_final:
        CO2_Probe = pm.get_probe_ctrl(SmartMathis, CO2_Probe_Idx)
        if CO2_Probe > 900 and Vmax==0:
            pm.give_passive_ctrl(SmartMathis, 60, Exhaust_FlowRate_ctrl_Idx)
            Vmax = 1
        elif CO2_Probe < 600:
            pm.give_passive_ctrl(SmartMathis, 10, Exhaust_FlowRate_ctrl_Idx)
            Vmax = 0
        # Ask MATHIS to compute the current time step
        pm.solve_timestep(SmartMathis, t*3600, dt*3600)
        ProbeCO2.append(CO2_Probe)
        # updating time iteration
        t = t + dt
        # prompt consol report
        if t%24==0: print('Time : ',t)
    #simulation is done, lets make a plot  of the control and probe
    pm.CloseDll(SmartMathis)
    MakeFinalPlot(MyCase,ProbeCO2)

def MakeFinalPlot(MyCase,ProbeCO2):
    Results = MyCase.ReadResults()
    fig, axs = plt.subplots(4, 1, figsize=(8, 6), sharex=True)
    axs[0].plot(Results.loc_YCO2_Room1['Time'], Results.loc_YCO2_Room1['Data'], label='loc_YCO2_Room1')
    axs[0].plot(Results.loc_YCO2_Room1['Time'], Results.loc_YCO2_Room2['Data'], label='loc_YCO2_Room2')
    axs[1].plot(Results.loc_YCO2_Room1['Time'], Results.loc_HR_Room1['Data'], label='loc_HR_Room1')
    axs[1].plot(Results.loc_YCO2_Room1['Time'], Results.loc_HR_Room2['Data'], label='loc_HR_Room2')
    axs[2].plot(Results.loc_YCO2_Room1['Time'], Results.loc_DP_Room1['Data'], label='loc_DP_Room1')
    axs[2].plot(Results.loc_YCO2_Room1['Time'], Results.loc_DP_Room2['Data'], label='loc_DP_Room2')
    axs[3].plot(Results.loc_YCO2_Room1['Time'], Results.branch_QV_Vent_Outlet['Data'], label='branch_QV_Vent_Outlet')
    for ax in axs:
        ax.legend()
        ax.grid()
    axs[-1].set_xlabel('Time in ' + MyCase.Misc.TIMEUNIT)
    plt.show()

def MakeCase(Name,Path2Case):
    MyCase.Path2Case = Path2Case
    MyCase.Misc.JOBNAME = Name
    #lets firt add a CO2 probe (in ppmv)
    MyCase.addCtrl(ID='CO2_Probe',CTRLTYPE='PROBE', FUNCTION='VALUE', QUANTITY='YK', SPECID='CO2', LOCID='Room1', CTRLID='ConvertCO2ppmv')
    MyCase.addCtrl(ID='ConvertCO2ppmv', CTRLTYPE='OPERATOR', FUNCTION='MAX', QUANTITIES='CONSTANT', CONSTANT=659090.91)
    #lets add an extra controler to further adapt the outlet volume flow rate
    MyCase.Branch['Vent_Outlet'].CTRLID = 'Exhaust_flow_rate_ctrl'
    MyCase.Branch['Vent_Outlet'].QV0 = 1 #this way the controler will directly be in m3/h
    MyCase.addCtrl(ID='Exhaust_flow_rate_ctrl', CTRLTYPE='PASSIVE')
    MyCase.MakeInputFile()
    return MyCase

if __name__ == '__main__':
    OldCaseName = 'StandaloneCase'
    Path2OldCase = os.path.join(os.getcwd(), 'StandaloneCase')
    if not os.path.isfile(os.path.join(Path2OldCase, OldCaseName+'.data')):
        print('WARNING : This example requires the Example_for_Standalone_Runs.py to be run in the first place')
    else:
        MyCase = MathisCase(os.path.join(Path2OldCase, OldCaseName))
        Name = 'FunctionExchange'
        Path2Case = os.path.join(os.getcwd(), Name)
        MyCase = MakeCase(Name,Path2Case)
        runFunctionExchange(MyCase)
        plt.show()