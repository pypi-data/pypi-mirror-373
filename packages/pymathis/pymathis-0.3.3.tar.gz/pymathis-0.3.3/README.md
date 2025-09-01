# PyMATHIS


![pymathis](pymathis.jpg)

PyMathis is a package that enables to build and launch MATHIS cases in the python environment.

MATHIS is a thermo-hygro-aeraulic nodal solver developed at CSTB, France,
for Buildings HVAC Design, Indoor Climate and Air Quality Assessment.  
For further detail on MATHIS software please refer to :
https://gitlab.com/CSTB/mathis/-/tree/master

PyMathis has been developped in python3 and embed MATHIS. It is compatible with windows and linux.  
PyMathis homepage : https://gitlab.com/CSTB/pymathis  

## Installation of PyMathis  
`pip install pymathis`  

## Requirements   
PyMathis uses matplotlib package only in its examples provided in the **examples** folder.  

## How to use PyMathis  

`from pymathis.Mathis_Objects import Building as MathisCase`  
`MyCase = MathisCase(CaseName)`  
`MyCase.Path2Case = your_path_to_results`  

**Note:** If 'CaseName' is an existing file (including full path), 'MathisCase()' will automatically load all parameters into 'MyCase' mathis object.  

a 'Misc' attribute and an 'Ext' attribute will automatically be given to 'MyCase' object with default values for each possible parameter.   

'Misc' corresponds to all simulation's parameters (timestep, starting and ending time, assumptions, convergence tolerances, ...).  
'Ext' corresponds to external ambiances.  
Modification can be made by :  
`MyCase.setMisc(parameter_to_change = value)`  
`MyCase.setExt(parameter_to_change = value)`  

Zones can be added by :  
`MyCase.addLoc(ID = zone1, **kwargs)`  
with 'kwargs' all possible parameters available for each zone in MathisCase.  

Branches can be added by :  
`MyCase.addBranch(ID = branch1, **kwargs)`  
with kwargs all possible parameters available for each Branch in MathisCase.  

The same paradigm goes for Occupants, Sources of pollutant / heat, Species, Materials, Walls, Surfaces, Bounds, Controlers and for external dll from users.  

Once the case is fully build, the input data file can be created, the simulation launched and the results fetched:  
`MyCase.MakeInputFile()`  
`MyCase.run()`  
`MyRes = MyCase.ReadResults()`  

MyRes will be a Mathis result Object type with all available variables defined as attributs.  

Three example are provided in the **examples** folder  
'Example_for_Standalone_Runs.py' shows how to build a case from scratch, launch the simulation and show some results.  
'Example_from_previous_Case.py' shows how to generate a pymathis case form an older input *.data file.  
'Example_for_Function_Exchange.py' shows how to exchange variable at each time step between Mathis and python.  

**Function Exchange Mode:**  
PyMathis enables to exchange variables at each time step. One can get computed variables or give values to controlers at each time step.  
It will require to load the Mathis, initiate the solver and to ask each time step to be solved (see 'Example_for_Function_Exchange.py' for the process).  
  
Here is some examples of other functions:  
`import pymathis.pymathis as pm`  
`dll=pm.LoadDll(pm.__file__,MyCase.Misc.JOBNAME)`  
`pm.give_weather(dll,arg)`  
with 'arg' being either : 'vmeteo', 'wdir', 'text', 'hr', 'sunrad', 'diffrad', 'tsky', 'tground', 'patm') for respectively Wind velocity (m/s), Wind direction (° north oriented), External temperature (°C), External relative humidity (%), Normal Direct solar irradiation (W/m²), horizontal Diffuse solar irradiation  (W/m²), Sky temperature (°C), ground temperature (°C) and atmospheric pressure (Pa).  
`get_obj_value(dll,objtype,objid,valuename,tag)`  
with 'objtype' being the object type ('LOC', 'BRANCH', 'WALL'), 'objid' being it's ID, 'valuename' being the wanted variable ('DP', 'T', ... for 'LOC' or 'DPFLOW', 'QV', ... for 'BRANCHE').  
The ID can be automatically fetch using :  
`get_obj_ID(dll,objtype, tag)`  
with 'tag' the position in the MATHIS list of this object type. If 'tag' is above the amount of objtec type, the error message will be the total number of object type.   
  
  
**Note:**  
`MyCase.run(ExternalProcess = True)` will run Mathis in an external process using check_call command. This option launches 'mathis.exe' (it requires mathis.exe to be located in Path2mathis or to be set as a global system variable).  
`MyRes = MyCase.ReadResults(GiveDict = True)` will associate to MyRes a dictionnary type with mathis sub-objects as keys. 

## **RECALL FROM MATHIS**

MATHIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.