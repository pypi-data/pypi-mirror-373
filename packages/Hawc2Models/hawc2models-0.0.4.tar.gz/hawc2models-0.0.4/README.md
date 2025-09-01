# HAWC2 Models

Collection of pip-installable hawc2 models.

## Installation

```
pip install hawc2models
```


# Example


```python
from hawc2models import IEA22MW, DTU10MW

# IEA 22MW Reference turbine
htc = IEA22MW(folder='IEA-22-280-RWT')

# specific version
htc = IEA22MW(folder='IEA-22-280-RWT_v1.0.1', version='refs/tags/v1.0.1')

# DTU10MW Reference wind turbine
htc = DTU10MW(folder='DTU10MW')

```





# Background
 
 
## Current status

We have reference models in different locations, e.g:
 
https://www.hawc2.dk/models
https://gitlab.windenergy.dtu.dk/rwts/dtu-10mw-rwt (frza’s model source)
https://gitlab.windenergy.dtu.dk/hawc-reference-models (rink’s group with models (e.g. a copy of dtu10mw) and utils)
https://github.com/IEAWindSystems (IEA3.4, 10, 15, 22)
 
Moreover, we have copies of the dtu10mw in the test_files folder of wetb, pytest_hawc2, hawc2lib, etc.
 
The models have very different sets of sensors. IEA22MW, for instance, has ~2000 aerodynamic sensors, which is just slowing down simulations for most users.
 
dtu10mw.py (https://gitlab.windenergy.dtu.dk/HAWC2/pytest_hawc2/-/blob/master/test_files/DTU10MW/dtu10mw.py?ref_type=heads) contains functionality to 
- Set tilt, cone, yaw
- Set fixed pitch and rotor speed
- Make blades stiff
- Make blades straight
- Set aero methods: aero_calc, induction, tiploss, dynstall
- Set wind: wsp, tint, turb_format, shear
- Set gravity
 
https://gitlab.windenergy.dtu.dk/hawc-reference-models has functionality to:
- Clone hawc2binary
- Clone/download dlls
  - https://gitlab.windenergy.dtu.dk/OpenLAC/control-binary/control-win32.git
  -	towerclearance_mblade.dll from artifact
  -	nrel-5mw-discon from artifact
- base_to_hs2
- base_to_step
- base_to_turb
- base_to_test
 
## Vision
- From roadmap
  - Reference model with full IEC 61400 DLB data set + post-processing
  - Example-model-library (exercises/walk-throughs)
  - Comparisons with measurements
- From users’ perspective:
  - One place to find all (up-to-date) HAWC2 reference models or links to source repositories?
  - Model similarity? (same kind of output, wind, aerodynamic, tiploss, tower shadow, turbulence, controllers?)
  - Newest controllers?
  - Including hs2 section
  - Step and turb?
  - Picture of model
  - DLB Reference loads?
  - Our and/or users comments/issues regarding the models? e.g.
	DTU10MW has aerodynamic discontinuties along blade due to change of profiles
	IEA22MW uses 100 aerodynamic calculation points because…”
- From test framework perspective
  - Pip installable
  - Download models from source repositories. Consistent or newest version?
  - Update dll’s?
  - Features as in dtu10mw.py. For all or just a subset?
- Other considerations
  - Should we try to change/fix the source repositories (e.g. reduce the number of sensors of the IEA22MW) or just provide a website with “our” versions?

## Open questions

- Where should model source files be stored
- How to obtain/download control dlls
- How to handle updates of control dlls and models
- What is a standard model (wsp, turbulence, controller/fixed)
- Which standard sensors should exist

