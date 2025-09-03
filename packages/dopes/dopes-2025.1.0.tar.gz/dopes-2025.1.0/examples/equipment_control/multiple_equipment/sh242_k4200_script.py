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
import dopes.equipment_control.k4200 as k4200 
import dopes.equipment_control.sh242 as sh242

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
mysh242=sh242.sh242('TCPIP0::192.168.100.11::57732::SOCKET',timeout=30e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================

smu_type={"SMU1":"voltage","SMU2":"voltage"}
smu_used={"SMU1":"on","SMU2":"on"}
smu_master=1
smu_bias={"SMU1":0,"SMU2":0}
smu_compliance={"SMU1":1e-6,"SMU2":1e-6}
sweep_param={"start":0,"stop":1,"step":0.05}
sweep_type="linear"
integration_mode="S"
delay_time=0
hold_time=0

temperature_list=np.arange(0,81,20)
wait_for_stabilization=False # if True, wait for the temperature and humidity to be stabilized to continue the script


# =============================================================================
# 5. Initialization of the equipment
# =============================================================================

print("-------------------------------------------------\n Starting initialisation ...", end='')

myK4200.initialize(smu_type=smu_type,smu_used=smu_used,smu_master=smu_master,smu_bias=smu_bias,
                    smu_compliance=smu_compliance,sweep_param=sweep_param,sweep_type=sweep_type,
                    integration_mode=integration_mode,delay_time=delay_time,hold_time=hold_time)
mysh242.initialize(temperature=True, humidity=False,temperature_dic={"upper":125,"lower":-45,"set":20})

print("  Done!")
# =============================================================================
# 6. Measurement script
# =============================================================================

for temperature in temperature_list:
    mysh242.set_temperature(temperature,wait_for_stabilization=wait_for_stabilization)

    print("-------------------------------------------------\n Starting measurement at %d (°C) ..."%temperature, end='')
    try:
        data,data_header=myK4200.launch_measurements()
    except Exception:
        traceback.print_exc()
        myK4200.close_connection()
    print("  Done!")

    # =============================================================================
    # 7. Save data
    # =============================================================================
    file_path="data/iv_%dC.txt"%temperature

    custom_header="IV results with K4200 at %d °C\n"%temperature
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
mysh242.close_connection()
