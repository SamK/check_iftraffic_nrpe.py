#!/usr/bin/env python

from distutils.core import setup

setup(name='check_iftraffic_nrpe',
      version='0.12.1',
      description='Nagios NRPE plugin to check Linux network traffic',
      scripts = ['check_iftraffic_nrpe.py'],
      author='Samuel Krieg',
      author_email='samuel.krieg+github@gmail.com',
      url='https://github.com/SamK/check_iftraffic_nrpe.py',
      download_url = 'https://github.com/SamK/check_iftraffic_nrpe.py/tarball/0.12.1',
      keywords = ['nagios', 'traffic', 'nrpe', 'monitoring']
)
