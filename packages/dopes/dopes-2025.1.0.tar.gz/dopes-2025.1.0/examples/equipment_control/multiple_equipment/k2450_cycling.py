

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


import numpy as np
import matplotlib.pyplot as plt
import dopes.equipment_control.equipment as eq
import dopes.equipment_control.k2450 as k2450
import dopes.equipment_control.cm110 as cm110
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
myk2450=k2450.k2450("GPIB0::27::INSTR",timeout=10e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
units={"voltage":"V", "current":"A", "resistance":"Ohms"}        

source_mode = "voltage"
measurement_mode = "current"
compliance = 5e-3
autozero = True
nplc = 0.2
digits = 6
continuous_trigger = False
disp_enable = True

n_cycle=1
vmin=0
vmax=7
n_sample=301
double=True
bias_list=np.linspace(vmin,vmax,n_sample)
if double:
    bias_list=np.append(bias_list,bias_list[-2::-1])
prefix='path_to_file_with_prefix'
file_path = prefix+'_rep%d.txt'%(n_cycle)

t_init=time.time()

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

data=np.zeros((len(bias_list),n_cycle))

for cycle in range(n_cycle):
    print("- Cycle %d ..."%cycle,end="")
    tcycle=time.time()
    i=0
    for bias_source in bias_list:
        myk2450.set_source(bias_source)
        data[i,cycle]=float(myk2450.read_single())
        i+=1
    print(" done in %d s"%(time.time()-tcycle))

myk2450.set_output("OFF")
print("Measurement done in %d s"%(time.time()-t_init))
# =============================================================================
# 7. Close connection
# =============================================================================
myk2450.close_connection()


# =============================================================================
# 8. Save data
# =============================================================================
header="%s (%s)"%(source_mode,units[source_mode])

for cycle in range(n_cycle):
    header+=", %s (%s)"%(measurement_mode,units[measurement_mode])
    
data_to_write=np.append(np.transpose([bias_list]),data,axis=1)
eq.write_in_file(file_path,data_to_write,header=header,date=True,overwrite=True)

# =============================================================================
# 9. Plot data
# =============================================================================
from matplotlib import colormaps
cmap=colormaps['coolwarm']
color_list=cmap(np.linspace(0,1,n_cycle))

fig,ax=plt.subplots()
ax.set_xlabel("Voltage (V)")
ax.set_ylabel("Current (A)")
#ax.set_yscale("log")
for cycle in range(n_cycle):
    ax.plot(bias_list,abs(data[:,cycle]),color=color_list[cycle])
plt.savefig(file_path.replace(".txt",".png").replace("Andrea_data/","Andrea_figures/"),dpi=200)
plt.show(block=True)