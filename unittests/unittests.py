#!/usr/bin/env python
import os
import sys
import unittest
import pep8


sys.path.insert(0, os.path.dirname(__file__) + '/..')
import check_iftraffic_nrpe as myscript

"""
class FooTest(unittest.TestCase):
class DeviceError(Exception):
class InterfaceDetection(object):
class DataFile():
class ProcNetDev():


"""

import struct
ARCH = struct.calcsize("P") * 8

class Max_Counter(unittest.TestCase):

    def setUp(self):
        # unsigned long integer
        if (ARCH == 32):
            self.expected_result = 2**32-1
        elif (ARCH == 64):
            self.expected_result = 2**64-1
        else:
            raise SystemError ("Unknown architecture %s" % arch)

    def test(self):
        self.assertEqual(myscript.max_counter(), self.expected_result)

class Calc_Diff(unittest.TestCase):
    """
    calc_diff(value1, uptime1, value2, uptime2)
    Calculate the difference between two values.
    The function takes care of the maximum allowed value by the system
    """
    def test_normal(self):
        value1, uptime1, value2, uptime2 = 1, 1, 2, 2
        self.assertEqual(myscript.calc_diff(value1, uptime1, value2, uptime2), 1)
    def test_reset(self):
        # the value got up the counter and dropped. must calc the diff.
        uptime1, uptime2 =9, 10
        # find the last value of the system before reset
        if ARCH == 32:
            value1 = 2**32 - 1
        if ARCH == 64:
            value1 = 2**64 - 1
        value2 = 0
        self.assertEqual(myscript.calc_diff(value1, uptime1, value2, uptime2), 1)
    def test_reboot(self):
        # the host rebooted, uptime2 is smaller than uptime1: must take latest value possible
        value1, uptime1, value2, uptime2 = 123, 10, 345, 5
        self.assertEqual(myscript.calc_diff(value1, uptime1, value2, uptime2), 345)


class Uptime(unittest.TestCase):
    def setUp(self):
        self.expected_result = float(open('/proc/uptime','r').readline().split()[0])
    def test(self):
        self.assertEqual(myscript.uptime(), self.expected_result)


class Worst_Status(unittest.TestCase):
    def test(self):
        status_order = ['CRITICAL', 'WARNING', 'UNKNOWN', 'OK']
        self.assertEqual(myscript.worst_status('CRITICAL','CRITICAL'), 'CRITICAL')
        self.assertEqual(myscript.worst_status('CRITICAL', 'WARNING'), 'CRITICAL')
        self.assertEqual(myscript.worst_status('CRITICAL', 'UNKNOWN'), 'CRITICAL')
        self.assertEqual(myscript.worst_status('CRITICAL', 'OK'), 'CRITICAL')
        self.assertEqual(myscript.worst_status('WARNING', 'CRITICAL'), 'CRITICAL')
        self.assertEqual(myscript.worst_status('WARNING','WARNING'), 'WARNING')
        self.assertEqual(myscript.worst_status('WARNING','UNKNOWN'), 'WARNING')
        self.assertEqual(myscript.worst_status('WARNING','OK'), 'WARNING')
        self.assertEqual(myscript.worst_status('OK', 'CRITICAL'), 'CRITICAL')
        self.assertEqual(myscript.worst_status('OK', 'WARNING'), 'WARNING')
        self.assertEqual(myscript.worst_status('OK', 'UNKNOWN'), 'UNKNOWN')
        self.assertEqual(myscript.worst_status('OK','OK'), 'OK')


class Nagios_Value_Status(unittest.TestCase):
    """ def nagios_value_status(value, max_value, percent_crit, percent_warn):
        Returns the string defining the Nagios status of the value
    """
    def exec_test(self, value, result):
        self.assertEqual(myscript.nagios_value_status(value,100,90, 80), result)

    def test(self):
        self.exec_test(0, 'OK')
        self.exec_test(50, 'OK')
        self.exec_test(80, 'WARNING')
        self.exec_test(81, 'WARNING')
        self.exec_test(90, 'CRITICAL')
        self.exec_test(91, 'CRITICAL')

class Bits2Bytes(unittest.TestCase):
    def test(self):
        self.assertEqual(myscript.bits2bytes(0), 0)
        self.assertEqual(myscript.bits2bytes(7), 0)
        self.assertEqual(myscript.bits2bytes(8), 1)
        self.assertEqual(myscript.bits2bytes(17), 2)
        self.assertEqual(myscript.bits2bytes(-1), -1)

class Specify_Devices(unittest.TestCase):
    def setUp(self):
        self.devices = myscript.ProcNetDev().parse(myscript.ProcNetDev().read())
    def test_specify_1_device(self):
        for key in self.devices.keys():
            devices = self.devices.copy()
            my_devices = [key]
            #print "Specifying %s: " % my_devices
            myscript.specify_device(my_devices, devices)
            for my_device in my_devices:
                self.assertIn(my_device, devices)

    def test_specify_all_devices(self):
        my_devices = []
        for key in self.devices.keys():
            my_devices.append(key)
        devices = self.devices.copy()
        myscript.specify_device(my_devices, devices)
        for device in self.devices:
            self.assertIn(device, devices)




if __name__ == "__main__":
    unittest.main()
