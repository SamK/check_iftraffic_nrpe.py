#!/usr/bin/python
#
# NRPE plugin to monitor network traffic
#
# This script is based on check_iftraffic_nrpe.pl by Van Dyck Sven.
#
# This file tends follow Python coding good practices:
# pep8 --ignore=E111 --ignore=E221  --show-source --show-pep8 file.py
# pylint -E file.py
#
#
# Website: https://github.com/samyboy/check_iftraffic_nrpe.py
#

import os
import re
import sys
import time
import argparse

__version__ = '0.6'
__author__ = 'Samuel Krieg'

#
# Exceptions
#


class DeviceError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

#
# Calc functions
#


def bits2bytes(bits):
    """Convert bits into bytes"""
    return bits / 8


def max_counter():
    """Define the maximum allowed value by the system"""
    if sys.maxsize > 2 ** 32:
        return 2 ** 64 - 1
    else:
        return 2 ** 32 - 1


def calc_diff(value1, uptime1, value2, uptime2):
    """Calculate the difference between two values.
    The function takes care of the maximum allowed value by the system"""
    if uptime2 < uptime1:
        #"The host rebooted. The values are wrong anyway.
        # value2 is the closest.
        return value2
    if value1 > value2:
        return max_counter() - value1 + value2
    else:
        # normal behaviour
        return value2 - value1

#
# Nagios related functions
#


def uptime():
    """Returns the uptime in seconds (float)"""
    with open('/proc/uptime', 'r') as f:
        return float(f.readline().split()[0])


def get_perfdata(label, value, warn_level, crit_level, min_level, max_level):
    """Return the perfdata string of an item"""
    return ("%(label)s=%(value).2f;" % {'label': label, 'value': value} + \
            '%(warn_level)d;%(crit_level)d;%(min_level)d;%(max_level)d' % \
            {'warn_level': warn_level, 'crit_level': crit_level,
             'min_level': min_level, 'max_level': max_level})


def nagios_value_status(value, max_value, percent_crit, percent_warn):
    """Returns the string defining the Nagios status of the value"""
    if value > percent_crit * (max_value / 100):
        return 'CRITICAL'
    if value > percent_warn * (max_value / 100):
        return 'WARNING'
    return 'OK'


def worst_status(status1, status2):
    """Compare two Nagios statuses and returns the worst"""
    status_order = ['CRITICAL', 'WARNING', 'UNKNOWN', 'OK']
    for status in status_order:
        if status1 == status or status2 == status:
            return status

#
# File functions
#


def load_data(filename, columns):
    """load the data from a file."""
    values = dict()
    try:
        f = open(filename)
    except IOError:
        raise ValueError("failed to open data file")
    last_modification = os.path.getmtime(filename)
    i = 0
    for line in f:
        i += 1
        if i == 1:
            """ The uptime line has been added on version 0.5.2.
            When upgrading from version 0.5.1 this line throws a
            ValueError exception."""
            uptime0 = float(line)
        else:
            data = line.split()
            # get the device name
            try:
                device_name = data.pop(0)
            except IndexError:
                raise ValueError("data file truncated")
            # transform values into integer
            data = map(int, data)
            # create a nice dictionnary of the values
            values[device_name] = dict(zip(columns, data))
    if i < 1:
        raise ValueError("data file truncated")
    return uptime0, last_modification, values


def save_data(filename, data, columns, uptime1):
    """save the data to a file."""
    f = open(filename, 'w')
    f.write("%s\n" % uptime1)
    for device_name, if_data in data.iteritems():
        """write each line"""
        values = []
        for name in columns:
            values.append(str(if_data[name]))
        f.write("%s\t%s\n" % (device_name, "\t".join(values)))


#
# Network interfaces functions
#

def get_data():
    """list all the network data"""
    traffic = dict()
    my_file = open('/proc/net/dev')
    i = 0
    for line in my_file:
        i += 1
        if i > 2:  # skip the 2 first lines
            data = dict()
            iface_name, iface_data = line.split(':')
            iface_name = iface_name.strip()
            data_values = iface_data.split()
            # receive: column 0
            # transmit: column 8
            data['rxbytes'] = int(data_values[0])
            data['txbytes'] = int(data_values[8])
            traffic[iface_name] = data
    return traffic


#
# User arguments related functions
#

def exclude_device(exclude, data):
    """Remove the interfaces excluded by the user"""
    for device in exclude:
        if device in data:
            del data[device]

def excludere_device(exclude, data):
    """Remove the interfaces excluded by the user"""
    for devicere in exclude:
        devicere = re.compile(devicere)
        for device in list(data):
            if devicere.match(device):
                del data[device]


def specify_device(devices, data):
    """Only includes interfaces specified by the user"""

    # be sure that the interfaces exist
    for device in devices:
        if device not in data:
            raise DeviceError("Device %s not found." % device)

    datatmp = data.copy()
    for i in datatmp:
        if not i in devices:
            del data[i]


def parse_arguments(default_values):
    """Try to parse the command line arguments given by the user"""
    global __author__
    global __version__

    version_string = "%(prog)s-%(version)s by %(author)s" % \
                     {"prog": "%(prog)s", "version": __version__, \
                     "author": __author__}

    p = argparse.ArgumentParser(description="Description",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group()

    p.add_argument('-V', '--version', action='version',
                   help="shows program version", version=version_string)
    p.add_argument('-c', '--critical', default=default_values['critical'],
                   type=int,
                   help='Percentage for value CRITICAL \
                        (default:  %(default)s).')
    p.add_argument('-w', '--warning', default=85, type=int,
                   help='Percentage for value WARNING \
                        (default:  %(default)s).')
    p.add_argument('-b', '--bandwidth', default=default_values['bandwidth'],
                   type=int,
                   help='Bandwidth in bytes/s \
                        (default  %(default)s) \
                        Example: \
                        13107200 = 100Mb/s * 1024 * 1024 / 8. \
                        Yes, you must calculate.')
    p.add_argument('-f', '--data-file', default=default_values['data_file'],
                   help='specify an alternate data file \
                        (default: %(default)s)')
    g.add_argument('-i', '--interfaces', nargs='*',
                   help='specify interfaces (default: all interfaces)')
    g.add_argument('-x', '--exclude', nargs='*',
                   help='if all interfaces, then exclude some')
    g.add_argument('-X', '--excludere', nargs='*',
                   help='if all interfaces, then exclude matching')

    #p.add_argument('-u', '--units', type=str, choices=['G', 'M', 'k'],
    #               help='units')
    #p.add_argument('-B', '--total', action=store_true,
    #               help='calculate total of interfaces')

    return p.parse_args()


def main(default_values):
    """This main function is wayyyy too long"""

    #
    # Default values
    #

    # Nagios status codes
    _status_codes = {'OK': 0, 'WARNING': 1, 'CRITICAL': 2, 'UNKNOWN': 3}
    # counters needed for calculations
    # see get_data() to see how it is used
    _counters = ['rxbytes', 'txbytes']
    # The default exit status
    exit_status = 'OK'
    # The temporary file where data will be stored between to metrics
    uptime1 = uptime()
    args = parse_arguments(default_values)

    # this is a list of problems
    problems = []

    #
    # Capture current data
    #

    traffic = get_data()

    #
    # Load previous data
    #

    if not os.path.exists(args.data_file):
        """The script did not write the previous data.
        This might be the first run."""
        if not problems:
            problems.append("First run.")
            exit_status = 'UNKNOWN'
            if_data0 = None
    else:
        try:
            uptime0, time0, if_data0 = load_data(args.data_file, _counters)
        except ValueError:
            """This must be a script upgrade"""
            os.remove(args.data_file)
            if_data0 = None
            time0 = time.time()
            problems.append("Data file upgrade, skipping this run.")
            exit_status = 'UNKNOWN'

    #
    # Save current data
    #

    try:
        save_data(args.data_file, traffic, _counters, uptime1)
    except IOError:
        problems.append("Cannot write in %s." % args.data_file)
        exit_status = 'UNKNOWN'

    #
    # Data filtering and preparation
    #

    # remove interfaces if needed
    if args.exclude:
        exclude_device(args.exclude, traffic)

    if args.excludere:
        excludere_device(args.excludere, traffic)

    # only keep the wanted interfaces if specified
    if args.interfaces:
        try:
            specify_device(args.interfaces, traffic)
        except DeviceError as e:
            traffic = dict()
            message = str(e).replace("'", "")
            problems.append(message)
            exit_status = 'CRITICAL'

    #
    # Data analysis
    #

    # calculate the results and the output
    perfdata = []

    if not if_data0:
        """The script did not gather the previous data.
        This might be the first run."""
        if not problems:
            problems.append("First run.")
    else:
        # get the time between the two metrics
        elapsed_time = time.time() - time0
        for if_name, if_data1 in traffic.iteritems():

            if if_name not in if_data0:
                # The interface was added between the last and the current run.
                continue

            #
            # Traffic calculation
            #

            # calculate the bytes
            txbytes = calc_diff(if_data0[if_name]['txbytes'], uptime0,
                                if_data1['txbytes'], uptime1)
            rxbytes = calc_diff(if_data0[if_name]['rxbytes'], uptime0,
                                if_data1['rxbytes'], uptime1)
            # calculate the bytes per second
            txbytes = txbytes / elapsed_time
            rxbytes = rxbytes / elapsed_time

            #
            # Decide a Nagios status
            #

            # determine a status for TX
            new_exit_status = nagios_value_status(txbytes, args.bandwidth,
                                                  args.critical, args.warning)
            if new_exit_status != 'OK':
                problems.append("%s: %sMbs/%sMbs" % \
                                (if_name, txbytes, args.bandwidth))
            exit_status = worst_status(exit_status, new_exit_status)
            # determine a status for RX
            new_exit_status = nagios_value_status(rxbytes, args.bandwidth,
                                                  args.critical, args.warning)
            if new_exit_status != 'OK':
                problems.append("%s: %sMbs/%sMbs" % \
                                (if_name, rxbytes, args.bandwidth))
            exit_status = worst_status(exit_status, new_exit_status)

            #
            # Perfdata
            #

            """ How to get perfdata values:
            perfdata format (in 1 line):
            (user_readable_message_for_nagios) | (label)=(value)(metric);
            (warn level);(crit level);(min level);(max level)
            """

            warn_level = int(args.warning) * (args.bandwidth / 100)
            crit_level = int(args.critical) * (args.bandwidth / 100)
            min_level = 0.0
            max_level = args.bandwidth

            perfdata.append(get_perfdata('out-' + if_name, txbytes, warn_level,
                            crit_level, min_level, max_level))
            perfdata.append(get_perfdata('in-' + if_name, rxbytes, warn_level,
                            crit_level, min_level, max_level))

    #
    # Program output
    #

    print "TRAFFIC %s: %s | %s " % (exit_status, ' '.join(problems),
                                    ' '.join(perfdata))

    # This is the exit code
    sys.exit(_status_codes[exit_status])

if __name__ == '__main__':
    default_values = {}
    default_values["warning"] = 85
    default_values["critical"] = 98
    default_values["data_file"] = '/var/tmp/traffic_stats.dat'
    default_values["bandwidth"] = 13107200
    main(default_values)
