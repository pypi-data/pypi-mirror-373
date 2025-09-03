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

import dopes.equipment_control.equipment as eq # Parent class that handle the connections with the equipments
import dopes.equipment_control.hp4145 as hp4145 # Child class that inherits from equipment parent class
import traceback # to write error message in try/except command
import datetime

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager() # you can use the function from equipment class or directly the pyvisa command rm = pyvisa.ResourceManager()
list_connections= eq.available_connections(rm=rm) # you can use the function from equipment class or directly the pyvisa command rm.list_resources()
print("-------------------------------------------------\n Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipment
# =============================================================================
myHP4145=hp4145.hp4145("GPIB0::1::INSTR",timeout=10e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
file_path='temp.txt'

smu_type={"SMU1":"voltage","SMU2":"voltage","SMU3":"voltage","SMU4":"voltage"}
smu_used={"SMU1":"on","SMU2":"on","SMU3":"on","SMU4":"on"}
smu_master=1
smu_bias={"SMU1":10,"SMU2":0.1,"SMU3":0.1,"SMU4":0.1}
smu_compliance={"SMU1":1e-6,"SMU2":1e-6,"SMU3":1e-6,"SMU4":1e-6}
sweep_param={"start":0,"stop":1,"step":0.05}
sweep_type="linear"
integration_mode="S"
delay_time=0
hold_time=0


# =============================================================================
# 5. Initialization of the equipment
# =============================================================================

print("-------------------------------------------------\n Starting initialisation ...", end='')

myHP4145.initialize(smu_type=smu_type,smu_used=smu_used,smu_master=smu_master,smu_bias=smu_bias,
                    smu_compliance=smu_compliance,sweep_param=sweep_param,sweep_type=sweep_type,
                    integration_mode=integration_mode,delay_time=delay_time,hold_time=hold_time)
print("  Done!")
# =============================================================================
# 6. Measurement script
# =============================================================================
print("-------------------------------------------------\n Starting measurement ...", end='')
try:
    data,data_header=myHP4145.launch_measurements()
except Exception:
    traceback.print_exc()
    myHP4145.close_connection()
print("  Done!")

# =============================================================================
# 7. Close connection
# =============================================================================
myHP4145.close_connection()

# =============================================================================
# 8. Save data
# =============================================================================
custom_header="IV results with HP4145\n"

print("-------------------------------------------------\n Print in file %s"%file_path)
print(" - Header:")
print("   # %s"%(datetime.datetime.now().strftime("%c")))
for line in (custom_header+data_header).split('\n'):
    print("   # "+line)
eq.write_in_file(file_path,data,overwrite=False,header=custom_header+data_header)
