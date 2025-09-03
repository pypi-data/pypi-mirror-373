import dopes.equipment_control.equipment as equipment
import pyvisa
import time
import numpy as np

class oscilloscope(equipment.equipment):
    
    """Class to control tektronix oscilloscope"""
    
    model="MSO56,TBS2000,MSO2024"
    company="tektronix"
    url="https://www.tek.com/en/products/oscilloscopes/"
    
    def initialize(self, channel_used={"CH1":"ON","CH2":"OFF","CH3":"OFF","CH4":"OFF"},
                   autoset=True,continuous=True, num_sequence=1,high_resolution=False, average=False,num_average=10,data_bytes=1, command_delay=0.02, query_delay=0.1, sync_delay=0.2):
        """ Function to initialize the Tektronix oscilloscope  with the desired settings
        
            args:
               \n\t- channel_used (dictionnary) : dictionnary for which the key are the name of the channel ("CH1","CH2","CH3","CH4") and the value is "ON" or "OFF" to activate or desactivate the channel
               \n\t- autoset (boolean) : if True, the oscilloscope performs an autoset during the initialization
               \n\t- continuous (boolean) : if True, the oscilloscope continue running after taken an acquisition
               \n\t- num_sequence (integer) : the number of sequence the oscilloscope will take for each acquisition. This is not an averaging.
               \n\t- high_resolution (boolean) : if True, the oscilloscope will enter high resolution mode, i.e. averaging over a fixed period in fast frame acquisition. High resolution is automatically turn on when 2 bytes are asked with TBS oscilloscope
               \n\t- average (boolean) : if True, the oscilloscope will take several signal to perform an averaging
               \n\t- num_average (integer) : the number of acquisitions to make the averaging
               \n\t- data_bytes (integer) : the number of bytes for the vertical resolution of the data (1 or 2 accepted)
        """
        self.SMALL_SLEEP=command_delay
        self.MID_SLEEP=query_delay
        self.BIG_SLEEP=sync_delay
        
        self.channel_used=channel_used
        self.average=average
        self.num_average=num_average
        self.data_bytes=data_bytes
        
        
        self.pyvisa_resource.encoding = 'ascii'
        self.pyvisa_resource.read_termination = '\n'
        self.pyvisa_resource.write_termination = None
        self.pyvisa_resource.send_termination = False
        
        identity=self.pyvisa_resource.query("*IDN?")
        self.model_tbs= (identity.upper().find("TBS")>=0)
        
        if self.model_tbs and data_bytes==2 and high_resolution==False:
            high_resolution=True
            print("TBS oscilloscope can only work under 2 bytes with high resolution mode.\nThe equipment has been swith to high resolution mode.")

        self.pyvisa_resource.write('*CLS') # clear ESR
        self.pyvisa_resource.write('*RST') # clear ESR

        for key in channel_used.keys():        
            self.pyvisa_resource.write('SELECT:%s %s'%(key,channel_used[key]))
                

        if autoset:
            self.pyvisa_resource.write('autoset EXECUTE') # autoset
            time.sleep(5)
        else:
            self.pyvisa_resource.write('HORIZONTAL:MODE AUTO')
            time.sleep(1)

        self.pyvisa_resource.write('ACQUIRE:STATE OFF')

        self.pyvisa_resource.query('*opc?',delay=1) # sync

        self.pyvisa_resource.write("HEADER 0")
        self.pyvisa_resource.write("DATA:ENCDG RIBINARY")   # Signed Binary Format, LSB order
        self.pyvisa_resource.write("DATA:WIDTH %d"%data_bytes) # 1 byte per sample
        self.pyvisa_resource.write("DATA:START 1")
        record = int(self.pyvisa_resource.query('horizontal:recordlength?',delay=self.MID_SLEEP))
        self.pyvisa_resource.write('data:stop {}'.format(record)) # last sample
        

        if average:
            self.pyvisa_resource.write('ACQUIRE:MODE AVERAGE')
            self.pyvisa_resource.write('ACQUIRE:NUMAVG %d'%num_average)
        elif high_resolution:
            self.pyvisa_resource.write('ACQUIRE:MODE HIRES')
        else:
            self.pyvisa_resource.write('ACQUIRE:MODE SAMPLE')
        
        if continuous:
            self.pyvisa_resource.write('ACQUIRE:STOPAFTER RUNSTOP')
            self.pyvisa_resource.write('ACQUIRE:STATE RUN')
        else:
            self.pyvisa_resource.write('ACQUIRE:STOPAFTER SEQUENCE')
            self.pyvisa_resource.write('ACQUIRE:SEQUENCE:NUMSEQUENCE %d'%num_sequence)    

    def acquire_wave(self):
        """ Intermediate function to acquire the data from the Tektronix oscilloscope
        
            return:
               \n\t- scaled_time, scaled_wave (numpy array) : time and waveform data vectors

        """
        
        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)
            
        if self.data_bytes==1:
            datatype="b"
        elif self.data_bytes==2:
            datatype="h"
        time.sleep(self.SMALL_SLEEP)               
        bin_wave = self.pyvisa_resource.query_binary_values('curve?', datatype=datatype, container=np.array,delay=self.MID_SLEEP)
        time.sleep(self.SMALL_SLEEP)

        tscale = float(self.pyvisa_resource.query('wfmoutpre:xincr?',delay=self.MID_SLEEP))
        time.sleep(self.SMALL_SLEEP)
        tstart = float(self.pyvisa_resource.query('wfmoutpre:xzero?',delay=self.MID_SLEEP))
        time.sleep(self.SMALL_SLEEP)
        vscale = float(self.pyvisa_resource.query('wfmoutpre:ymult?',delay=self.MID_SLEEP)) # volts / level
        time.sleep(self.SMALL_SLEEP)
        voff = float(self.pyvisa_resource.query('wfmoutpre:yzero?',delay=self.MID_SLEEP)) # reference voltage
        time.sleep(self.SMALL_SLEEP)
        vpos = float(self.pyvisa_resource.query('wfmoutpre:yoff?',delay=self.MID_SLEEP)) # reference position (level)
        time.sleep(self.SMALL_SLEEP)
        record = int(self.pyvisa_resource.query('horizontal:recordlength?',delay=self.MID_SLEEP))
        # create scaled vectors
        # horizontal (time)
        total_time = tscale * record
        tstop = tstart + total_time
        scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype=datatype) # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff
        
        return scaled_time, scaled_wave
            
    def acquire_single_channel(self,channel="CH1", force_trig=False):
        """ Function to acquire the data of a single channel from the Tektronix oscilloscope 
            
            args:
                \n\t- channel (string) : the channel from which the data has to be taken
                \n\t- force_trig (boolean) : if True, force the trigger to acquire the data. If False, an other trigger mechanism has to be used or manual triggering has to be done.
            return:
               \n\t- scaled_time, scaled_wave (numpy array) : time and waveform data vectors

        """
        self.pyvisa_resource.write('ACQUIRE:STATE ON')
        time.sleep(self.MID_SLEEP)
        if force_trig:
            if self.average:
                for i in range(self.num_average):
                    self.pyvisa_resource.write('TRIGGER FORCE')
                    time.sleep(self.MID_SLEEP)
            else:
                self.pyvisa_resource.write('TRIGGER FORCE')

        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)
        time.sleep(self.SMALL_SLEEP)

        self.pyvisa_resource.write("DATA:SOURCE %s"%channel)
        time.sleep(self.MID_SLEEP)
        scaled_time, scaled_wave=self.acquire_wave()
        return scaled_time, scaled_wave
        
    def acquire_all_channels(self, force_trig=False):
        """ Function to acquire the data of all active channels from the Tektronix oscilloscope 
            
            args:
                \n\t- force_trig (boolean) : if True, force the trigger to acquire the data. If False, an other trigger mechanism has to be used or manual triggering has to be done.
            return:
               \n\t- scaled_time, scaled_wave (numpy array) : time and waveform data vectors

        """
        
        self.pyvisa_resource.write('ACQUIRE:STATE ON')
        time.sleep(self.MID_SLEEP)

        if self.average:
            for i in range(self.num_average):
                self.pyvisa_resource.write('TRIGGER FORCE')
                time.sleep(self.MID_SLEEP)
        else:
            time.sleep(self.MID_SLEEP)
            self.pyvisa_resource.write('TRIGGER FORCE')


        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)

        scaled_time={}
        scaled_wave={}
        for channel in self.channel_used.keys():
            if self.channel_used[channel].upper()=="ON" or self.channel_used[channel]==1:
                self.pyvisa_resource.write("DATA:SOURCE %s"%channel)
                scaled_time[channel], scaled_wave[channel]=self.acquire_wave()
                time.sleep(self.MID_SLEEP)

        return scaled_time, scaled_wave

    def get_measurement(self,channel,meas_type,ref_channel="CH1"):
        """ Function to get the measurement from a previous acquisition  
            
            args:
                \n\t- channel (string) : the channel on which the measurement has to be done
                \n\t- meas_type (string) : the measurement that has to be done. Possible measurements are "FREQUENCY", "AMPLITUDE", "MIN", "MAX", "MEAN", "RMS", "PHASE", "PK2Pk"
                \n\t- ref_channel (string) : the reference channel if phase measurement is asked

            return:
               \n\t- meas (scalar) : the value of the measurement taken
 
        """
        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)
    
        time.sleep(self.SMALL_SLEEP)
    
        if meas_type.upper()=="PHASE":
            self.pyvisa_resource.write('MEASUREMENT:IMMED:TYPE %s'%meas_type)
            time.sleep(self.SMALL_SLEEP)
            self.pyvisa_resource.write('MEASUREMENT:IMMED:SOURCE1 %s'%channel)
            time.sleep(self.SMALL_SLEEP)
            self.pyvisa_resource.write('MEASUREMENT:IMMED:SOURCE2 %s'%ref_channel)
            time.sleep(self.SMALL_SLEEP)
            self.pyvisa_resource.write("MEASUREMENT:IMMED:TOEDGE OPPositeas")
            time.sleep(self.SMALL_SLEEP)
            print(self.pyvisa_resource.query('MEASUREMENT:IMMED:VALUE?', delay=self.MID_SLEEP))
            meas=float(self.pyvisa_resource.query('MEASUREMENT:IMMED:VALUE?', delay=self.MID_SLEEP))-180
            
        else:
            self.pyvisa_resource.write('MEASUREMENT:IMMED:TYPE %s'%meas_type)
            time.sleep(self.SMALL_SLEEP)
    
            self.pyvisa_resource.write('MEASUREMENT:IMMED:SOURCE1 %s'%channel)
            time.sleep(self.SMALL_SLEEP)
            meas=self.pyvisa_resource.query('MEASUREMENT:IMMED:VALUE?', delay=self.BIG_SLEEP)
        return float(meas)
    
    def get_measurement_list(self,channel,meas_list,ref_channel="CH1"):
        """ Function to get a list of measurements from a previous acquisition  
            
            args:
                \n\t- channel (string) : the channel on which the measurement has to be done
                \n\t- meas_list (list of string) : the list of measurements that have to be done. Possible measurements are "FREQUENCY", "AMPLITUDE", "MIN", "MAX", "MEAN", "RMS", "PHASE", "PK2Pk"
                \n\t- ref_channel (string) : the reference channel if phase measurement is asked

            return:
               \n\t- meas_dic (dictionnary) : dictionnary with the value of the measurements. The keys of the dictionnary are meas_list
 
        """        
        meas_dic={}
        for meas_type in meas_list:
            time.sleep(self.SMALL_SLEEP)
            meas_dic[meas_type]=self.get_measurement(channel,meas_type,ref_channel)
    
            
        return meas_dic
        
    
    def acquire_channels_with_measurement(self,meas_list,force_trig=False,ref_channel="CH1"):
        """ Function to acquire the data of all active channels from the Tektronix oscilloscope along a list of measurements
            
            args:
                \n\t- meas_list (list of string) : the list of measurements that have to be done. Possible measurements are "FREQUENCY", "AMPLITUDE", "MIN", "MAX", "MEAN", "RMS", "PHASE", "PK2Pk"
                \n\t- ref_channel (string) : the reference channel if phase measurement is asked
                \n\t- force_trig (boolean) : if True, force the trigger to acquire the data. If False, an other trigger mechanism has to be used or manual triggering has to be done.
            return:
               \n\t- scaled_time, scaled_wave (numpy array) : time and waveform data vectors
               \n\t- measurement (dictionnary) : dictionnary with the value of the measurements. The first key of the dictionnary is the channel (ex. "CH1") while the second key is the measurement name from meas_list. For example, measurement["CH1"]["AMPLITUDE"] gives the amplitude calculated from the channel 1 signal
    
        """
        
        self.pyvisa_resource.write('ACQUIRE:STATE ON')
        time.sleep(self.MID_SLEEP)
    
        if self.average:
            for i in range(self.num_average):
                self.pyvisa_resource.write('TRIGGER FORCE')
                time.sleep(self.MID_SLEEP)
        else:
            self.pyvisa_resource.write('TRIGGER FORCE')
    
        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)
    
        time.sleep(self.SMALL_SLEEP)
    
        scaled_time={}
        scaled_wave={}
        measurement={}
    
        for channel in self.channel_used.keys():
            if self.channel_used[channel].upper()=="ON" or self.channel_used[channel]==1:
                self.pyvisa_resource.write("DATA:SOURCE1 %s"%channel)
                time.sleep(self.MID_SLEEP)
                scaled_time[channel], scaled_wave[channel]=self.acquire_wave()
                measurement[channel]=self.get_measurement_list(channel,meas_list,ref_channel)
    
        return scaled_time, scaled_wave, measurement
    
    def acquire_single_channel_with_measurement(self,meas_list,channel,ref_channel="CH1", force_trig=False):
        """ Function to acquire the data of a single channel from the Tektronix oscilloscope along a list of measurements
            
            args:
                \n\t- meas_list (list of string) : the list of measurements that have to be done. Possible measurements are "FREQUENCY", "AMPLITUDE", "MIN", "MAX", "MEAN", "RMS", "PHASE", "PK2Pk"
                \n\t- channel (string) : the channel on which the measurement has to be done
                \n\t- ref_channel (string) : the reference channel if phase measurement is asked
                \n\t- force_trig (boolean) : if True, force the trigger to acquire the data. If False, an other trigger mechanism has to be used or manual triggering has to be done.
            return:
               \n\t- scaled_time, scaled_wave (numpy array) : time and waveform data vectors
               \n\t- measurement (dictionnary) : dictionnary with the value of the measurements. The keys of the dictionnary are meas_list
                
        """
        self.pyvisa_resource.write('ACQUIRE:STATE ON')
        time.sleep(self.MID_SLEEP)
        if force_trig:
            if self.average:
                for i in range(self.num_average):
                    self.pyvisa_resource.write('TRIGGER FORCE')
                    time.sleep(self.MID_SLEEP)
            else:
                self.pyvisa_resource.write('TRIGGER FORCE')
    
        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)
    
        time.sleep(self.SMALL_SLEEP)
    
        self.pyvisa_resource.write("DATA:SOURCE1 %s"%channel)
        time.sleep(self.MID_SLEEP)
        scaled_time, scaled_wave=self.acquire_wave()
        measurement=self.get_measurement_list(channel,meas_list,ref_channel)
        return scaled_time, scaled_wave,measurement
        
    def set_edge_trigger(self,channel="CH1", level=0):
        """ Function to set a rising edge trigger 
            
            args:
                \n\t- channel (string) : specify the channel for the triggering mechanism
                \n\t- level (scalar) : the voltage level of trigger

        """
        
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('TRIGger:A:TYPe EDGE')
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('TRIGger:A:EDGE:SOUrce %s'%channel)
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('TRIGger:A:LEVel:%s %f'%(channel,level))
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write("TRIG:A:EDGE:SLOPE RIS")

        
    def set_horizontal_properties(self,record_length,sample_rate):
        """ Function to set the horizontal (time axis) properties of the oscilloscope 
            
            args:
                \n\t- record_length (integer) : specify the number of points for the acquisition. For TBS2000, the suppored values are: 1000, 2000, 20000, 200000, 2000000, and 5000000. For MSO2024, the suppored values are 100000, and 1000000.
                \n\t- sample_rate (scalar) : specify the sampling rate in samples/s for the acquisition. The total time window can then be calculated as record_length/sampling_rate

        """

        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)

        # record_length max = 125e6
        # sample_rate max = 500e9 sample/seconds
        time.sleep(self.SMALL_SLEEP)

        self.pyvisa_resource.write('HORIZONTAL:MODE MANUAL')
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('HORizontal:MODe:MANual:CONFIGure RECORDLength')
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('HORIZONTAL:RECORDLENGTH %e'%record_length)
        time.sleep(self.SMALL_SLEEP)
        true_record_length = int(self.pyvisa_resource.query('horizontal:recordlength?',delay=self.MID_SLEEP))
        if self.model_tbs:
            n_divisions=int(float(self.pyvisa_resource.query('HORizontal:DIVisions?')))
            self.pyvisa_resource.write('HORIZONTAL:SCALE %.3e'%(true_record_length/sample_rate/n_divisions))            
        else:            
            self.pyvisa_resource.write('HORIZONTAL:SAMPLERATE %e'%sample_rate)
        
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('data:stop %e'%true_record_length) # last sample

        
    def set_channel_properties(self, channel, scale, offset=0, coupling="DC", bandwidth="FULL", termination=1e6):
        """ Function to set the properties of a channel of the oscilloscope 
            
            args:
                \n\t- channel (string) : the channel from which the data has to be taken
                \n\t- scale (scalar) : the dimension of one vertical divistion in Volts. The full scale is made of 10 divisions
                \n\t- offset (scalar) : the offset in volt of the vertical position of the signal
                \n\t- coupling (string) : the coupling of the channel. Choice between "AC" to remove the DC component or "DC" to keep it
                \n\t- bandwidth (scalar or string) : the selectable low-pass bandwidth limit filter of the specified channel. "FULL" disables any optional bandwidth limiting. The specified channel operates at its maximum bandwidth.
                \n\t- termination (scalar) : The vertical termination for the specified analog channel. Choice between 50 or 1e6 Ohms. 

        """
        
        while float(self.pyvisa_resource.query('BUSY?',delay=self.BIG_SLEEP)):
            time.sleep(self.SMALL_SLEEP)
        time.sleep(self.SMALL_SLEEP)

        self.pyvisa_resource.write('%s:SCALE %e'%(channel,scale))
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('%s:TERmination %e'%(channel,termination))
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('%s:OFFSet %e'%(channel,offset))
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('%s:COUPLING %s'%(channel,coupling))
        time.sleep(self.SMALL_SLEEP)
        if bandwidth.upper()=="FULL":
            self.pyvisa_resource.write('%s:BANdwidth %s'%(channel,bandwidth))
        else:
            self.pyvisa_resource.write('%s:BANdwidth %e'%(channel,bandwidth))
                    
    def set_state(self, state="ON"):
        """ Function to set the acquisition state 
            
            args:
                \n\t- state (string) : When state is set to "ON" or "RUN", a new acquisition will be started. When state is set to "OFF" or "STOP", the acquisition is stopped.
                If the last acquisition was a single acquisition sequence, a new single sequence acquisition will be started. If the last acquisition was continuous, a new continuous acquisition will be started.
                If "RUN" is issued in the middle of completing a single sequence acquisition (for example, averaging or enveloping), the acquisition sequence is restarted, 
                and any accumulated data is discarded. Also, the instrument resets the number of acquisitions. If the "RUN" argument is issued while in continuous mode, a reset occurs and acquired data continues to acquire.
        """
        time.sleep(self.SMALL_SLEEP)
        self.pyvisa_resource.write('ACQUIRE:STATE %s'%state)

    def get_sample_rate(self):
        """ Function to get the effective sample rate 
            
            return:
                \n\t- sample_rate (float) : the effective sample rate
        
        """
        
        time.sleep(self.SMALL_SLEEP)
        sample_rate=float(self.pyvisa_resource.query('HORizontal:SAMPLERate?'))
        return sample_rate
        
    def force_trig(self):
        """ Function to force the triggering of the oscilloscope 
        """
        if self.average:
            for i in range(self.num_average):
                self.pyvisa_resource.write('TRIGGER FORCE')
                time.sleep(self.MID_SLEEP)
        else:
            self.pyvisa_resource.write('TRIGGER FORCE')
            

    