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
import dopes.equipment_control.dmm as dmm
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
mydmm=dmm.dmm('USB0::0x05E6::0x6500::04529651::INSTR',timeout=1e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
units={"voltage":"V", "current":"A", "resistance":"Ohms", "4wires":"Ohms"}        

mode="current"
autozero=True
nplc=1
digits=4
continuous_trigger = False
disp_enable=True
k2000=False
file_path='temp.txt'
t_init=time.time()

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
mydmm.initialize( mode=mode, autozero=autozero, continuous_trigger=continuous_trigger, 
                 digits=digits,nplc=nplc,disp_enable=disp_enable,k2000=k2000)

# =============================================================================
# 6. Measurement script
# =============================================================================
data=mydmm.read_single()
t_data=time.time()-t_init
print("%s measured: %E %s"%(mode,data,units[mode]))
# =============================================================================
# 7. Close connection
# =============================================================================
mydmm.close_connection()


# =============================================================================
# 8. Save data
# =============================================================================
data_to_write=[t_data,data]
header="Time (s), %s (%s)"%(mode,units[mode])
eq.write_in_file(file_path,data_to_write,header=header,date=True,overwrite=False)
