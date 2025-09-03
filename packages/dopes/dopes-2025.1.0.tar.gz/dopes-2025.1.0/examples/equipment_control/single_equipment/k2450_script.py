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
import dopes.equipment_control.k2450 as k2450
import time

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipment
# =============================================================================
myk2450=k2450.k2450("GPIB0::29::INSTR",timeout=5e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
units={"voltage":"V", "current":"A", "resistance":"Ohms"}        

source_mode = "voltage"
measurement_mode = "current"
compliance = 1e-6
autozero = True
nplc = 1
digits = 6
continuous_trigger = True
disp_enable = True
bias_source = 1
file_path = 'temp.txt'
t_init=time.time()
# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
myk2450.initialize(source_mode=source_mode, measurement_mode=measurement_mode,
                   compliance=compliance, autozero=autozero, digits=digits,
                   continuous_trigger=continuous_trigger,disp_enable=disp_enable, nplc=nplc)

# =============================================================================
# 6. Measurement script
# =============================================================================
myk2450.set_source(bias_source)
myk2450.set_output("ON")
data=myk2450.read_single()
t_data=time.time()-t_init
print("%s measured: %E %s"%(measurement_mode,data,units[measurement_mode]))
# =============================================================================
# 7. Close connection
# =============================================================================
myk2450.close_connection()


# =============================================================================
# 8. Save data
# =============================================================================
data_to_write=[t_data,data]
header="Time (s), %s (%s)"%(measurement_mode,units[measurement_mode])
eq.write_in_file(file_path,data_to_write,header=header,date=True,overwrite=False)
