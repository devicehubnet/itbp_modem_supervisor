#!/usr/bin/env python

from distutils.core import setup

setup(name='DeviceHub Modem Supervisor',
      version='0.5',
      description='DEVICEHUB modem supervisor daemon',
      author='Ionut Cotoi',
      author_email='ionut@devicehub.net',
      url='https://github.com/devicehubnet/itbp_modem_supervisor',
      packages=['DHModemSupervisor'],
      install_requires=['RPi.GPIO'],
      scripts=['dhmsupervisord.py'],
      data_files=[('/lib/systemd/system', ['dhmsupervisord.service']),
                  ('/etc/devicehub', ['dhmsupervisord.ini.sample']),
                  ('/usr/local/bin', ['dhmsupervisord.py'])],
      )
