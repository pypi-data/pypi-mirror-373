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

import equipment_control.equipment as eq
import equipment_control.pm100d as pm100d

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipments
# =============================================================================
mypm100d=pm100d.pm100d('USB0::0x1313::0x8070::P0011704::INSTR') # serial link through port COM5

# =============================================================================
# 4. Measurement parameters
# =============================================================================
wavelength=800

file_path="monochromator_calibration.txt"
# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mypm100d.initialize()

# =============================================================================
# 6. Set wavelength
# =============================================================================
power=mypm100d.read_power(wavelength,average_number=10)
print("Power measured: %.3E W"%float(power))

# =============================================================================
# 7. Close connection
# =============================================================================
mypm100d.close_connection()


