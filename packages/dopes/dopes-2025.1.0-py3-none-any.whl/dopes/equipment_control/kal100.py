import dopes.equipment_control.equipment as equipment
import time
import serial

class kal100(equipment.equipment):
    
    """Class to control KAL100 pressure system"""
    model="KAL100"
    company="halstrup-walcher"
    url="https://www.halstrup-walcher.de/en/products/KAL100.php"

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
            bytesize=serial.EIGHTBITS,
            timeout=10
        )

    def initialize(self,units="kPa",percentage=100, mode_operation="MS", mode_input="positive",zero_adjust=True):    
        """ Function to initialize the KAL100
        
            args:
               \n\t- units (string) : "Pa", "kPa" or "hPa"
               \n\t- percentage (int) : pressure fixed at "percentage" of the targeted value
               \n\t- mode_operation (string) :  mode test ("MT"), mode zeroing ("MZ"), mode target value ("MS"), mode pressure measurement ("MP")
               \n\t- mode_input (string) : Positive P-input ("positive"), Negative P-input ("negative"), Differential pressure measurement  ("differential")
                
        """
        units_dic={"kPa":0,"Pa":1,"hPa":2}
        mode_dic={"positive":"MI0","negative":"MI1","differential":"MI2"}

        input("Unplug the pressure line before initialization to avoid pressure burst on your sample.\n(Press any key to continue)")
        self.units=units
        # self.serial_resource.write(str.encode(">PD%d\n"%units_dic[units]))
        # self.serial_resource.read_until(b'\r')
        self.serial_resource.write(str.encode(">PE%d\n"%units_dic[units]))
        self.serial_resource.read_until(b'\r')
        self.serial_resource.write(str.encode(">PP%d\n"%percentage)) # percentage of the target 
        self.serial_resource.read_until(b'\r')

        self.serial_resource.write(str.encode("%s\n"%mode_dic[mode_input])) # MI0: Positive P-input, MI1: Negative P-input, MI2: Differential pressure measurement 
        self.serial_resource.read_until(b'\r')

        if zero_adjust:
            self.serial_resource.write(str.encode("MZ\n")) # mode zeroing
            self.serial_resource.read_until(b'\r')
            time.sleep(10)
        self.serial_resource.write(str.encode("%s\n"%mode_operation)) #MT: mode test, MZ: mode zeroing, MS: mode target value, MP: mode pressure measurement 
        self.serial_resource.read_until(b'\r')
        
        if mode_operation=="MS":
            self.serial_resource.write(str.encode(">PS%3.5f\n"%0))
            self.serial_resource.read_until(b'\r')
            
    def set_pressure(self,pressure):
        """ Function to set pressure level of the KAL100
        
            args:
               \n\t- pressure (scalar) : targeted pressure
        """
        units_mult={"kPa":10,"Pa":1e-3,"hPa":1}

        self.serial_resource.write(str.encode("MS\n"))
        self.serial_resource.read_until(b'\r')
        self.serial_resource.write(str.encode(">PS%3.5f\n"%(pressure*units_mult[self.units])))
        # self.serial_resource.write(str.encode(">PS%3.5f\n"%(pressure)))
        self.serial_resource.read_until(b'\r')
            
    def close_connection(self):
        """ Function to close the  serial connection with the equipment """
        self.serial_resource.close()

