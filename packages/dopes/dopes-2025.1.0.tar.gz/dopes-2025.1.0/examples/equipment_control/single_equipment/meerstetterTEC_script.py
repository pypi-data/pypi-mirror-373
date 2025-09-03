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
import dopes.equipment_control.meerstetterTEC as TEC

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipment
# =============================================================================
myTEC=TEC.meerstetterTEC()
myTEC.initialize()
# =============================================================================
# 4. Measurement parameters
# =============================================================================
temperature=25.0

# =============================================================================
# 5. Set the temperature 
# =============================================================================
myTEC.set_temp(temperature,wait_for_stabilization=True)

# =============================================================================
# 6. Read the temperature 
# =============================================================================
TEC_data=myTEC.get_data()
object_temp=TEC_data["object temperature"]
print("Object temperature: %.3f %s"%(object_temp))

# =============================================================================
# 7. Close the connection 
# =============================================================================
myTEC.close_connection()