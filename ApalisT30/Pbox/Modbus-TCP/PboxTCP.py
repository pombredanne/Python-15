# -*- coding:utf-8 -*-
""" Pbox Modbus RTU"""
# !/usr/bin/python
# Python:   3.5.2
# Platform: Windows
# Author:   Heyn
# Program:  Modbus RTU
# History:  2017/02/14 V1.0.0[Heyn]

import pymodbus
import imx6_ixora_led as led


class PboxTCP:
    """Pbox Modbus Class"""

    def __init__(self, ip='127.0.0.1', port=502):
        super(PboxTCP, self).__init__()
        pymodbus.new_tcp(ip, port)

    def __del__(self):
        led.ioctl(led.IXORA_LED4, led.GREEN, led.LOW)
        led.ioctl(led.IXORA_LED4, led.RED, led.LOW)
        pymodbus.free_tcp()

    def send(self, readlist, length=1):
        """Send Data to Device."""
        try:
            ret = pymodbus.read_registers(readlist[0:3], length)
        except BaseException as err:
            led.ioctl(led.IXORA_LED4, led.GREEN, led.LOW)
            led.ioctl(led.IXORA_LED4, led.RED, led.HIGH)
            print(err)
            return -1
        else:
            led.ioctl(led.IXORA_LED4, led.RED, led.LOW)
            led.ioctl(led.IXORA_LED4, led.GREEN, led.HIGH)
        finally:
            pass
        return ret[0]
