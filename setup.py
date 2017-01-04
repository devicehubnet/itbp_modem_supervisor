#!/usr/bin/env python

from distutils.core import setup

setup(name='ITBP Modem Supervisor',
      version='0.1',
      description='itbrainpower.net / devicehub.net modem supervisor daemon',
      author='Ionut Cotoi',
      author_email='ionut@devicehub.net',
      url='https://github.com/devicehubnet/itbp_modem_supervisor',
      install_requires=['transitions'],
      scritps=['itbp-gprs.py'],
      data_files=[('/etc/systemd/system', ['itbp-gprs.service']),
                  ('/etc', ['itbp-gprs.ini'])],
      )
