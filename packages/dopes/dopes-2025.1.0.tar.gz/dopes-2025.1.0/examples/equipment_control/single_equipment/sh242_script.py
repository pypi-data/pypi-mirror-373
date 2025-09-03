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
import dopes.equipment_control.sh242 as sh242

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipments
# =============================================================================
mysh242=sh242.sh242('TCPIP0::192.168.100.11::57732::SOCKET',timeout=30e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
temperature=25
humidity=70
wait_for_stabilization=False # if True, wait for the temperature and humidity to be stabilized to continue the script

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mysh242.initialize(temperature=True, humidity=True,temperature_dic={"upper":125,"lower":-45,"set":20},humidity_dic={"upper":100,"lower":0,"set":55})

# =============================================================================
# 6. Read temperature and humidity
# =============================================================================
data_temperature=mysh242.read_temperature().split(",")
data_humidity=mysh242.read_humidity().split(",")
print("\n- Temperature: %.2f °C\n- Humidity: %.2f %%"%(float(data_temperature[0]),float(data_humidity[0])))

# =============================================================================
# 7. Set temperature and humidity
# =============================================================================
mysh242.set_temperature(temperature,wait_for_stabilization=wait_for_stabilization)
mysh242.set_humidity(humidity,wait_for_stabilization=wait_for_stabilization)

# =============================================================================
# 8. Close connection
# =============================================================================
mysh242.close_connection()