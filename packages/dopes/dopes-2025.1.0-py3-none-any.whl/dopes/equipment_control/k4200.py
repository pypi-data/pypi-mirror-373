import dopes.equipment_control.equipment as equipment
import pyvisa
import time
import numpy as np

class k4200(equipment.equipment):
    
    """Class to control K4200 semiconductor analyzer"""
    model="K4200"
    company="Keysight"
    url="https://www.tek.com/en/products/keithley/4200a-scs-parameter-analyzer"
    
    def initialize(self, smu_type={"SMU1":"voltage","SMU2":"voltage","SMU3":"common","SMU4":"common"}, 
                   smu_used={"SMU1":"on","SMU2":"on","SMU3":"on","SMU4":"on"}, 
                   smu_master=1,smu_bias={"SMU1":0,"SMU2":0,"SMU3":0,"SMU4":0},
                   smu_compliance={"SMU1":1e-6,"SMU2":1e-6,"SMU3":1e-6,"SMU4":1e-6},
                   sweep_param={"start":0,"stop":0,"step":0}, sweep_type="linear",
                   integration_mode="S",delay_time=0,hold_time=0):
        
        
        
        """ Function to initialize the K4200 equipment with the desired settings
        
            args:
               \n\t- smu_type (dictionary) : dictionary indicated for each SMU ("SMU1","SMU2","SMU3" and "SMU4") the bias type ("voltage", "current" or "common")
               \n\t- smu_used (dictionary) : dictionary indicated for each SMU ("SMU1","SMU2","SMU3" and "SMU4") if active or not ("on" or "off")
               \n\t- smu_master (int) : integer to indicate which SMU performs the sweep
               \n\t- smu_bias (dictionary) : dictionary indicated for each SMU ("SMU1","SMU2","SMU3" and "SMU4") the bias point (scalar)
               \n\t- smu_compliance (dictionary) : dictionary indicated for each SMU ("SMU1","SMU2","SMU3" and "SMU4") the compliance (scalar)
               \n\t- sweep_param (dictionary) : dictionary indicated the starting bias ("start"), the stoping bias ("stop") and step ("step") of the sweep
               \n\t- sweep_type (string) : string to indicate linear ("linear") sweep or logarithmic ("log") sweep
               \n\t- integration_mode (string) : set the integration time parameter ("S" for short, "M" for medium and "L" for long)
               \n\t- delay_time (scalar) : the time to wait between when the output voltage is set and when the measurement is made in a sweep
               \n\t- hold_time (scalar) : hold time that delays the start of a sweep
        """
        self.smu_type=smu_type
        self.sweep_type=sweep_type
        self.smu_used=smu_used
        self.smu_master=smu_master
        self.sweep_param=sweep_param
        self.smu_compliance=smu_compliance
        self.smu_bias=smu_bias
        self.integration_mode=integration_mode
        self.delay_time=delay_time
        self.hold_time=hold_time
        
        index_measurement_type={"sweep":1, "constant":3}
        index_smu_type={"voltage":1, "current":2, "common":3}
        integration_dictionnary={"S":"IT1","M":"IT2","L":"IT3"}

        try:
            self.pyvisa_resource.write("BC") # clear all buffer.
            self.pyvisa_resource.write("DR1") # This command enables or disables service request for data ready when communications is set to GPIB.
            self.pyvisa_resource.write("EC 1") # This command sets the condition to exit the test if compliance is reached.
            
                
            self.pyvisa_resource.write("DE") # DE: Accesses SMU channel definition page.
            
            self.pyvisa_resource.write("CH%d, 'V%d', 'I%d', %d, %d"%(smu_master,smu_master,smu_master,index_smu_type[smu_type["SMU%d"%smu_master]],index_measurement_type["sweep"])) # 1/2/3: voltage/current/Common 1/2/3: VAR1/VAR2/constant
            
            for smu_index in range(4):
                if (smu_index+1!=smu_master) and smu_used["SMU%d"%(smu_index+1)]=="off":
                    self.pyvisa_resource.write("CH%d"%(smu_index+1)) 
                elif (smu_index+1!=smu_master) and smu_used["SMU%d"%(smu_index+1)]=="on":
                    self.pyvisa_resource.write("CH%d, 'V%d', 'I%d', %d, %d"%(smu_index+1,smu_index+1,smu_index+1,index_smu_type[smu_type["SMU%d"%(smu_index+1)]],index_measurement_type["constant"])) 

            self.pyvisa_resource.write("SS")# Accesses source setup page
            if smu_type["SMU%d"%smu_master]=="voltage":
                if sweep_type=="linear":
                    self.pyvisa_resource.write("VR1, %.6E, %.6E, %.6E, %.6E"%(sweep_param["start"],sweep_param["stop"],sweep_param["step"],smu_compliance["SMU%d"%smu_master])) # VR1 for linear sweep of VAR1 source function, vmin, vmax,vstep, compliance
                elif sweep_type=="log":
                    self.pyvisa_resource.write("VR2, %.6E, %.6E, %.6E"%(sweep_param["start"],sweep_param["stop"],smu_compliance["SMU%d"%smu_master])) # VR2 for log sweep of VAR1 source function, vmin, vmax, compliance
            elif smu_type["SMU%d"%smu_master]=="current":
                if sweep_type=="linear":
                    self.pyvisa_resource.write("IR1, %.6E, %.6E, %.6E, %.6E"%(sweep_param["start"],sweep_param["stop"],sweep_param["step"],smu_compliance["SMU%d"%smu_master])) # IR1 for linear sweep of VAR1 source function, vmin, vmax,vstep, compliance
                elif sweep_type=="log":
                    self.pyvisa_resource.write("IR2, %.6E, %.6E, %.6E"%(sweep_param["start"],sweep_param["stop"],smu_compliance["SMU%d"%smu_master])) # IR2 for log sweep of VAR1 source function, vmin, vmax, compliance
            
            for smu_index in range(4):
                if (smu_index+1!=smu_master) and smu_used["SMU%d"%(smu_index+1)]=="on":
                    if smu_type["SMU%d"%(smu_index+1)]=="voltage":
                        self.pyvisa_resource.write("VC%d, %.6E, %.6E"%(smu_index+1,smu_bias["SMU%d"%(smu_index+1)],smu_compliance["SMU%d"%(smu_index+1)]))
                    elif smu_type["SMU%d"%(smu_index+1)]=="current":
                        self.pyvisa_resource.write("IC%d, %.6E, %.6E"%(smu_index+1,smu_bias["SMU%d"%(smu_index+1)],smu_compliance["SMU%d"%(smu_index+1)]))

            self.pyvisa_resource.write("HT %.6E"%hold_time) # Sets a hold time that delays the start of a sweep
            self.pyvisa_resource.write("DT %.6E"%delay_time) # delay time: Sets the time to wait between when the output voltage is set and when the measurement is made in a sweep.
            self.pyvisa_resource.write(integration_dictionnary[integration_mode]) # integration time, IT1/IT2/IT3 : short/medium/long

            self.pyvisa_resource.write("SM")
            self.pyvisa_resource.write("DM2")
            list_display=""
            for smu_index in range(4):
                if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                    if self.smu_type["SMU%d"%(smu_index+1)]=="voltage":
                        list_display+=",'%s%d'"%("I",smu_index+1)
                    elif self.smu_type["SMU%d"%(smu_index+1)]=="current":
                        list_display+=",'%s%d'"%("V",smu_index+1)
                        
            self.pyvisa_resource.write("LI %s"%list_display[1:])
        except pyvisa.VisaIOError:
            print("/!\ VisaIOError : timeout expired")
            self.pyvisa_resource.close()
        
    
    def launch_measurements(self):
        """ Function that launch the measurement and return the data (in array shape) and the header (string) depending on the measurement configuration
        
            return:
               \n\t- data (array) : array with the measurement data
               \n\t- header (string) : string with the description of the data column "Vx" or "Ix" for voltage or current measured from SMUx.
        """            
        number_channel=0
        for smu_index in range(4):
            if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                number_channel+=1
        sweep_list=np.round(np.arange(self.sweep_param["start"],self.sweep_param["stop"]+self.sweep_param["step"],self.sweep_param["step"]),6)
        N_sweep=len(sweep_list)
        data=np.zeros((N_sweep,number_channel+1))
        data[:,0]=sweep_list

        
        self.pyvisa_resource.write("MD") # This command controls measurements.
        self.pyvisa_resource.write("ME1") # Run a single trigger test and store readings in a cleared buffer: 1
        while self.pyvisa_resource.read_stb()!=0:
            print(self.pyvisa_resource.read_stb())
            time.sleep(1)
        i=0
        for smu_index in range(4):
            if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                i+=1
                if self.smu_type["SMU%d"%(smu_index+1)]=="voltage":
                    data_list=self.pyvisa_resource.query("DO 'I%d'"%(smu_index+1))# Read measurements

                elif self.smu_type["SMU%d"%(smu_index+1)]=="current":
                    data_list=self.pyvisa_resource.query("DO 'V%d'"%(smu_index+1),delay=1)# Read measurements
                
                j=0
                for  data_j in data_list.split(","):
                    data[j,i]=float(data_j[1:])
                    j+=1            
# =============================================================================
#         j=0               
#         while (j<N_sweep):
#             if self.smu_type["SMU%d"%(self.smu_master)]=="voltage":
#                 data_master=np.float32(self.pyvisa_resource.query("RD 'I%d', %d"%(self.smu_master,j+1)))
#             elif self.smu_type["SMU%d"%(self.smu_master)]=="current":
#                 data_master=np.float32(self.pyvisa_resource.query("RD 'V%d', %d"%(self.smu_master,j+1)))
#             if (data_master!=0.):
#                 i=0
#                 for smu_index in range(4):
#                     if self.smu_used["SMU%d"%(smu_index+1)]=="on":
#                         i+=1
#                         if self.smu_type["SMU%d"%(smu_index+1)]=="voltage":
#                             data[j,i]=np.float32(self.pyvisa_resource.query("RD 'I%d', %d"%(smu_index+1,j+1)))# Read measurements
#                         elif self.smu_type["SMU%d"%(smu_index+1)]=="current":
#                             data[j,i]=np.float32(self.pyvisa_resource.query("RD 'V%d', %d"%(smu_index+1,j+1)))# Read measurements
#                             
#                 j+=1
# =============================================================================
        header="%s%d"%(self.smu_type["SMU%d"%self.smu_master][0].upper(),self.smu_master)
        for smu_index in range(4):
            if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                if self.smu_type["SMU%d"%(smu_index+1)]=="voltage":
                    header+=", %s%d"%("I",smu_index+1)
                elif self.smu_type["SMU%d"%(smu_index+1)]=="current":
                    header+=", %s%d"%("V",smu_index+1)
        return data, header
    
    def launch_measurements_without_reading(self):
        
        """ Function to launch the measurement without reading the data
        """        

        self.pyvisa_resource.write("MD") # This command controls measurements.
        self.pyvisa_resource.write("ME1") # Run a single trigger test and store readings in a cleared buffer: 1
        
    def read_measurements(self):
        """ Function to return the data (in array shape) and the header (string) after the measurements
        
            return:
               \n\t- data (array) : array with the measurement data
               \n\t- header (string) : string with the description of the data column "Vx" or "Ix" for voltage or current measured from SMUx.
        """
        
        number_channel=0
        for smu_index in range(4):
            if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                number_channel+=1
        sweep_list=np.round(np.arange(self.sweep_param["start"],self.sweep_param["stop"]+self.sweep_param["step"],self.sweep_param["step"]),6)
        N_sweep=len(sweep_list)
        data=np.zeros((N_sweep,number_channel+1))
        data[:,0]=sweep_list
        
        i=0
        for smu_index in range(4):
            if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                i+=1
                if self.smu_type["SMU%d"%(smu_index+1)]=="voltage":
                    data_list=self.pyvisa_resource.query("DO 'I%d'"%(smu_index+1))# Read measurements

                elif self.smu_type["SMU%d"%(smu_index+1)]=="current":
                    data_list=self.pyvisa_resource.query("DO 'V%d'"%(smu_index+1),delay=1)# Read measurements
                
                j=0
                for  data_j in data_list.split(","):
                    data[j,i]=float(data_j[1:])
                    j+=1   
                    
        header="%s%d"%(self.smu_type["SMU%d"%self.smu_master][0].upper(),self.smu_master)
        for smu_index in range(4):
            if self.smu_used["SMU%d"%(smu_index+1)]=="on":
                if self.smu_type["SMU%d"%(smu_index+1)]=="voltage":
                    header+=", %s%d"%("I",smu_index+1)
                elif self.smu_type["SMU%d"%(smu_index+1)]=="current":
                    header+=", %s%d"%("V",smu_index+1)
        return data, header
    
