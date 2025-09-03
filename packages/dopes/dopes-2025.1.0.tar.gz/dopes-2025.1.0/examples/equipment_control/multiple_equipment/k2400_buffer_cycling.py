

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
import dopes.equipment_control.k2400 as k2400
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
myk2400=k2400.k2400("GPIB0::27::INSTR",timeout=100e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
units={"voltage":"V", "current":"A", "resistance":"Ohms"}        

source_mode = "voltage"
measurement_mode = "current"
compliance = 1e-3
autozero = True
nplc = 0.1
digits = 6
continuous_trigger = False
disp_enable = True


n_cycle=2
vmin=0
vmax=4
n_sample=400*2+1 # max 2500 point in the buffer so n_sample<1250 if double==True
double=True
bias_list=np.linspace(vmin,vmax,n_sample)
if double:
    bias_list=np.append(bias_list,bias_list[-2::-1])
prefix='data/VO2_Wafer01_Ft_Loic_D01_L0.6_W10_Tamb'
file_path = prefix+'_mardi_test04_postilum_rep%d_dark.txt'%(n_cycle)
#file_path="test01.txt"
t_init=time.time()

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
myk2400.initialize(source_mode=source_mode, measurement_mode=measurement_mode,
                   compliance=compliance, autozero=autozero, digits=digits,
                   continuous_trigger=continuous_trigger,disp_enable=disp_enable, nplc=nplc)
myk2400.set_source(vmin)
myk2400.set_output("ON")
time.sleep(1)

# =============================================================================
# 6. Measurement script
# =============================================================================
data=np.zeros((len(bias_list),n_cycle))

for cycle in range(n_cycle):
    print("- Cycle %d ..."%cycle,end="")
    tcycle=time.time()
    myk2400.set_buffer_list(bias_list)
    myk2400.start_buffer(wait=1)

    data[:,cycle]=myk2400.read_buffer()
    print(" done in %d s"%(time.time()-tcycle))

myk2400.set_output("OFF")
print("Measurement done in %d s"%(time.time()-t_init))
# =============================================================================
# 7. Close connection
# =============================================================================
myk2400.close_connection()

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
ax.set_yscale("log")
for cycle in range(n_cycle):
    ax.plot(bias_list,abs(data[:,cycle]),color=color_list[cycle])
plt.savefig(file_path.replace(".txt",".png").replace("data/","figures/"),dpi=200)
plt.show(block=True)