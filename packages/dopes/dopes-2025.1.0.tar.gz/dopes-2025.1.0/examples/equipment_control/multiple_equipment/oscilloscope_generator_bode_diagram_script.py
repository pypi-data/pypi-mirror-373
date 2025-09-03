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
import dopes.equipment_control.signal_generator as signal_generator

import matplotlib.pyplot as plt
import numpy as np
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
myoscilloscope=oscilloscope.oscilloscope('USB0::0x0699::0x0522::C012270::INSTR',timeout=20e3)
mygenerator=signal_generator.signal_generator("USB0::0x0699::0x0349::C012340::INSTR",timeout=5e3)

# =============================================================================
# 4. Measurement parameters
# =============================================================================
channel_used={"CH1":"ON","CH2":"ON","CH3":"OFF","CH4":"OFF"}
waveform="sin"
amplitude=1 
offset=0.0
frequency_list=np.logspace(1,6,11)
input_channel="CH1"
output_channel="CH2"

# =============================================================================
# 5. Initialization of the equipment
# =============================================================================
myoscilloscope.initialize(channel_used=channel_used, autoset=False, continuous=False, average=False,num_average=10,data_bytes=1)

myoscilloscope.set_channel_properties(input_channel, scale=0.5,coupling="DC")
myoscilloscope.set_channel_properties(output_channel, scale=0.5,coupling="DC")
myoscilloscope.set_horizontal_properties(record_length=1e4,sample_rate=1e6)
myoscilloscope.set_edge_trigger(input_channel,level=0)

mygenerator.initialize(waveform=waveform, freq=1, amp=amplitude, offset=offset)
mygenerator.set_output("ON")

# =============================================================================
# 6. Measurement script
# =============================================================================
bode_amplitude=np.zeros(len(frequency_list))
bode_phase=np.zeros(len(frequency_list))

n_period=10
n_point_per_period=100
i=0
for freq in frequency_list:
    period=1/freq 
    sample_rate=n_point_per_period*freq
    record_length=period*n_period * sample_rate
    myoscilloscope.set_horizontal_properties(record_length=record_length,sample_rate=sample_rate)
    mygenerator.set_frequency(freq)  
    
    time.sleep(1)
    _,_,meas_dic=myoscilloscope.acquire_single_channel_with_measurement(["PK2PK"],channel=output_channel)
    myoscilloscope.set_channel_properties(output_channel, scale=meas_dic["PK2PK"]/8,coupling="DC")
    t_data,data,meas_dic=myoscilloscope.acquire_channels_with_measurement(["RMS","PHASE"],channel=output_channel,ref_channel=input_channel)
    bode_amplitude[i]=20*np.log(meas_dic[output_channel]["RMS"]/meas_dic[input_channel]["RMS"])
    bode_phase[i]=meas_dic[output_channel]["PHASE"]

    
    
    i+=1

# =============================================================================
# 7. Close connection
# =============================================================================
myoscilloscope.close_connection()
mygenerator.close_connection()

# =============================================================================
# 8. Plot figure
# =============================================================================
fig,ax=plt.subplots()
fig.set_dpi(200)
ax.set_title('Bode Diagram') # plot label
ax.set_xlabel('Frequency Hz') # x label
ax.set_xscale("log")
ax.set_ylabel('Amplitude (dB)') # y label
secax=ax.twinx()
secax.set_ylabel('Phase (°)') # y label

ax.plot(frequency_list,bode_amplitude)
secax.plot(frequency_list,bode_phase,ls=":")

# =============================================================================
# 9. Save data
# =============================================================================
data_to_write=np.transpose([frequency_list,bode_amplitude,bode_phase])
eq.write_in_file("temp.txt",data_to_write,header=None,date=True,overwrite=True)
