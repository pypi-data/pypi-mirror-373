import dopes.equipment_control.equipment as equipment
import time

class dmm(equipment.equipment):
    
    """Class to control digital multimeter"""
    model="DMM7510, DMM6500 or K2000"
    company="Keithley"
    url="https://www.tek.com/en/products/keithley/benchtop-digital-multimeter"

    def initialize(self, mode, autozero=True, nplc=1,timeout=10e3,digits=6,continuous_trigger=False,disp_enable=True,k2000=False):
        
        """ Function to initialize the K2400 SMU  with the desired settings
        
            args:
               \n\t- mode (string) : measurement mode of the multimeter ("current", "voltage", "resistance" or "4 wires")
               \n\t- autozero (boolean) : if true, enable autozero of the SMU
               \n\t- nplc (scalar) : set NPLC to set the integration time for the measurement. For a NPLC of 1, the integration period would be 1/50 (for 50Hz line power) which is 20 msec
               \n\t- digits (int) : display resolution in number of bits
               \n\t- continuous_trigger (boolean) : if true, the display of the equipment does not freeze after a measurement. When disabled, the instrument operates at a higher speed
               \n\t- disp_enable (boolean) : if true, enable the front panel display circuitry. When disabled, the instrument operates at a higher speed
               \n\t- k2000 (boolean) : if true send instruction formatted for k2000 multimeter, otherwise send instruction for more recent multimeter such as DMM6500 and DMM7510
        """
        

        self.continuous_trigger=continuous_trigger
        self.k2000=k2000
        self.pyvisa_resource.write("*RST")
        # self.set_connection_parameter_dic({"write_termination":'\r\n',"read_termination":'\r\n',"send_end":True})

        mode_name={"voltage":"VOLT", "current":"CURR", "resistance":"RES", "4wires":"FRES", "4 wires":"FRES"}        

        self.pyvisa_resource.write(":SENS:FUNC '%s'"%mode_name[mode])           

        self.pyvisa_resource.write(":SENS:%s:RANG:AUTO ON"%mode_name[mode])     # set automatic range


        if k2000:
            self.pyvisa_resource.write(":SENS:%s:DIG %d"%(mode_name[mode],digits))    
            if disp_enable:
                self.pyvisa_resource.write(":DISP:ENAB ON")     # This command is used to enable and disable the front panel display circuitry. When disabled, the instrument operates at a higher speed.
            else:
                 self.pyvisa_resource.write(":DISP:ENAB OFF")

            if continuous_trigger:
                self.pyvisa_resource.write("INIT:CONT ON")     # able continuous triggering
            else:
                self.pyvisa_resource.write("INIT:CONT OFF")     

        else:
            if disp_enable:
                self.pyvisa_resource.write(":DISP:LIGHT:STAT ON100")     # This command is used to enable and disable the front panel display circuitry. When disabled, the instrument operates at a higher speed.
            else:
                 self.pyvisa_resource.write(":DISP:LIGHT:STAT OFF")

            self.pyvisa_resource.write(":DISP:%s:DIG %d"%(mode_name[mode],digits))   
            self.pyvisa_resource.write(":SENS:%s:NPLC %d"%(mode_name[mode],nplc))           # set NPLC. For a PLC of 1, the integration period would be 1/50 (for 50Hz line power) which is 20 msec
           
            if autozero:
                self.pyvisa_resource.write(":%s:AZER ON"%mode_name[mode])          # enable auto-zero
            else:
                self.pyvisa_resource.write(":%s:AZER OFF"%mode_name[mode])

            if continuous_trigger:
                self.pyvisa_resource.write("TRIG:CONT REST")     # able continuous triggering
            else:
                self.pyvisa_resource.write("TRIG:CONT OFF")

    def read_single(self):
        """ Function to read a single measurement data. The output is turn off at the end of the measurement only if continuous_trigger and output_state have been initialized as false and off
        
            return:
               \n\t- data (float) : float with the value of the measurement
        """
        
        if self.k2000:
            if self.continuous_trigger:
                data=self.pyvisa_resource.query("FETCH?")
            else:
                data=self.pyvisa_resource.query("READ?")
        else:
            if self.continuous_trigger:
                self.pyvisa_resource.write("TRIG:CONT OFF")
                time.sleep(0.1)
                data=float(self.pyvisa_resource.query("MEAS?"))
                self.pyvisa_resource.write("TRIG:CONT REST")
            else:
                data=float(self.pyvisa_resource.query("MEAS?"))

        return data
    
