# =============================================================================
# 1. Import classes and modules
# =============================================================================

#If local installation of dopes instead of using PyPI (https://pypi.org/project/dopes/)
import sys
dopes_path = 'D:/Roisin/Documents/dopes'        
if dopes_path not in sys.path:
    sys.path.insert(0, dopes_path)

import dopes.equipment_control.equipment as eq
import dopes.equipment_control.k2450 as k2450
import numpy as np
import matplotlib.pyplot as plt
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
myk2450=k2450.k2450("GPIB0::24::INSTR",timeout=60e3)

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
continuous_trigger = False
disp_enable = True
file_path = 'temp.txt'

vmin=0
vmax=4
n_sample=10*2+1 # max 2500 point in the buffer so n_sample<1250 if double==True
double=False # True for back and forth measurements
bias_list=np.linspace(vmin,vmax,n_sample)
if double:
    bias_list=np.append(bias_list,bias_list[-2::-1])

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
myk2450.initialize(source_mode=source_mode, measurement_mode=measurement_mode,
                   compliance=compliance, autozero=autozero, digits=digits,
                   continuous_trigger=continuous_trigger,disp_enable=disp_enable, nplc=nplc)
myk2450.set_source(vmin)
myk2450.set_output("ON")
time.sleep(1)


# =============================================================================
# 6. Measurement script
# =============================================================================

t_init=time.time()

myk2450.set_buffer_list(bias_list)
myk2450.start_buffer(wait=1)

data_dic=myk2450.read_buffer(elements=["READ","RELATIVE","SOURCE"]) 

print("Measurement done in %d s"%(time.time()-t_init))


# =============================================================================
# 7. Close connection
# =============================================================================
myk2450.close_connection()


# =============================================================================
# 8. Save data
# =============================================================================
data_to_write=np.transpose([data_dic["RELATIVE"],data_dic["SOURCE"],data_dic["READ"]])
header="Time (s), %s (%s)"%(measurement_mode,units[measurement_mode])
eq.write_in_file(file_path,data_to_write,header=header,date=True,overwrite=False)

# =============================================================================
# 9. Plot Data
# =============================================================================

fig,ax=plt.subplots()
ax.set_xlabel("Voltage (V)")
ax.set_ylabel("Current (A)")
ax.plot(data_dic["SOURCE"],data_dic["READ"],marker=".",markeredgecolor="k")

fig,ax=plt.subplots()
ax.set_xlabel("Time (t)")
ax.set_ylabel("Voltage (V)")
ax.plot(data_dic["RELATIVE"],data_dic["SOURCE"],color="tab:blue",marker=".",markeredgecolor="k",label="source voltage")
secax=ax.twinx()
secax.plot(data_dic["RELATIVE"],data_dic["READ"],color="tab:red",marker=".",markeredgecolor="k",label="reading current")
secax.set_ylabel("Current (A)")
fig.legend()
