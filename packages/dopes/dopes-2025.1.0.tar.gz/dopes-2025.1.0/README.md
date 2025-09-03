  <img src="https://forge.uclouvain.be/welcome/dopes/-/raw/main/logo.png" width="350">

## Description
Data analysis and Operation Software (DOpeS) provides a set of tools for 
1. the analysis of data coming from lab equipment such as Raman spectrometer, white-light interferometer, semiconductor analyzer, ...
2. the control of lab equipment such as multimeter, source measurement units, pressure generator, climatic chamber, monochromator, ...

For more advanced software for equipment control, the user can refer to <a href=https://pymeasure.readthedocs.io/> **PyMeasure** </a> software.

## Structure
- **data_analysis** for the analysis of lab equipment:
    - Data processing function such as baseline removal, interpolation, filtering, ...
    - File handling to read data files and writting processed data in files
    - Specific functions to analyse measurements such as Raman specroscopy, white-light interferometer, semiconductor analyzer, ...
    - Modeling of electronic device and material such as diode and MOS transistor
- **equipment_control** for the control of various lab equipment:
    - Digital multimeter (DMM) *DMM7510*, *DMM6500* and *K2000*
    - Source Measurement Unit (SMU) *K2400* and *K2450* 
    - Semiconductor analyser *HP4145* and *K4200*
    - Oscilloscope *MSO56*, *TBS2000* and *MSO2024*
    - Signal generator *Agilent 33120*, *Agilent 33250A* and *Tektronix AFG2021*
    - Monochromator *CM110*
    - Power meter controller *PM100D*
    - Pressure generator and monitor *KAL100* 
    - Climatic chamber *SH242*
    - Thermoelectric cooler (TEC) *SKT-1165*
    - ...

## Requirements
DOpeS is made from functions, classes and scripts based on Python programming lanquage. The following packages are required for the data analysis and the equipment control:
- <a href=https://pypi.org/project/numpy/> **Numpy** </a> for the data handling and processing
- <a href=https://pypi.org/project/scipy/> **SciPy** </a> for the data processing tools such as interpolation and filtering (only for *data_analysis* part)
- <a href=https://pypi.org/project/PyVISA/> **Pyvisa** </a> for the communication with equipment (only for *equipment_control* part)
- <a href=https://pypi.org/project/pyserial/> **Pyserial** </a> for the serial communication with equipment (only for *equipment_control* part)

On top of the Python requirements, do not forget to download the correct drivers if you use a <a href=https://www.ni.com/en/support/downloads/drivers/download.ni-488-2.html#305442> **GPIB-USB connector** </a> and the <a href=https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html#409839> **VISA** </a> I/O standard.

## Installation
DOpeS is easily installed through the Python Index Package (PyPI) available at <a href=https://pypi.org/project/dopes/> **dopes** </a>:
```
pip install dopes
```

If you want to keep track of the latest versions, you can download the gitlab repository and keep it synchronized with the gitlab project:
To download it, you just have to type the following command in a terminal:
```
git clone https://forge.uclouvain.be/welcome/dopes.git
```

To update it with the gitlab project, you can type:
```
cd path/to/dopes
git pull
```

## Usage
DOpeS is built as a set of python classes and functions.
To use it, you only have to create a python script in you favorite IDE and import the dopes package installed through the Python Index Package (PyPI).

A global import can be made to import all the functionnalities:
```
import dopes
```

The various tools can also bee specifically accessed as any python package:
```
import dopes.equipment_control.equipment as eq
import dopes.equipment_control.k2400 as k2400
import dopes.data_analysis.raman as ram
```

If the package has been locallly downloaded on your laptop with git command or not, the path to DOpeS folder has to be added at the beginning of the script:
```
import sys
dopes_path = 'path/to/dopes'        
if dopes_path not in sys.path:
    sys.path.insert(0, dopes_path)
```
The various tools can then be accessed as any python package and class:
```
import equipment_control.equipment as eq
import equipment_control.k2400 as k2400
import data_analysis.raman as ram
```

Lots of examples for the data analysis and equipment control can be found in the <a href=https://forge.uclouvain.be/welcome/dopes/-/tree/main/examples> **examples** </a>  folder ("examples/data_analysis/" and "/examplesequipment_control").
Furthermore, an markdown (.md) or html (.html) documentation can be found in the <a href=https://forge.uclouvain.be/welcome/dopes/-/tree/main/doc> **doc** </a>" folder with a description of all classes and functions present in the software.

## Private project
A private part of the **DOpeS** project exists to keep some codes private and preserve the intellectual property of UCLouvain.
Access to <a href=https://forge.uclouvain.be/welcome/dopes_private/> **DOpeS_private** </a> can be requested from technical staff of the <a href=https://app.uclouvain.be/PTech/Home/WELCOME> **WELCOME** platform </a>.
However, be careful to only request access for trusted partners of UCLouvain.


## Support and contributing
We welcome any feedback on issue, missing operation or equipment but also idea for further improvements.

For people who have been added as editor or contributor, you need to set a <a href=https://forge.uclouvain.be/help/user/ssh.md> **secure ssh connection** </a> between their computer and their forge account.
Then, git has to be installed on your <a href=https://git-scm.com/downloads/linux>Linux</a> or <a href=https://git-scm.com/downloads/win>Windows</a> computer.
Finally, you only have to use <a href=https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project> **git command** </a> to contribute to the project.

For windows user, a graphical user interface (GUI) such as  <a href=https://gitextensions.github.io/>Github Desktop</a> could be useful for users unfamiliar with terminal commands.

## Authors and acknowledgment
The initial idea of this project has been thought by **Loïc Lahaye** and **Nicolas Roisin**.

## License
 DOpeS © 2025 by Loïc Lahaye and Nicolas Roisin is licensed under <a href=https://creativecommons.org/licenses/by-nc-sa/4.0/> Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International </a> (<a href=https://creativecommons.org/licenses/by-nc-sa/4.0/> CC BY-NC-SA 4.0</a>) 
## Project status
Still alive