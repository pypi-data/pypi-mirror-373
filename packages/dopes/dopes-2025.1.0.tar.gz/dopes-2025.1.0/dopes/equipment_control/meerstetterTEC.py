"""

"""
import logging
import platform
from time import time, sleep
from dopes.equipment_control.mecom import MeComSerial, ResponseException, WrongChecksum
from serial import SerialException
from serial.serialutil import PortNotOpenError
import numpy as np

# default queries from command table below
DEFAULT_QUERIES = [
    "loop status",
    "object temperature",
    "target object temperature",
    "output current",
    "output voltage"
]

# syntax
# { display_name: [parameter_id, unit], }
COMMAND_TABLE = {
    "loop status": [1200, ""],
    "object temperature": [1000, "degC"],
    "target object temperature": [3000, "degC"],
    "output current": [1020, "A"],
    "output voltage": [1021, "V"],
    "sink temperature": [1001, "degC"],
    "ramp temperature": [1011, "degC"],
}

MAX_COM = 256

class meerstetterTEC(object):
    """
    Controlling TEC devices via serial.
    """

    def close_connection(self):
        self.session().stop()

    def __init__(self, port=None, scan_timeout=30, channel=1, queries=DEFAULT_QUERIES, *args, **kwars):
        assert channel in (1, 2)
        self.channel = channel
        self.port = port
        self.scan_timeout = scan_timeout
        self.queries = queries
        self._session = None
        self._connect()

    def _connect(self):
        # open session
        if self.port is not None:
            self._session = MeComSerial(serialport=self.port)
        else:
            if platform.system() != "Windows":
                start_index = 0
                base_name = "/dev/ttyUSB"
            else:
                start_index = 1
                base_name = "COM"

            scan_start_time = time()
            while True:
                for i in range(start_index, MAX_COM + 1):
                    try:
                        self._session = MeComSerial(serialport=base_name + str(i))
                        break
                    except SerialException:
                        pass
                if self._session is not None or (time() - scan_start_time) >= self.scan_timeout:
                    break
                sleep(0.1) # 100 ms wait time between each scan attempt

            if self._session is None:
                 raise PortNotOpenError
        # get device address
        self.address = self._session.identify()
        logging.info("connected to {}".format(self.address))

    def initialize(self):
        # start logging
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(module)s:%(levelname)s:%(message)s")

        # initialize controller
        # mc = MeerstetterTEC()

        # get the values from DEFAULT_QUERIES
        print(self.get_data())

    def session(self):
        if self._session is None:
            self._connect()
        return self._session

    def get_data(self):
        data = {}
        for description in self.queries:
            id, unit = COMMAND_TABLE[description]
            try:
                value = self.session().get_parameter(parameter_id=id, address=self.address, parameter_instance=self.channel)
                data.update({description: (value, unit)})
            except (ResponseException, WrongChecksum) as ex:
                self.session().stop()
                self._session = None
        return data

    def set_temp(self, value,wait_for_stabilization=False,waiting_time=0.1,stabilization_tolerance=0.1,stabilization_number=10):
        """
        Set object temperature of channel to desired value.
        :param value: float
        :param channel: int
        :return:
        """
        # assertion to explicitly enter floats
        assert type(value) is float
        logging.info("set object temperature for channel {} to {} C".format(self.channel, value))
        message=self.session().set_parameter(parameter_id=3000, value=value, address=self.address, parameter_instance=self.channel)
        if wait_for_stabilization:
            temperature_stabilized=False
            stabilization_count=0
            
            while temperature_stabilized==False:
                sleep(waiting_time)
                temperatue_data=self.get_data()
                temperature_read=np.round(float(temperatue_data["object temperature"][0]),3)
                if abs(temperature_read-value)<stabilization_tolerance:
                    stabilization_count+=1

                    if stabilization_count==stabilization_number:
                        temperature_stabilized=True

                else:
                    stabilization_count=0

        return message
    def _set_enable(self, enable=True):
        """
        Enable or disable control loop
        :param enable: bool
        :param channel: int
        :return:
        """
        value, description = (1, "on") if enable else (0, "off")
        logging.info("set loop for channel {} to {}".format(self.channel, description))
        return self.session().set_parameter(value=value, parameter_name="Status", address=self.address, parameter_instance=self.channel)

    def enable(self):
        return self._set_enable(True)

    def disable(self):
        return self._set_enable(False)
