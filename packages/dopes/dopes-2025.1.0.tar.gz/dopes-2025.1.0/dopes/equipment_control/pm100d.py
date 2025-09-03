import dopes.equipment_control.equipment as equipment
import time
class pm100d(equipment.equipment):
    
    """Class to control PM100D powermeter controller"""
    model="PM100D"
    company="Thorlabs"
    url="https://www.thorlabs.com/thorproduct.cfm?partnumber=PM100D"

    def initialize(self,zero_calibration=True):
        """ Function to initialize the PM100D powermeter controller """

        self.set_connection_parameter_dic({"write_termination":'\n',"read_termination":'\n',"send_end":True})
        self.pyvisa_resource.write("*CLS")
        self.pyvisa_resource.write("*RST")
        self.pyvisa_resource.write("CONFigure:power")
        self.pyvisa_resource.write("power:range:auto on")

        if zero_calibration:
            input("Turn off the light for the zero calibration. (Press enter to continue)")
            self.pyvisa_resource.write("CORRection:collect:zero")
            input("Zero calibrated! (Press enter to continue)")

        
    def read_power(self,wavelength,average_number=10):
        """ Function to read the power from the powermeter 
        
            args:
               \n\t - wavelength (integer): the wavelength parameter in nanometers to calculate the power from the photocurrent
               \n\t - average_number (integer): the number of acquisition to do an averaging 
               
            return:
                \n\t - a scalar with the power in Watts read by the powermeter
                """
               

        self.pyvisa_resource.query("*OPC?")
        self.pyvisa_resource.write("CORRection:WAVelength %d"%wavelength)
        self.pyvisa_resource.write("AVERAGE:COUNT %d"%average_number)
        data=float(self.pyvisa_resource.query("Read?"))
        
        return data
