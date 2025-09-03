import dopes.equipment_control.equipment as equipment
import time
import numpy as np

class sh242(equipment.equipment):
    
    """Class to control SH242 climatic chamber"""
    model="SH242"
    company="ESPEC"
    url="https://espec.com/na/products/model/sh_242"       


    def initialize(self,temperature=True, humidity=False,temperature_dic={"upper":125,"lower":-45,"set":20},humidity_dic={"upper":100,"lower":0,"set":55}):
        """ Function to initialize the SH242
        
            args:
               \n\t- temperature (boolean) : if True, activate the temperature control
               \n\t- humidity (boolean) : if True, activate the humidity control
               \n\t- temperature_dic (dictionary) : dictionnary with the upper ("upper") and lower ("lower") alarm and the initial set point ("set") for the temperature
               \n\t- humidity_dic (dictionary) : dictionnary with the upper ("upper") and lower ("lower") alarm and the initial set point ("set") for the humidity
        """

        self.set_connection_parameter_dic({"write_termination":'\r\n',"read_termination":'\r\n',"send_end":True})

        self.pyvisa_resource.write('POWER, ON')
        time.sleep(1)
        self.pyvisa_resource.read()
        self.pyvisa_resource.write('POWER, CONSTANT')
        time.sleep(10)
        self.pyvisa_resource.read()

        if temperature:
            self.pyvisa_resource.write("TEMP, L%.2f"%temperature_dic["upper"])  #Changes the temperature lower absolute alarm value in constant setup
            time.sleep(1)
            self.pyvisa_resource.read()
            self.pyvisa_resource.write("TEMP, H%.2f"%temperature_dic["lower"]) #Changes the temperature upper absolute alarm value in constant setup
            time.sleep(1)
            self.pyvisa_resource.read()
            self.pyvisa_resource.write("TEMP, S%.2f"%temperature_dic["set"]) #Changes the temperature set point in constant setup
            time.sleep(1)
            self.pyvisa_resource.read()
        else:
            self.pyvisa_resource.write("TEMP, SOFF") # disable temperature
            time.sleep(1)
            self.pyvisa_resource.read()
            

        if humidity:
            self.pyvisa_resource.write("HUMI, L%.2f"%humidity_dic["upper"])  #Changes the temperature lower absolute alarm value in constant setup
            time.sleep(1)
            self.pyvisa_resource.read()
            self.pyvisa_resource.write("HUMI, H%.2f"%humidity_dic["lower"]) #Changes the temperature upper absolute alarm value in constant setup
            time.sleep(1)
            self.pyvisa_resource.read()
            self.pyvisa_resource.write("HUMI, S%.2f"%humidity_dic["set"]) #Changes the temperature set point in constant setup
            time.sleep(1)
            self.pyvisa_resource.read()
        else:
            self.pyvisa_resource.write("HUMI, SOFF") # disable temperature
            time.sleep(1)
            self.pyvisa_resource.read()
            
    def read_temperature(self):
        """ Function to read the temperature of the climatic chamber
        
            return:
               \n\t- temperature (scalar) : temperature of the chamber
        """

        self.pyvisa_resource.write('TEMP?')
        time.sleep(0.5)
        temperature=self.pyvisa_resource.read()
        return temperature
    
    def read_humidity(self):
        """ Function to read the humidity of the climatic chamber
        
            return:
               \n\t- humidity (scalar) : humidity of the chamber
        """
        self.pyvisa_resource.write('HUMI?')
        time.sleep(0.5)
        humidity=self.pyvisa_resource.read()
        return humidity
    
    
    def set_temperature(self,temperature,waiting_time=0,wait_for_stabilization=False,stabilization_tolerance=0.1,stabilization_number=10):
        """ Function to set the temperature of the climatic chamber
        
            return:
               \n\t- temperature (scalar) : targeted temperature of the chamber
               \n\t- waiting_time (scalar) : time in seconds to wait before after changing the temperature target. If a waiting for the stabilization is required, the waiting time happens before.
               \n\t- wait_for_stabilization (boolean) : if True, the function wait that the chamber has stabilized within "stabilization_tolerance" over "stabilization_number" cycles of 5 seconds
               \n\t- stabilization_tolerance (scalar) : the tolerance in °C to consider the temperature of the chamber close enough to the targeted temperature
               \n\t- stabilization_number (int) : number of cycles to be checked to consider the temperature as stabilized
        """
        self.pyvisa_resource.write("TEMP, S%.2f"%temperature) #Changes the temperature set point in constant setup
        time.sleep(1)
        self.pyvisa_resource.read()
        time.sleep(waiting_time)
        
        if wait_for_stabilization:
            temperature_stabilized=False
            stabilization_count=0
            
            while temperature_stabilized==False:
                self.pyvisa_resource.write("TEMP?") 
                time.sleep(5)
                temperature_read=np.round(float(self.pyvisa_resource.read().split(",")[0]),1)
                if abs(temperature_read-temperature)<stabilization_tolerance:
                    stabilization_count+=1
                    if stabilization_count==stabilization_number:
                        temperature_stabilized=True
                else:
                    stabilization_count=0
        

    def set_humidity(self,humidity,waiting_time=0,wait_for_stabilization=False,stabilization_tolerance=0.5,stabilization_number=1):
        """ Function to set the humidity of the climatic chamber
        
            return:
               \n\t- humidity (scalar) : targeted humidity of the chamber
               \n\t- waiting_time (scalar) : time in seconds to wait before after changing the humidity target. If a waiting for the stabilization is required, the waiting time happens before.
               \n\t- wait_for_stabilization (boolean) : if True, the function wait that the chamber has stabilized within "stabilization_tolerance" over "stabilization_number" cycles of 5 seconds
               \n\t- stabilization_tolerance (scalar) : the tolerance in % to consider the humidity of the chamber close enough to the targeted humidity
               \n\t- stabilization_number (int) : number of cycles to be checked to consider the humidity as stabilized
        """
        self.pyvisa_resource.write("HUMI, S%.2f"%humidity) #Changes the temperature set point in constant setup
        time.sleep(1)
        self.pyvisa_resource.read()
        time.sleep(waiting_time)
        
        if wait_for_stabilization:
            humidity_stabilized=False
            stabilization_count=0
            
            while humidity_stabilized==False:
                self.pyvisa_resource.write("HUMI?") 
                time.sleep(5)
                humidity_read=np.round(float(self.pyvisa_resource.read().split(",")[0]),1)
                if abs(humidity_read-humidity)<stabilization_tolerance:
                    stabilization_count+=1
                    if stabilization_count==stabilization_number:
                        humidity_stabilized=True
                else:
                    stabilization_count=0
