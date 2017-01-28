#!/usr/bin/env python

from distutils.core import setup

setup(name='ITBP Modem Supervisor',
      version='0.2',
      description='itbrainpower.net / devicehub.net modem supervisor daemon',
      author='Ionut Cotoi',
      author_email='ionut@devicehub.net',
      url='https://github.com/devicehubnet/itbp_modem_supervisor',
      install_requires=['transitions', 'RPi.GPIO'],
      scripts=['itbp-gprs.py'],
      data_files=[('/etc/systemd/system', ['itbp-gprs.service']),
                  ('/etc', ['itbp-gprs.ini']),
                  ('/usr/local/bin', ['itbp-gprs.py'])],
      )
