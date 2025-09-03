

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
import dopes.equipment_control.kal100 as kal100

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipments
# =============================================================================
mykal100=kal100.kal100('COM7') # serial link through port COM7

# =============================================================================
# 4. Measurement parameters
# =============================================================================
pressure=1 # in kPa

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mykal100.initialize(units="hPa")

# =============================================================================
# 6. Set wavelength
# =============================================================================
mykal100.set_pressure(pressure)

# =============================================================================
# 7. Close connection
# =============================================================================
mykal100.close_connection()

