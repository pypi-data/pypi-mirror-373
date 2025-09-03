# =============================================================================
# 1. Import classes and modules
# =============================================================================

# =============================================================================
# #If local installation of dopes instead of using PyPI (https://pypi.org/project/dopes/)
# import sys
# dopes_path = 'path/to/dopes'        
# if dopes_path not in sys.path:
#     sys.path.insert(0, dopes_path)
# =============================================================================

import dopes.equipment_control.equipment as eq
import dopes.equipment_control.cm110 as cm110
import dopes.equipment_control.pm100d as pm100d

import numpy as np
import matplotlib.pyplot as plt
# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipments
# =============================================================================
mycm110=cm110.cm110('COM5') # serial link through port COM5
mypm100d=pm100d.pm100d('COM3') # serial link through port COM5

# =============================================================================
# 4. Measurement parameters
# =============================================================================
wavelength_list=np.linspace(700,1500,9)
grating=2 # Grating 1 : AG2400-00240-303 (2400 G/mm and 180 nm - 680 nm) and Grating 2 : AG1200-00750-303 (1200 G/mm and 480 nm - 1500 nm)

file_path="monochromator_calibration.txt"
# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mycm110.initialize(grating_number=grating,waiting_time=30)
mypm100d.initialize()

# =============================================================================
# 6. Set wavelength
# =============================================================================
power=np.zeros(len(wavelength_list))
i=0
for wavelength in wavelength_list:
    mycm110.set_wavelength(wavelength,waiting_time=1)
    power[i]=mypm100d.read_data(wavelength,average_number=10)
    i+=1
# =============================================================================
# 7. Close connection
# =============================================================================
mycm110.close_connection()

# =============================================================================
# 8. Save data
# =============================================================================
data=np.transpose([wavelength_list, power])
header="Wavelength (nm), Power (W)\n"
eq.write_in_file(file_path,data,overwrite=True,header=header,comment="#")

# =============================================================================
# 9. Plot
# =============================================================================
fig,ax=plt.subplots()
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Power (W)")
ax.plot(wavelength_list, power,marker=".",markeredgecolor="k")

