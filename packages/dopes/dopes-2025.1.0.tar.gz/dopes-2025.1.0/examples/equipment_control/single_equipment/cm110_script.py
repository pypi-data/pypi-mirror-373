 =============================================================================
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

# =============================================================================
# 4. Measurement parameters
# =============================================================================
wavelength=600
grating=1 # Grating 1 : AG2400-00240-303 (2400 G/mm and 180 nm - 680 nm) and Grating 2 : AG1200-00750-303 (1200 G/mm and 480 nm - 1500 nm)

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mycm110.initialize(grating_number=grating,waiting_time=30)

# =============================================================================
# 6. Set wavelength
# =============================================================================
mycm110.set_wavelength(wavelength,waiting_time=1)

# =============================================================================
# 7. Close connection
# =============================================================================
mycm110.close_connection()