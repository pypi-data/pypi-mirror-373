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
import dopes.equipment_control.oscilloscope as oscilloscope
import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# 2. List  available connections (dopes use pyvisa package for communicate with most equipments)
# =============================================================================
rm=eq.resource_manager()
list_connections= eq.available_connections()
print("Available connections: %s"%str(list_connections))

# =============================================================================
# 3. Connection to the equipment
# =============================================================================
myoscilloscope=oscilloscope.oscilloscope('USB0::0x0699::0x0522::C012270::INSTR',timeout=20e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
channel_used={"CH1":"ON","CH2":"ON","CH3":"OFF","CH4":"OFF"}

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
myoscilloscope.initialize(channel_used=channel_used, autoset=False, continuous=False, average=False,data_bytes=1)

myoscilloscope.set_channel_properties("CH1", scale=1,coupling="DC")
myoscilloscope.set_channel_properties("CH2", scale=1,coupling="DC")
myoscilloscope.set_horizontal_properties(record_length=2e5,sample_rate=1e6)
# myoscilloscope.set_edge_trigger("CH1",level=1e-3)

# =============================================================================
# 6. Measurement script
# =============================================================================
t_data,data=myoscilloscope.acquire_all_channels(force_trig=True)
amplitude_ch1=myoscilloscope.get_measurement('CH1',"AMPLITUDE")
amplitude_ch2=myoscilloscope.get_measurement('CH2',"AMPLITUDE") 

# =============================================================================
# 7. Close connection
# =============================================================================
myoscilloscope.close_connection()

# =============================================================================
# 8. Plot figure
# =============================================================================
fig,ax=plt.subplots()
fig.set_dpi(200)
ax.set_xlabel('Time (seconds)') # x label
ax.set_ylabel('Voltage (volts)') # y label
ax.plot(t_data["CH1"],data["CH1"])
ax.plot(t_data["CH2"],data["CH2"])

# =============================================================================
# 9. Save data
# =============================================================================
data_to_write=np.transpose([t_data["CH1"],data["CH1"],data["CH2"]])
eq.write_in_file("temp.txt",data_to_write,header=None,date=True,overwrite=False)
