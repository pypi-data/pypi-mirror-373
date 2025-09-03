import dopes.equipment_control.equipment as equipment
class signal_generator(equipment.equipment):
    
    """Class to control Agilent 33120, Agilent 33250A and Tektronix AFG2021 signal generator"""
    model="Agilent 33120, Agilent 33250A and Tektronix AFG2021"
    company="Agilent or Tektronix"
    url=""
    
    def initialize(self, waveform="sin", freq=1e3, amp=1, offset=0, phase=0,output="off",high_impedance=True,output_impedance=50):
        """ Function to initialize the signal generator  
            
            args:
                \n\t- waveform (string) : the type of waveform. Choise between sinus ("sin" or "sinusoid"), square ("squ" or "square") or ramp ("ramp")
                \n\t- freq (scalar) : the frequency of the waveform
                \n\t- amp (scalar) : the amplitude of the waveform
                \n\t- offset (scalar) : the DC offset of the waveform
                \n\t- phase (integer) : the intial phase in degree of the waveform
                \n\t- output (string) : string to control the output state at the end of the initialization ("on" or "off")

        """
        
        identity=self.pyvisa_resource.query("*IDN?")

        self.pyvisa_resource.write("*RST")
        self.pyvisa_resource.write("FUNCTION %s"%waveform)
        
        self.pyvisa_resource.write("VOLTAGE %.3f"%amp)
        self.pyvisa_resource.write("VOLTAGE:OFFSET %.3f"%offset)

        self.pyvisa_resource.write("FREQUENCY %.1E"%freq)
        self.pyvisa_resource.write("PHASE %dDEG"%phase)
        
        if identity.upper().find("33120")<=0:
            self.pyvisa_resource.write("OUTPUT %s"%output)
       
        if (identity.upper().find("AFG")>=0):
            if high_impedance:
                self.pyvisa_resource.write("OUTPUT:IMP INF")
            else:
                self.pyvisa_resource.write("OUTPUT:IMP %d"%output_impedance)
        else:
            if high_impedance:
                self.pyvisa_resource.write("OUTPUT:LOAD INF")
            else:
                self.pyvisa_resource.write("OUTPUT:LOAD %d"%output_impedance)  
            
            
    def set_waveform(self, waveform):
        """ Function to change the waveform of the signal generator  
            
            args:
                \n\t- waveform (string) : the type of waveform. Choise between sinus ("sin" or "sinusoid"), square ("squ" or "square") or ramp ("ramp")

        """
        self.pyvisa_resource.write("FUNCTION %s"%waveform)
       
    def set_frequency(self, freq):
        """ Function to change the frequency of the signal generator  
            
            args:
                \n\t- freq (scalar) : the frequency of the waveform

        """
        self.pyvisa_resource.write("FREQUENCY %.1E"%freq)
        
    def set_amplitude(self,amp):
        """ Function to change the amplitude of the signal generator  
            
            args:
                \n\t- amp (scalar) : the amplitude of the waveform

        """
        self.pyvisa_resource.write("VOLTAGE %.3f"%amp)
        
    def set_offset(self,offset):
        """ Function to change the offset of the signal generator  
            
            args:
                \n\t- offset (scalar) : the DC offset of the waveform

        """
        self.pyvisa_resource.write("VOLTAGE:OFFSET %.3f"%offset)

    def set_phase(self,phase):
        """ Function to change the initial phase of the signal generator  
            
            args:
                \n\t- phase (integer) : the intial phase in degree of the waveform

        """
        self.pyvisa_resource.write("PHASE %dDEG"%phase)

    def set_output(self,state):
        """ Function to change the output state of the signal generator  
            
            args:
                \n\t- output (string) : string to control the output state at the end of the initialization ("on" or "off")

        """
        self.pyvisa_resource.write("OUTPUT %s"%state)

