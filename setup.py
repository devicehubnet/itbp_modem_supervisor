#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install
from subprocess import check_call


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        check_call("systemctl enable dhmsupervisord.service".split())
        install.run(self)


setup(name='DeviceHub Modem Supervisor',
      version='0.6',
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
      cmdclass={
            'install': PostInstallCommand,
      })
