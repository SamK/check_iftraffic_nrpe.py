#!/usr/bin/env python
import os
import sys
import unittest


sys.path.insert(0, os.path.dirname(__file__) + '/..')
import check_iftraffic_nrpe as myscript

"""
class FooTest(unittest.TestCase):
class DeviceError(Exception):
class InterfaceDetection(object):
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
       self.sample_values = [ 0, 1, 10, 100, 1000, 3214, 57665, 739373, 8635791]
       self.byte_units = ['Bps', 'kBps', 'MBps', 'GBps', 'TBps']
       self.bit_units = ['bps', 'kbps', 'Mbps', 'Gbps', 'Tbps']


    def test_convert_bytes(self):
        # Test Bytes
        for value in self.sample_values:
            result = value
            for unit in self.byte_units:
                #print ("Convertion test:  %sB = %s%s" % (value, result, unit))
                self.assertEqual(myscript.convert_bytes(value, unit), result, ("Convert %sB in %s" % (value, unit)))
                result = result / self.multiple

    def test_convert_bytes_to_bits(self):
        # Test Bytes
        for value in self.sample_values:
            self.assertEqual(myscript.convert_bytes(0, 'bps'), 0)
            self.assertEqual(myscript.convert_bytes(0, 'kbps'), 0)
            self.assertEqual(myscript.convert_bytes(0, 'Tbps'), 0)
            self.assertEqual(myscript.convert_bytes(1, 'bps'), 8)
            self.assertEqual(myscript.convert_bytes(1000, 'kbps'), 8)
            result = 8 * value
            for unit in self.bit_units:
                #print ("Convertion test:  %sB = %s%s" % (value, result, unit))
                self.assertEqual(myscript.convert_bytes(value, unit), result, ("Convert %sBps in %s" % (value, unit)))
                result = result / self.multiple

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
        try:
            self.assertRaises(SystemExit)
        finally:
            self.result.exit()

    def test_add(self):
        pass

class Data_File(unittest.TestCase):

    def setUp(self):
        self.filename = './unit-tests-datafile'
        self.datafile = myscript.DataFile(self.filename)

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.unlink(self.filename)

    def write_datafile(self):
        self.datafile.uptime = myscript.uptime()
        self.datafile.data = myscript.ProcNetDev().read()
        self.datafile.write()

    def parse_data(self, uptime, procnetdev):
        self.assertTrue(isinstance(uptime, float), 'The uptime must be a float type')
        self.assertGreater(uptime, 0.0, 'The uptime cannot be 0')
        lines = procnetdev.split('\n')
        self.assertGreater(len(lines), 2, 'The /proc/net/dev file does not seem to be correctly parsed')

    def test_parse_datafile(self):
        self.write_datafile()
        uptime0, procnetdev0 = self.datafile.read()
        self.parse_data(uptime0, procnetdev0)

    def test_write_datafile(self):
        self.write_datafile()

    def test_parse_empty_datafile(self):
        open(self.filename, 'w').close()
        self.assertRaises(IndexError,self.datafile.read)

    def test_read_missing_datafile(self):
        if os.path.isfile(self.filename):
            os.unlink(self.filename)
        self.assertRaises(IOError, self.datafile.read)

    def test_read_malformed_datafile(self):
        f = open(self.filename, 'w')
        f.write('This is the content of a malformed datafile')
        f.close()
        self.assertRaises(ValueError, self.datafile.read)

    def test_write_non_writable_datafile(self):
        f = open(self.filename, 'a')
        os.chmod(self.filename, 0o444);
        self.assertRaises(IOError,self.write_datafile)

    def test_write_non_readable_datafile(self):
        self.write_datafile()
        os.chmod(self.filename, 0o000);
        self.assertRaises(IOError,self.write_datafile)


if __name__ == "__main__":
    print ("Python version: ", sys.version.split('\n', 1)[0])
    unittest.main()
