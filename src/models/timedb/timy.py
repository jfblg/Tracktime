import datetime
import logging
import time

import usb
# import usb.util

from src.common.database import db
from src.models.timedb.timedb import TimeDbModel

# TODO How to interupt while loop when running?

class Timy(object):
    """Class responsible for communication with the ALGE TIMY 3
    """
    TIMY_VEND = 0x0c4a  # USB Vendor ID
    TIMY_PROD = 0x0889  # USB Product ID
    READEP = 0x81  # Interrupt input endpoint ID
    WRITEEP = 0x01  # Interrupt output endpoint ID
    CMDS_ALL = ['TIMYINIT', 'NSF', 'KL0', 'CHK1', 'PRE4',
            'RR0', 'BE1', 'DTS00.02', 'DTF00.02', 'EMU0',
            'PRIIGN1', 'PRILF', 'DTP------------',
            'PS1', 'PROG', 'CLR',
            ]
    CMDS= ['TIMYINIT', 'EMU0', 'CLR']

    def __init__(self, timeout=720000, logging=True, logfile="timylog.txt"):
        self.logging = logging
        self.logfile = logfile
        self.timeout = timeout
        self.device_handle = None
        self.kill = False

        if self.logging:
            Timy.logging_init(self.logfile)

        self.find_device()

    def find_device(self):
        """Verifies if ALGE TIMY3 USB device is connected."""

        self.device_handle = usb.core.find(
            idVendor=Timy.TIMY_VEND,
            idProduct=Timy.TIMY_PROD)

        if self.device_handle is None:
            logging.error("ALGE TIMY3 not found. Time capture not possible.")
            return False

        self.device_handle.set_configuration()

    def capture_start(self):
        """Starts neverending loop, listens what is received and save received times to the database."""

        if self.device_handle is None:
            logging.error("ALGE TIMY3 not found. Time capture not possible.")
            return False

        self.kill = False
        self.device_handle.write(Timy.WRITEEP, '\r')
        try:
            while True:
                if self.kill:
                    print("stopping the loop")
                    break
                try:
                    if len(Timy.CMDS) > 0:
                        cmd = Timy.CMDS.pop(0)
                        self.device_handle.write(Timy.WRITEEP, cmd + '\r')
                        print(bytearray(self.device_handle.read(Timy.READEP, 32, timeout=self.timeout)))

                    received = bytearray(self.device_handle.read(
                                        Timy.READEP,
                                        32,
                                        timeout=self.timeout))\
                        .decode("UTF-8")

                    print(received)
                    time_received = received.split()

                    if len(time_received) == 4:
                        if time_received[1] == "c1M":
                            print(time_received)
                            logging.debug("Received values: %s - %s - %s - %s", *time_received)
                            if self._save_to_db(time_received[2], time_received[3]):
                                logging.debug("Time saved to the database")
                            else:
                                logging.error("Problem with saving to the database")
                    else:
                        print(time_received)
                    time.sleep(0.1)

                except usb.core.USBError as e:
                    if e.args[0] == 60:
                        # To capture usb.core.USBError timeout exception raised after TIMEOUT expires with the code 60
                        # usb.core.USBError: [Errno 60] Operation timed out
                        print("Timeout exception occured.")
                        logging.warning(
                            "Configured timeout %s msec has expired. Recommendation: Increase its value.",
                            self.timeout)
                        pass

                    if e.args[0] == 19:
                        # Device has been disconnected
                        # usb.core.USBError: [Errno 19] No such device (it may have been disconnected)
                        print("Timeout exception occured.")
                        logging.error(
                            "ALGE TIMY USB device has been disconnected",
                            self.timeout)
                        break
                    else:
                        raise e
        finally:
            print("device reset - ending the loop")
            self.device_handle.reset()

    def capture_stop(self):
        """By calling this method, the neverending loop should be terminated"""
        # TODO it does not work yet. Figure out how to stop the loop.

        if self.device_handle is None:
            logging.error("ALGE TIMY3 not found. Time capture not possible.")
            return False

        self.kill = True

    def _save_to_db(self, timy_time_format, order_number):
        """Save the time to the database."""
        try:
            deltatime = Timy.convert_time_to_delta(timy_time_format)
            record = TimeDbModel(deltatime, order_number)
            record.save_to_db()
        except:
            return False
        return True

    @staticmethod
    def logging_init(logfile):
        """Initialize logging for debuggin purposes."""

        logging.basicConfig(filename=logfile,
                            format='%(asctime)s %(levelname)s %(message)s',
                            level=logging.DEBUG)


    @staticmethod
    def convert_time_to_delta(input_value):
        """Function coverts string into to the time.timedelta object for database storage.

        :param input_value: (str) example: 00:00:10.82
        :return: deltatime
        """
        epoch = datetime.datetime.utcfromtimestamp(0)

        time_entered = input_value.strip()
        datetime_composite = "1 Jan 1970 {}".format(time_entered)
        time_converted = datetime.datetime.strptime(datetime_composite, '%d %b %Y %H:%M:%S.%f')
        delta_time = time_converted - epoch
        return delta_time


def main():
    timy = Timy()
    timy.capture_start()
    timy.capture_stop()


if __name__ == "__main__":
    main()