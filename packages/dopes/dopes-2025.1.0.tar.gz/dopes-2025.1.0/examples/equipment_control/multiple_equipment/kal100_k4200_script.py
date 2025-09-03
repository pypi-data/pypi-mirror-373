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
import dopes.equipment_control.k4200 as k4200 
import dopes.equipment_control.kal100 as kal100

import numpy as np
import traceback # to write error message in try/except command
import datetime

# =============================================================================
# 2. List  available connections
# =============================================================================
rm=eq.resource_manager() # you can use the function from equipment class or directly the pyvisa command rm = pyvisa.ResourceManager()
list_connections= eq.available_connections(rm=rm) # you can use the function from equipment class or directly the pyvisa command rm.list_resources()
print("-------------------------------------------------\n Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipment
# =============================================================================
myK4200=k4200.k4200("GPIB0::17::INSTR",timeout=10e3)
mykal100=kal100.kal100('COM7') # serial link through port COM7

# =============================================================================
# 4. Measurement parameters
# =============================================================================

smu_type={"SMU1":"voltage","SMU2":"voltage","SMU3":"voltage","SMU4":"voltage"}
smu_used={"SMU1":"on","SMU2":"on","SMU3":"on","SMU4":"on"}
smu_master=1
smu_bias={"SMU1":10,"SMU2":0,"SMU3":0,"SMU4":0}
smu_compliance={"SMU1":1e-6,"SMU2":1e-6,"SMU3":1e-6,"SMU4":1e-6}
sweep_param={"start":0,"stop":1,"step":0.05}
sweep_type="linear"
integration_mode="S"
delay_time=0
hold_time=0

pressure_list=np.arange(0,11,1) # in kPa

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================

print("-------------------------------------------------\n Starting initialisation ...", end='')

myK4200.initialize(smu_type=smu_type,smu_used=smu_used,smu_master=smu_master,smu_bias=smu_bias,
                    smu_compliance=smu_compliance,sweep_param=sweep_param,sweep_type=sweep_type,
                    integration_mode=integration_mode,delay_time=delay_time,hold_time=hold_time)
mykal100.initialize(units="kPa")

print("  Done!")
# =============================================================================
# 6. Measurement script
# =============================================================================

for pressure in pressure_list:
    mykal100.set_pressure(pressure)

    print("-------------------------------------------------\n Starting measurement ...", end='')
    try:
        data,data_header=myK4200.launch_measurements()
    except Exception:
        traceback.print_exc()
        myK4200.close_connection()
    print("  Done!")

    # =============================================================================
    # 7. Save data
    # =============================================================================
    file_path='data/iv_%dkPa.txt'%pressure

    
    custom_header="IV results with K4200 at %d kPa\n"%pressure
    comment_delimiter="#"
    print("-------------------------------------------------\n Print in file %s"%file_path)
    print(" - Header:")
    print("   # %s"%(datetime.datetime.now().strftime("%c")))
    for line in (custom_header+data_header).split('\n'):
        print("   # "+line)
    eq.write_in_file(file_path,data,overwrite=True,header=custom_header+data_header,comment=comment_delimiter)

# =============================================================================
# 8. Close connection
# =============================================================================
myK4200.close_connection()
mykal100.close_connection()

