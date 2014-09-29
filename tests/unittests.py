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
        f = open('/proc/uptime','r')
        self.expected_result = float(f.readline().split()[0])
        f.close()
    def test(self):
        self.assertEqual(myscript.uptime(), self.expected_result)


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

class Convert_Bytes(unittest.TestCase):
    def setUp(self):
       self.multiple = 1000
       self.sample_values = [ 0, 1, 10, 100, 1000, 3214]

    def test_convert_bytes(self):
        # Test Bytes
        for value in self.sample_values:
            result = value
            self.assertEqual(myscript.convert_bytes(value, 'Bps'), result)
            result = value / self.multiple
            self.assertEqual(myscript.convert_bytes(value, 'kBps'), result)
            result = value / ( pow(self.multiple, 2) )
            self.assertEqual(myscript.convert_bytes(value, 'MBps'), result)
            result = value / ( pow(self.multiple, 3) )
            self.assertEqual(myscript.convert_bytes(value, 'GBps'), result)
            result = value / ( pow(self.multiple, 4) )
            self.assertEqual(myscript.convert_bytes(value, 'TBps'), result)
            # Test bits
    def test_convert_bytes_to_bits(self):
        # Test Bytes
        for value in self.sample_values:
            self.assertEqual(myscript.convert_bytes(0, 'bps'), 0)
            self.assertEqual(myscript.convert_bytes(0, 'kbps'), 0)
            self.assertEqual(myscript.convert_bytes(0, 'Tbps'), 0)
            self.assertEqual(myscript.convert_bytes(1, 'bps'), 8)
            self.assertEqual(myscript.convert_bytes(1000, 'kbps'), 8)
            result = 8 * value
            self.assertEqual(myscript.convert_bytes(value, 'bps'), result)
            result = 8 * value / self.multiple
            self.assertEqual(myscript.convert_bytes(value, 'kbps'), result)
            result = 8 * value / ( pow(self.multiple, 2) )
            self.assertEqual(myscript.convert_bytes(value, 'Mbps'), result)
            result = 8 * value / ( pow(self.multiple, 3) )
            self.assertEqual(myscript.convert_bytes(value, 'Gbps'), result)
            result = 8 * value / ( pow(self.multiple, 4) )
            self.assertEqual(myscript.convert_bytes(value, 'Tbps'), result)

"""
class Nagios_Service(unittest.TestCase):
    def setUp(self):
        service = Nagios_Service()
    def test_init(self):
    def test_str(self):
    def test_status(self):

    def exec_test_status(self, value, result):
        self.assertEqual(myscript.nagios_value_status(value,100,90, 80), result)

    def test_status(self):
        self.exec_test_status(0, 'OK')
        self.exec_test_status(50, 'OK')
        self.exec_test_status(80, 'WARNING')
        self.exec_test_status(81, 'WARNING')
        self.exec_test_status(90, 'CRITICAL')
        self.exec_test_status(91, 'CRITICAL')
"""

class Nagios_Result(object):
    def setUp(self):
        self.result = myscript.Nagios_Result("Test Result")

    def test_init(self):
        pass

    def test_str(self):
        self.assertIsString(self.result.__str__())

    def test_worst(self):
        self.assertEqual(self.result.worst_status('CRITICAL','CRITICAL'), 'CRITICAL')
        self.assertEqual(self.result.worst_status('CRITICAL', 'WARNING'), 'CRITICAL')
        self.assertEqual(self.result.worst_status('CRITICAL', 'UNKNOWN'), 'CRITICAL')
        self.assertEqual(self.result.worst_status('CRITICAL', 'OK'), 'CRITICAL')
        self.assertEqual(self.result.worst_status('WARNING', 'CRITICAL'), 'CRITICAL')
        self.assertEqual(self.result.worst_status('WARNING','WARNING'), 'WARNING')
        self.assertEqual(self.result.worst_status('WARNING','UNKNOWN'), 'WARNING')
        self.assertEqual(self.result.worst_status('WARNING','OK'), 'WARNING')
        self.assertEqual(self.result.worst_status('OK', 'CRITICAL'), 'CRITICAL')
        self.assertEqual(self.result.worst_status('OK', 'WARNING'), 'WARNING')
        self.assertEqual(self.result.worst_status('OK', 'UNKNOWN'), 'UNKNOWN')
        self.assertEqual(self.result.worst_status('OK','OK'), 'OK')


    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.result.exit()

    def test_add(self):
        pass


if __name__ == "__main__":
    print ("Python version: ", sys.version.split('\n', 1)[0])
    unittest.main()
