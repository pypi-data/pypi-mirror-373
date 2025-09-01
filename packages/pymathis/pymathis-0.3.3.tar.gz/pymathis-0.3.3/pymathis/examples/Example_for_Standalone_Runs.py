from pymathis.Mathis_Objects import Building as MathisCase
import os
import matplotlib.pyplot as plt

"""Example of standalone case
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
"""

Name = 'StandaloneCase'
MyCase = MathisCase(Name)
#folder for running the simulation and fetch the results
MyCase.Path2Case = os.path.join(os.getcwd(), Name)
#MISC information
MyCase.setMisc(JOBNAME=Name, TETA0=0, DTETA=0.25, TETAEND= 240 ,TIMEUNIT='H', CONSTANT_SPECIFIC_HEAT=False)
#external conditions
MyCase.setExt(TEXT=10,YKS=0.000607, SPECIDS='CO2')

# Indoor spaces
MyCase.addLoc(ID='Room1', ALT= 0, AREA=30, HEIGHT=2.3, TINI=20)
MyCase.addLoc(ID='Room2', ALT=0, AREA=30, HEIGHT=2.3, TINI=20)

# Indoor spaces connections
MyCase.addBranch(ID='Internal_door',
                 BRANCHTYPE='OUVERTURE_VERTICALE',
                 LOCIDS=['Room1', 'Room2'],
                 Z1=0,
                 Z2=0,
                 SECTION=1.6,
                 HEIGHT=2,
                 COEF=0.7,
                 CTRLID='Door_control')
MyCase.addBranch(ID='door_leakage',
                 LOCIDS=['Room1', 'Room2'],
                 Z1=0,
                 Z2=0,
                 SECTION=0.006,
                 COEF = 0.7,
                 CTRLID='leakage_control')

MyCase.addBranch(ID='Vent_Inlet',
                 BRANCHTYPE='ENTREE_FIXE',
                 LOCIDS=['EXT', 'Room1'],
                 Z1=2, Z2=2,
                 QV0=45,
                 DPREF=20)
MyCase.addBranch(ID='Vent_Outlet',
                 BRANCHTYPE='DEBIT_CONSTANT',
                 LOCIDS=['Room2', 'EXT'],
                 Z1=2, Z2=2,
                 QV0=30)
MyCase.addBranch(ID='Room1_leakage',
                 BRANCHTYPE='PERMEABILITE',
                 LOCIDS=['Room1', 'EXT'],
                 Z1=2, Z2=2,
                 QV0=7,
                 DPREF=4,
                 EXPO=0.667)
MyCase.addBranch(ID='Room2_leakage',
                 BRANCHTYPE='PERMEABILITE',
                 LOCIDS=['Room2', 'EXT'],
                 Z1=2, Z2=2,
                 QV0=10,
                 DPREF=4,
                 EXPO=0.667)

MyCase.addSpecies(ID='CO2', YKREF=0.000607)
MyCase.addSpecies(ID='H2O')

MyCase.addHSRC(ID='HR_source',LOCID='Room1',MFLUX=0.0000153,YKS=1,SPECIDS='H2O',CTRLID='HR_source_control')
MyCase.addHSRC(ID='CO2_source',LOCID='Room1',MFLUX=0.0000081,YKS=1,SPECIDS='CO2',CTRLID='CO2_source_control')

# Controlers

HR_Profile = []
HRVal = 0
Door_Profile = []
DoorVal = 0
CO2_Profile = []
CO2Val = 0
val = 1
for time in range(240):
    if time%24==0:
        HR_Profile.append((time,HRVal))
        if HRVal == val: HRVal =0
        else: HRVal = val
        CO2_Profile.append((time, CO2Val))
        if CO2Val == val:
            CO2Val = 0
        else:
            CO2Val = val
    if time%12==0:
        Door_Profile.append((time,DoorVal))
        if DoorVal == val: DoorVal =0
        else: DoorVal = val



MyCase.addCtrl(ID='Door_control', CTRLTYPE='RAMP', FUNCTION='CRENEL', QUANTITY='TIME', RAMP=Door_Profile)
MyCase.addCtrl(ID='leakage_control', CTRLTYPE='LOGICAL_OPERATOR', FUNCTION='NOT', QUANTITIES='Door_control')
MyCase.addCtrl(ID='HR_source_control', CTRLTYPE='RAMP', FUNCTION='CRENEL', QUANTITY='TIME', RAMP=HR_Profile)
MyCase.addCtrl(ID='CO2_source_control', CTRLTYPE='RAMP', FUNCTION='CRENEL', QUANTITY='TIME', RAMP=CO2_Profile)


# make the input file
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
    ax.grid('on')

plt.show()

