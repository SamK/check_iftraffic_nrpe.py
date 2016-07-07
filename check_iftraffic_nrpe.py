#!/usr/bin/env python
"""
License:
--------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Description:
------------

NRPE plugin to monitor network traffic

This script is based on check_iftraffic_nrpe.pl by Van Dyck Sven.

Website: https://github.com/samyboy/check_iftraffic_nrpe.py
"""

import array
import fcntl
import os
import re
import socket
import struct
import sys
import time
import argparse

__version__ = '0.12.1'
__author__ = 'Samuel Krieg'

# Python2.x compatibility
if sys.version >= '3':
    long = int


#
# Exceptions
#


class DeviceError(Exception):
    """Raised when something related to a device went wrong."""
    def __init__(self, message):
        super(DeviceError, self).__init__(message)
        self.value = message

    def __str__(self):
        return repr(self.value)

#
# Classes
#


class InterfaceDetection(object):
    """Detects automatically the types of interfaces"""
    SIOCGIFHWADDR = 0x8927
    IF_NAMESIZE = 16
    families = {
        1: "ethernet",
        512: "ppp",
        772: "loopback",
        776: "sit",
        0xfffe: "unspecified"}

    def __init__(self):
        try:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_DGRAM,
                                        socket.IPPROTO_IP)
        except socket.error:
            self.socket = socket.socket(socket.AF_INET6,
                                        socket.SOCK_DGRAM,
                                        socket.IPPROTO_IP)

    def __del__(self):
        self.socket.close()

    def query_linktype(self, interface):
        """Detects automatically the type of the *interface*"""
        buff = struct.pack("%ds1024x" % self.IF_NAMESIZE, interface)
        buff = array.array("b", buff)
        fcntl.ioctl(self.socket.fileno(), self.SIOCGIFHWADDR, buff, True)
        fmt = "%dsH" % self.IF_NAMESIZE
        _, family = struct.unpack(fmt, buff[:struct.calcsize(fmt)])
        return self.families.get(family, "unknown")

    def linktype_filter(self, linktypes, data):
        """Remove from *data* the interfaces that are not *linktypes*"""
        for device in list(data):
            if self.query_linktype(device) not in linktypes:
                del data[device]


class DataFile(object):
    """data file format:
        - line 1: uptime
        - rest: data
    """

    def __init__(self, filename):
        self.filename = filename
        self.uptime = None
        self.data = None

    def mtime(self):
        """Returns the last modification time of the datafile.
           See os.path.getmtime() for the format.
        """
        return os.path.getmtime(self.filename)

    def read(self):
        """Returns the uptime and the data stored in the datafile"""
        file_obj = open(self.filename, "r")
        content = file_obj.readlines()
        file_obj.close()
        self.uptime = float(content[0])
        self.data = "".join(content[1:])
        return self.uptime, self.data

    def write(self):
        """writes the datafile. The data must be stored in DataFile.data"""
        if not self.uptime:
            self.uptime = str(self.uptime())

        file_obj = open(self.filename, 'w')
        file_obj.write("%s\n" % self.uptime)
        file_obj.write(self.data)


class ProcNetDev(object):
    """http://stackoverflow.com/a/1052628/238913

       Transform the /proc/net/dev file into a Python readable format
    """

    def __init__(self):
        self.filename = '/proc/net/dev'
        self.interfaces = {}
        self.content = None

    def parse(self, data=None):
        """Returns a python dictionnary including the values of the
           `/proc/net/dev` file. *data* can be a string containing
           the content of `/proc/net/dev`.
        """
        if data is None:
            data = self.read()

        lines = data.splitlines()

        # retrive the titles
        titles = lines[1]
        _, rx_titles, tx_titles = titles.split("|")

        # transorm the titles into a list
        rx_titles = list(["rx_" + a for a in rx_titles.split()])
        tx_titles = list(["tx_" + a for a in tx_titles.split()])

        # append the titles together
        titles = rx_titles + tx_titles

        # gather the values
        for line in lines[2:]:
            if line.find(":") < 0:
                continue  # impossible?
            # get the interface name
            if_name, data = line.split(":")
            if_name = if_name.strip()
            # get the values
            values = [int(x) for x in data.split()]
            # bring titles and values together to make interface data
            if_data = dict(list(zip(titles, values)))
            self.interfaces[if_name] = if_data
        return self.interfaces

    def read(self, filename=None):
        """Returns the content of the /proc/net/dev file as is."""
        if filename is None:
            filename = self.filename
        f = open(filename, "r")
        self.content = f.read()
        f.close()
        return self.content

#
# system functions
#


def uptime():
    """Returns the uptime in seconds (float)"""
    file_obj = open('/proc/uptime', 'r')
    uptime = float(file_obj.readline().split()[0])
    file_obj.close()
    return uptime


#
# Calculation functions
#


def max_counter():
    """Define the maximum allowed value by the system"""
    return sys.maxsize * 2 + 1


def calc_diff(value1, uptime1, value2, uptime2):
    """Calculate the difference between two values.
    The function takes care of the maximum allowed value by the system"""
    # raise error if not numeric type
    for val in [value1, uptime1, value2, uptime2]:
        if not (isinstance(val, int) or
                isinstance(val, float) or
                isinstance(val, long)):
            raise ValueError
    if uptime2 < uptime1:
        # "The host rebooted. The values are wrong anyway.
        # value2 is the closest.
        return value2
    if value1 > value2:
        # the counter did a reset. I hope that max_counter() is doint right
        return max_counter() - value1 + value2 + 1
    else:
        # normal behaviour
        return value2 - value1


class NagiosService(object):
    """Defines a Nagios service with a Perfdata output
    """
    def __init__(self):
        self.label = None
        self.value = None
        self.min_level = 0
        self.max_level = None
        self.warn_level = None
        self.crit_level = None

    def __str__(self):
        """Return the perfdata string"""
        return '%(label)s=%(value).2f;' \
               '%(warn_level)s;' \
               '%(crit_level)s;' \
               '%(min_level)s;' \
               '%(max_level)s' % \
               {'label': self.label,
                'value': self.value,
                'warn_level': self.warn_level,
                'crit_level': self.crit_level,
                'min_level': self.min_level,
                'max_level': self.max_level}

    def status(self):
        """Returns the string defining the Nagios status of the value"""
        if self.value >= self.crit_level:
            return 'CRITICAL'
        if self.value >= self.warn_level:
            return 'WARNING'
        return 'OK'


class NagiosResult(object):
    """A Nagios Result output with services in it
    """

    def __init__(self, name):
        self.status_codes = {'OK': 0,
                             'WARNING': 1,
                             'CRITICAL': 2,
                             'UNKNOWN': 3}

        self.status_order = ['CRITICAL',
                             'WARNING',
                             'UNKNOWN',
                             'OK']

        # The list of the services appened to this Results instance
        self._services = []

        # The final perfdata string
        self.name = name
        self.status = 'OK'
        self.messages = []
        self.perfdata = ''

    def __str__(self):
        """Return the output of a Nagios check"""

        # The name and the status

        output = "%s %s" % (self.name, self.status)

        # Some messages if existing
        if self.messages:
            output += ": " + ' '.join(self.messages)

        # perfdata
        output += ' |'
        for service in self._services:
            output += " %s" % service

        return output

    def worst(self, status1, status2):
        """Compares two Nagios statuses and returns the worst"""
        status_order = ['CRITICAL', 'WARNING', 'UNKNOWN', 'OK']
        for status in status_order:
            if status1 == status or status2 == status:
                return status

    def exit(self):
        """Exit the script with the accurate Nagios status
        """
        sys.exit(self.status_codes[self.status])

    def add(self, new_service):
        """ Add a NagiosService object in the Nagios results
        """
        self.status = self.worst(self.status, new_service.status())
        self._services.append(new_service)


#
# User arguments related functions
#


def exclude_device(exclude, data):
    """Remove the *exclude* device from *data*"""
    for device in exclude:
        if device in data:
            del data[device]


def excludere_device(exclude, data):
    """Remove the *exclude* device from *data* using regexp"""
    for devicere in exclude:
        devicere = re.compile(devicere)
        for device in list(data):
            if devicere.match(device):
                del data[device]


def specify_device(devices, data):
    """Only includes the *devices* in *data*"""

    # be sure that the interfaces exist
    for device in devices:
        if device not in data:
            raise DeviceError("Device %s not found." % device)

    datatmp = data.copy()
    for i in datatmp:
        if i not in devices:
            del data[i]


def convert_bytes(value, unit):
    """Convert bytes to something else"""
    # default is byte:

    if unit == 'Bps':
        return value

    if unit == 'bps':
        return value * 8

    multiple_unit = unit[0]
    data_unit = unit[1:]

    if data_unit == 'bps':
        value *= 8

    for single_unit in ['k', 'M', 'G', 'T']:
        value = value / 1000
        if single_unit == multiple_unit:
            return value
    raise Exception("Cannot parse %s" % unit)


def parse_arguments(default_values):
    """Try to parse the command line arguments given by the user"""
    global __author__
    global __version__

    unit_choices = ['Bps', 'kBps', 'MBps', 'GBps', 'TBps',
                    'bps', 'kbps', 'Mbps', 'Gbps', 'Tbps']

    version_string = "%(prog)s-%(version)s by %(author)s" % \
        {"prog": "%(prog)s", "version": __version__, "author": __author__}

    parser = argparse.ArgumentParser(
        description="NRPE plugin to monitor Linux network traffic")

    parser.add_argument('-V', '--version', action='version',
                        help="shows program version", version=version_string)
    parser.add_argument('-f', '--data-file',
                        default=default_values['data_file'],
                        help='specify an alternate data file \
                             (default: %(default)s)')
    parser.add_argument('-u', '--unit', default=default_values['unit'],
                        choices=unit_choices,
                        help='Specifies the unit to to display per seconds.\
                              (default: %(default)s). Note that the \
                              multiplier is 1000.')

    g_nag = parser.add_argument_group("nagios options", "")
    g_nag.add_argument('-c', '--critical', default=default_values['critical'],
                       type=int,
                       help='Percentage for value CRITICAL \
                            (default:  %(default)s).')
    g_nag.add_argument('-w', '--warning', default=85, type=int,
                       help='Percentage for value WARNING \
                            (default:  %(default)s).')

    g_if = parser.add_argument_group("interface options", "")
    g_if.add_argument('-b', '--bandwidth', default=default_values['bandwidth'],
                      type=int,
                      help="Define the maximum bandwidth (default %(default)s \
                            %(default_unit)s which is something around \
                            %(descr)s). If --units is specified, the value of \
                            BANDWIDTH must in the same unit." %
                            {'descr': default_values['bandwidth_descr'],
                             'default_unit': default_values['unit'],
                             'default': '%(default)s'})

    g_filter = parser.add_argument_group("filtering options",
                                         'The options "-i", "-x" and "-X" are \
                                         mutually exclusive')
    g_filter.add_argument('-l', '--linktype', nargs='*',
                          help='Only consider interfaces with given \
                               linktype. Possible values are "ethernet", \
                               "loopback", "ppp", "sit"')

    g_filter_x = g_filter.add_mutually_exclusive_group()
    g_filter_x.add_argument('-i', '--interfaces', nargs='*',
                            help='consider specified interfaces (default: \
                            all)')
    g_filter_x.add_argument('-x', '--exclude', nargs='*',
                            help='exclude interface specified by name')
    g_filter_x.add_argument('-X', '--excludere', nargs='*',
                            help='exclude interface specified by regexp')

    # p.add_argument('-B', '--total', action=store_true,
    #               help='calculate total of interfaces')

    return parser.parse_args()


def main(default_values):
    """This main function is wayyyy too long"""

    #
    # Default values
    #

    # previous data
    if_data0 = None
    # The temporary file where data will be stored between to metrics
    args = parse_arguments(default_values)

    # this is a list of problems
    problems = []
    ifdetect = InterfaceDetection()

    nagios_result = NagiosResult("Traffic %s" % args.unit)
    #
    # Read current data
    #

    procnetdev1 = ProcNetDev().read()
    uptime1 = uptime()
    traffic1 = ProcNetDev().parse(procnetdev1)

    #
    # Read previous data
    #

    datafile = DataFile(args.data_file)

    if not os.path.exists(args.data_file):
        # The script did not write the previous data.
        # This might be the first run.
        if not problems:
            nagios_result.messages.append("First run.")
            nagios_result.status = 'UNKNOWN'
    else:
        try:
            uptime0, procnetdev0 = datafile.read()
            time0 = datafile.mtime()
            if_data0 = ProcNetDev().parse(procnetdev0)
        except IndexError:
            os.remove(args.data_file)
            if_data0 = None
            time0 = time.time()
            nagios_result.messages.append("Malformed data file, skipping run.")
        except ValueError:
            # This must be a script upgrade
            os.remove(args.data_file)
            if_data0 = None
            time0 = time.time()
            nagios_result.messages.append("Data file upgrade, skipping run.")

    #
    # Save current data
    #

    # I can safeuly reuse the datafile object
    datafile = DataFile(args.data_file)
    datafile.uptime = uptime1
    datafile.data = procnetdev1

    try:
        datafile.write()
    except IOError:
        nagios_result.messages.append("Cannot write in %s." % args.data_file)
        nagios_result.status = 'CRITICAL'

    # parse data

    #
    # Data filtering and preparation
    #

    # remove interfaces if needed
    if args.exclude:
        exclude_device(args.exclude, traffic1)

    if args.excludere:
        excludere_device(args.excludere, traffic1)

    if args.linktype:
        ifdetect.linktype_filter(args.linktype, traffic1)

    # only keep the wanted interfaces if specified
    if args.interfaces:
        try:
            specify_device(args.interfaces, traffic1)
        except DeviceError as err:
            traffic1 = dict()
            message = str(err).replace("'", "")
            nagios_result.messages.append(message)
            nagios_result.status = 'CRITICAL'

    #
    # Data analysis
    #

    if not if_data0:
        # The script did not gather the previous data.
        # This might be the first run.
        if not nagios_result.messages:
            # TODO: what is the condition to go here?
            nagios_result.messages.append("First run.")
    else:
        # get the time between the two metrics
        elapsed_time = time.time() - time0
        for if_name, if_data1 in traffic1.items():

            if if_name not in if_data0:
                # The interface was added between the last and the current run.
                continue

            #
            # Traffic calculation
            #

            for counter in default_values['counters']:

                nagios_service = NagiosService()
                nagios_service.label = counter['prefix'] + if_name
                # calculate the bytes
                traffic_value = calc_diff(if_data0[if_name][counter['name']],
                                          uptime0,
                                          if_data1[counter['name']],
                                          uptime1)

                # calculate the bytes per second
                traffic_value /= elapsed_time

                #
                # Define service values
                #

                nagios_service.value = traffic_value
                nagios_service.max_level = float(args.bandwidth)
                # convert percent levels given by user into real values
                nagios_service.warn_level = (float(args.warning) *
                                             args.bandwidth / 100)
                nagios_service.crit_level = (float(args.critical) *
                                             args.bandwidth / 100)

                if args.unit != default_values['_system_unit']:
                    # convert to desired unit if asked
                    nagios_service.value = convert_bytes(nagios_service.value,
                                                         args.unit)

                nagios_result.add(nagios_service)

    #
    # Program output
    #

    print(nagios_result)
    nagios_result.exit()

if __name__ == '__main__':
    default_values = {}
    default_values["warning"] = 85
    default_values["critical"] = 98
    default_values["data_file"] = '/var/tmp/traffic_stats.dat'
    default_values["bandwidth"] = 1000 * 1000 * 100 / 8
    default_values["bandwidth_descr"] = "100 Mbps"
    # the traffic unit from /proc/net/dev
    default_values['_system_unit'] = 'Bps'
    default_values['unit'] = default_values['_system_unit']

    default_values["counters"] = [
        {"name": "rx_bytes", "prefix": "in-", "column": 0},
        {"name": "tx_bytes", "prefix": "out-", "column": 8}
    ]

    main(default_values)
