import dopes.equipment_control.equipment as equipment
import time
import numpy as np
class k2400(equipment.equipment):
    
    """Class to control K2400 SMU"""
    model="K2400"
    company="Keithley"
    url="https://www.tek.com/en/products/keithley/digital-multimeter/dmm7510"


    def initialize(self, source_mode,measurement_mode, compliance, autozero=True, nplc=1,digits=6,continuous_trigger=False,disp_enable=True):
        """ Function to initialize the K2400 SMU  with the desired settings
        
            args:
               \n\t- source_mode (string) : source mode of the SMU ("current" or "voltage")
               \n\t- measurement_mode (string) : measurement mode of the SMU ("current", "voltage" or "resistance")
               \n\t- compliance (scalar) : compliance of the source
               \n\t- autozero (boolean) : if true, enable autozero of the SMU
               \n\t- nplc (scalar) : set NPLC to set the integration time for the measurement. For a NPLC of 1, the integration period would be 1/50 (for 50Hz line power) which is 20 msec
               \n\t- digits (int) : display resolution in number of bits
               \n\t- continuous_trigger (boolean) : if true, the display of the equipment does not freeze after a measurement. When disabled, the instrument operates at a higher speed
               \n\t- disp_enable (boolean) : if true, enable the front panel display circuitry. When disabled, the instrument operates at a higher speed
        """
        mode_name={"voltage":"VOLT", "current":"CURR", "resistance":"RES"}        
        self.output_state="OFF"
        self.pyvisa_resource.write("*RST")
        self.source_mode=source_mode
        self.continuous_trigger=continuous_trigger
        
        if source_mode=="voltage":
            self.pyvisa_resource.write(":SOUR:FUNC VOLT")   
            self.pyvisa_resource.write(":SENS:CURR:PROT %E"%compliance)     # set automatic range

        if source_mode=="current":
            self.pyvisa_resource.write(":SOUR:FUNC CURR")   
            self.pyvisa_resource.write(":SENS:VOLT:PROT %E"%compliance)     # set automatic range



        if measurement_mode=="voltage":
            self.pyvisa_resource.write(":SENS:FUNC 'VOLT'")   
            self.pyvisa_resource.write(":SENS:VOLT:RANG:AUTO ON")     # set automatic range

        elif measurement_mode=="current":
            self.pyvisa_resource.write(":SENS:FUNC 'CURR'")   
            self.pyvisa_resource.write(":SENS:CURR:RANG:AUTO ON")     # set automatic range

        elif measurement_mode=="resistance":
            self.pyvisa_resource.write(":SENS:FUNC 'RES'") 
            self.pyvisa_resource.write(":SENS:RES:RANG:AUTO ON")     # set automatic range
            
                   
        self.pyvisa_resource.write(":DISP:DIG %d"%digits)     # Query largest allowable display resolution
        if disp_enable:
            self.pyvisa_resource.write(":DISP:ENAB ON")     # This command is used to enable and disable the front panel display circuitry. When disabled, the instrument operates at a higher speed.
        else:
            self.pyvisa_resource.write(":DISP:ENAB OFF")     

            
        if autozero:
            self.pyvisa_resource.write(":SYST:AZER:STAT ON")          # enable auto-zero
        else:
            self.pyvisa_resource.write(":SYST:AZER:STAT OFF")
        

        self.pyvisa_resource.write(":SENS:%s:NPLC %d"%(mode_name[measurement_mode],nplc))           # set NPLC. For a PLC of 1, the integration period would be 1/50 (for 50Hz line power) which is 20 msec
        self.pyvisa_resource.write(":FORM:ELEM %s"%mode_name[measurement_mode])
        
        if continuous_trigger:
            self.pyvisa_resource.write(":ARM:SOUR TIMer")
            self.pyvisa_resource.write(":ARM:TIMer 0.001") # minimal timer is 1 ms
            self.pyvisa_resource.write(":ARM:COUNT INF")
        else:
            self.pyvisa_resource.write(":ARM:SOUR IMMediate")

    def read_single(self):
        
        """ Function to read a single measurement data. The output is turn off at the end of the measurement only if continuous_trigger and output_state have been initialized as false and off
        
            return:
               \n\t- data (float) : float with the value of the measurement
        """
        self.pyvisa_resource.write(":OUTP ON")

        if self.continuous_trigger:
            self.pyvisa_resource.write(":ABORt")
            self.pyvisa_resource.write(":ARM:COUNT 1")
            data=float(self.pyvisa_resource.query(":READ?"))
            self.pyvisa_resource.write(":ARM:COUNT INF")
            self.pyvisa_resource.write(":INIT")
            
        else:
            data=float(self.pyvisa_resource.query("READ?"))
            self.pyvisa_resource.write(":OUTP %s"%self.output_state)


        return data
    
    def set_source(self,value):
                
        """ Function to set the source bias
        
            args:
               \n\t- value (scalar) : value of the bias point
        """
        if self.source_mode=="current":
            self.pyvisa_resource.write(":SOUR:CURR %.2E"%value)           #set output voltage
        elif self.source_mode=="voltage":
            self.pyvisa_resource.write(":SOUR:VOLT %.2E"%value)           #set output voltage


    def set_output(self,output_state="ON"):
                        
        """ Function to set the state of the outpute 
        
            args:
               \n\t- output_state (string) : "ON" and "OFF" to turn the output on or off
        """
        self.output_state=output_state

        self.pyvisa_resource.write(":OUTP %s"%output_state)
        if self.continuous_trigger:
            self.pyvisa_resource.write(":INIT")

    def set_buffer_sweep(self,start,stop,buffer_point):
        
        """ Function to set the buffer measurements in (linear) sweep mode
        
            args:
               \n\t- start (scalar) : the starting value for the voltage or current sweep
               \n\t- stop (scalar) : the ending value for the voltage or current sweep
               \n\t- buffer_point (integer) : the number of points for the sweep. 
        """
        
        self.buffer_points=int(buffer_point)
        self.pyvisa_resource.write(":TRACE:CLEAR")
        self.pyvisa_resource.write(":TRACE:POINTS %d"%buffer_point)
        self.pyvisa_resource.write(":TRACE:FEED SENSE")

        self.pyvisa_resource.write(":SOURCE:%s:START %.3f"%(self.source_mode,start))
        self.pyvisa_resource.write(":SOURCE:%s:STOP %.3f"%(self.source_mode,stop))
        self.pyvisa_resource.write(":SOURCE:SWEEP:POINTS %d"%(buffer_point))
        self.pyvisa_resource.write(":SOURCE:SWEEP:RANGING AUTO")
        self.pyvisa_resource.write(":CURRENT:MODE SWEEP")
        self.pyvisa_resource.write(":TRIGGER:COUNT %d"%buffer_point)

    def set_buffer_list(self,bias_list):
        """ Function to set the buffer measurements in list mode
        
            args:
               \n\t- bias_list (1D array) : the list of bias points for the measurements. The maximal size of the list is 2500 
        """
        buffer_point=len(bias_list)
        self.buffer_points=int(buffer_point)
            
        self.pyvisa_resource.write(":TRACE:CLEAR")
        self.pyvisa_resource.write(":TRACE:FEED SENSE")

        self.pyvisa_resource.write(":TRACE:POINTS %d"%buffer_point)
        self.pyvisa_resource.write(":SOURCE:%s:MODE LIST"%self.source_mode)
        self.pyvisa_resource.write(":TRIGGER:COUNT %d"%buffer_point)

        n_point=buffer_point
        i=0
        while buffer_point>0:
            n_point=np.min((100,buffer_point))
            bias_list_str=""
            for j in range(n_point):
                bias_list_str+="%.3f, "%bias_list[i+j]
            if i==0:
                self.pyvisa_resource.write(":SOURCE:LIST:%s %s"%(self.source_mode,bias_list_str[:-2]))
            else:
                self.pyvisa_resource.write(":SOURCE:LIST:%s:APPEND %s"%(self.source_mode,bias_list_str[:-2]))
            buffer_point-=n_point
            i+=n_point




    def start_buffer(self,wait=1):
        """ Function to start the measurements using the internal buffer of the equipment. 
        
            args:
               \n\t- wait (scalar) : the small waiting time that could be set to avoid synchronisation issue.
        """
        self.pyvisa_resource.write(":TRACE:FEED:CONTROL NEXT")
        self.pyvisa_resource.write(":INITIATE")
        time.sleep(wait)
        
    def read_buffer(self):
        """ Function to read the measurement buffer
        
            return:
               \n\t- data (list) : list of floats of the measurements taken by the instruments.
        """

        data=self.pyvisa_resource.query(":TRACe:DATA?")
        return [float(dat) for dat in data.split(",")]

 
        
