import os
from pymathis.Mathis_Objects import Building as MathisCase
import matplotlib.pyplot as plt

"""
Example of using and already existing *.data file
the case is identical as the StandAlone example case
WARNING : It requires the Example_Fort_Standalone_Runs.py to be run in the first place
"""
def runCase(Path2OldCase,OldCaseName):
    MyCase = MathisCase(os.path.join(Path2OldCase, OldCaseName))
    MyCase.Path2Case = os.path.join(os.getcwd(), 'ExistingCase')
    MyCase.Misc.JOBNAME = 'ExistingCase'
    MyCase.MakeInputFile()
    MyCase.run()
    Results = MyCase.ReadResults()
    fig, axs = plt.subplots(4, 1, figsize=(8, 6),sharex = True)
    axs[0].plot(Results.loc_YCO2_Room1['Time'],Results.loc_YCO2_Room1['Data'], label='loc_YCO2_Room1')
    axs[0].plot(Results.loc_YCO2_Room1['Time'],Results.loc_YCO2_Room2['Data'], label='loc_YCO2_Room2')
    axs[1].plot(Results.loc_YCO2_Room1['Time'],Results.loc_HR_Room1['Data'], label='loc_HR_Room1')
    axs[1].plot(Results.loc_YCO2_Room1['Time'],Results.loc_HR_Room2['Data'], label='loc_HR_Room2')
    axs[2].plot(Results.loc_YCO2_Room1['Time'],Results.loc_DP_Room1['Data'], label='loc_DP_Room1')
    axs[2].plot(Results.loc_YCO2_Room1['Time'],Results.loc_DP_Room2['Data'], label='loc_DP_Room2')
    axs[3].plot(Results.loc_YCO2_Room1['Time'],Results.branch_QV_Vent_Outlet['Data'], label='branch_QV_Vent_Outlet')
    for ax in axs:
        ax.legend()
        ax.grid()
    axs[-1].set_xlabel('Time in '+MyCase.Misc.TIMEUNIT)
    plt.show()

if __name__ == '__main__':
    OldCaseName = 'StandaloneCase'
    Path2OldCase = os.path.join(os.getcwd(), OldCaseName)
    if not os.path.isfile(os.path.join(Path2OldCase, OldCaseName+'.data')):
        print('WARNING : This example requires the Example_for_Standalone_Runs.py to be run in the first place')
    else:
        runCase(Path2OldCase, OldCaseName)