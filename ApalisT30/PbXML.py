# -*- coding:utf8 -*-
""" P-Box XML """
# !/usr/bin/python
# Python:   3.5.2
# Platform: Windows
# Author:   Heyn
# Program:  P-Box XML
# History:  2017/02/10 V1.0.0[Heyn]


# import xml.etree.ElementTree as PBET
from xml.dom.minidom import parse
import xml.dom.minidom

class PbXML:
    """P-Box XML"""
    def __init__(self, path='/www/pages/htdocs/conf/config.xml'):
        super(PbXML, self).__init__()
        try:
            self.tree = xml.dom.minidom.parse(path)
            self.data = self.tree.documentElement
        except BaseException:
            print("Error:cannot parse file : %s." % path)

    def dataitem(self):
        """Get XML Data Items"""
        datalist = []
        dicts = {'BOOLEAN':'B08','BYTE':'B08','int16_t':'S16', 'int32_t':'S32', 'DOUBLE':'D32', 'WORD':'S32'}
        for items in self.data.getElementsByTagName('dataItem'):
            if items.hasAttribute("config"):
                itemlist = items.getAttribute("config").split(';')
                datalist.append([int(itemlist[1]), int(itemlist[2]), dicts[itemlist[4]]])
        return datalist

    def driverinfo(self):
        """Get Serial Configure Information."""
        # datalist = []
        for items in self.data.getElementsByTagName('driver'):
            if items.hasAttribute("config"):
                datalist = items.getAttribute("config").split(';')
        print(datalist)

    def devicedriver(self):
        """ Get Device Driver.
            [Modbus-RTU, Modbus-TCP]
        """
        for items in self.data.getElementsByTagName('model'):
            if items.hasAttribute("devicedriver"):
                return items.getAttribute("devicedriver")
        return None

# if __name__ == "__main__":
#     XML = PbXML()
#     print(XML.dataitem())
#     XML.driverinfo()
#     print(XML.devicedriver())
