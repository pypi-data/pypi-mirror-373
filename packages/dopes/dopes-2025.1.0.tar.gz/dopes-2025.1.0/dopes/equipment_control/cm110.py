import dopes.equipment_control.equipment as equipment
import time
import serial

class cm110(equipment.equipment):
    
    """Class to control CM110 monochromator"""
    model="CM110"
    company="Spectral Product"
    url="https://www.spectralproducts.com/CM110"

    def __init__(self,port):
        """ Function called when an instance of the class is created
        
            args:
                \n\t- port (string) : the computer port to which the equipment is connected        
        """
        self.serial_resource = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )


    def initialize(self,grating_number=1,waiting_time=30):
        """ Function to initialize the CM110
        
            args:
                \n\t- grating_number (int) : select the grating (Grating 1 : AG2400-00240-303 (2400 G/mm and 180 nm - 680 nm) and Grating 2 : AG1200-00750-303 (1200 G/mm and 480 nm - 1500 nm))
                \n\t- waiting_time (int) : waiting time in seconds after changing the grating and reset to the initial position
                
        """
        reset=[255,255,255] 
        
        self.serial_resource.write(serial.to_bytes([26,grating_number]))
        time.sleep(waiting_time)
        self.serial_resource.write(serial.to_bytes(reset))
        time.sleep(waiting_time)
        
    def set_wavelength(self, wavelength,waiting_time=5):
        """ Function to set the wavelength of the monochromator
        
            args:
               \n\t- wavelength (scalar) : targeted wavelength in nm
               \n\t- waiting_time : waiting time in seconds to let the grating of the monochromator reach the targeted wavelength
        """
        set_position = [16,int((wavelength-wavelength%256)/256),int(wavelength)%256] # Goto Position : 1000 -> 0x3E8 -> 3 and 232 
        self.serial_resource.write(serial.to_bytes(set_position))
        time.sleep(waiting_time)
        
    def select_grating(self, grating_number,waiting_time=30):
        """ Function to select the gratin
               \n\t- grating_number (int) : select the grating (Grating 1 : AG2400-00240-303 (2400 G/mm and 180 nm - 680 nm) and Grating 2 : AG1200-00750-303 (1200 G/mm and 480 nm - 1500 nm))
               \n\t- waiting_time (int) : waiting time in seconds after changing the grating and reset to the initial position 
        """
        self.serial_resource.write(serial.to_bytes([26,grating_number]))
        time.sleep(waiting_time)

    def close_connection(self):
        """ Function to close the  serial connection with the equipment """
        self.serial_resource.close()



                   
                  