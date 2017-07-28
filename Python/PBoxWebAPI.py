# -*- coding:utf8 -*-
""" PBox WebMc API """
# !/usr/bin/python
# Python:   3.5.2
# Platform: Windows/ARMv7/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  PBox WebMc API.
# History:  2017/07/27 V1.0 [Heyn]
#

# (1) Limit all lines to a maximum of 79 characters
# (2) Private attrs use [__private_attrs]
# (3) [PyLint Message: See web: http://pylint-messages.wikidot.com/]

import json
import random
import string
import hashlib
import logging
import collections

import requests
from prettytable import  PrettyTable

ERROR_CODE = 'ERROR'
SUCCESS_CODE = 'SUCCESS'

def catch_exception(origin_func):
    """Catch exception."""
    def wrapper(self, *args, **kwargs):
        """Wrapper."""
        try:
            return origin_func(self, *args, **kwargs)
        except BaseException as msg:
            return '[ERROR] %s an exception raised. *** %s ***'%(origin_func, str(msg))
    return wrapper

@catch_exception
def msg_register(method, cgi):
    """Message register"""
    def decorator(func):
        """Decorator."""
        def wrapper(self, *args, **kwargs):
            """Wrapper."""
            payload = func(self, *args, **kwargs)
            header = {'Content-Type':'application/x-www-form-urlencoded'}
            if payload is not False and method == 'POST':
                ret = self.sess.post(self.url + cgi, data=payload,
                                     headers=header, timeout=5)
            elif payload is not False and method == 'GET':
                ret = self.sess.get(self.url + cgi, headers=header, timeout=3)

            if 'Response [200]' in str(ret) and 'SUCCESS' in ret.text:
                return 'SUCCESS'
            elif 'Response [200]' in str(ret) and ret.text != 'ERROR':
                return 'SUCCESS' if ret.text == '' else json.loads(ret.text)
            else:
                return '[ERROR] %s'%func
        return wrapper
    return decorator

@catch_exception
def print_pretty(title):
    """Print Pretty,"""
    def decorator(func):
        """Decorator."""
        def wrapper(*args, **kwargs):
            """Wrapper."""
            table = PrettyTable(title)
            table.align[title[0]] = '1'
            table.padding_width = 1
            for item in func(*args, **kwargs):
                table.add_row(item)
            print(table)
        return wrapper
    return decorator


class PBoxWebAPI:
    """PBox WebMc API Class."""
    def __init__(self, url='http://192.168.3.111', debugLevel=logging.INFO):
        self.url = url + '/cgi-bin/'
        self.sess = requests.session()
        self.token = '200'
        self.username = self.password = self.passwordmd5 = 'admin'
        self.pboxinfo = None
        self.jcid = self.jdid = dict(id='0') # JSON Channel ID & JSON Device ID.

        formatopt = '[%(asctime)s] [%(filename)s] [%(levelname)s] %(message)s'
        logging.basicConfig(level=debugLevel, format=formatopt)

    @msg_register('POST', 'Login.cgi')
    def logininit(self, username='admin', password='admin'):
        """Login."""

        pwdmd5 = hashlib.md5()
        pwdmd5.update(password.encode('UTF-8'))
        params = collections.OrderedDict()
        params['UserName'] = self.username = username
        params['PassWord'] = self.passwordmd5 = pwdmd5.hexdigest()
        return params

    @msg_register('POST', 'Verifypasswd.cgi')
    def loginverify(self):
        """Login Verify"""
        params = collections.OrderedDict(TokenNumber=self.token)
        params['UserName'] = self.username
        params['PassWord'] = self.passwordmd5
        return params

    def login(self, password='admin'):
        """WebMc Login"""
        if ERROR_CODE in self.logininit(password=password):
            return False
        if SUCCESS_CODE in self.loginverify():
            return True
        return False

    def newchannel(self, items, name='default'):
        """ PBox new a channel.
        Items params:
            ['Modbus-RTU', '/dev/ttymxc1', '9600', 'None', '8', '1', '500']
            ['Modbus-TCP', '192.168.3.1', '500', '500']
        """

        payload = ['TokenNumber=' + self.token,
                   'ChannelName=' + name,
                   'ChannelConf=' + ';'.join(items)]

        cid = msg_register('POST', 'AddChannel.cgi')(lambda x, y: '&'.join(y))(self, payload)
        self.pboxinfo = msg_register('GET', 'Pboxgetsetupinfo.cgi')(lambda x, y: y)(self, payload)
        self.jcid = dict(id=dict(self.pboxinfo)['pboxsetup']['model']['_id']) if isinstance(cid, dict) is False else cid
        logging.info('PBox Channel ID=%s', self.jcid)
        return True

    def newdevice(self, name='default'):
        """PBox New Device."""
        params = collections.OrderedDict(TokenNumber=self.token)
        params['DeviceName'] = name
        params['ChannelID'] = self.jcid['id']
        params['DeviceIP'] = '0.0.0.0'

        did = msg_register('POST', 'AddDevice.cgi')(lambda x, y: y)(self, params)
        self.pboxinfo = msg_register('GET', 'Pboxgetsetupinfo.cgi')(lambda x, y: y)(self, params)
        self.jdid = dict(id=dict(self.pboxinfo)['pboxsetup']['model']['device']['_id']) if isinstance(did, dict) is False else did
        logging.info('PBox Device ID=%s', self.jdid)
        return True

    @msg_register('POST', 'DeleteChannel.cgi')
    def delchannel(self):
        """PBox Delete Channel"""
        param = collections.OrderedDict(TokenNumber=self.token)
        param['DelChannelID'] = self.jcid['id']
        return param

    @msg_register('POST', 'DeleteDevice.cgi')
    def deldevice(self):
        """Delete Device."""
        params = collections.OrderedDict(TokenNumber=self.token)
        params['DelChannelID'] = self.jcid['id']
        params['DelDeviceID'] = self.jdid['id']
        return params

    def newitem(self, items):
        """ PBox New Item
            eg.
            Modbus RTU : item=['python', 'test', '5000', 'a', '0', '1', '1;3;2;1;INT16;0;0;0']
        """
        params = [self.token, self.jdid['id']]
        params.extend(items)

        iid = msg_register('POST', 'AddDataitem.cgi')(lambda x, y: '&'.join(y))(self, list(map(lambda x: 'item=%s'%x, params)))
        if isinstance(iid, dict) is not True:
            return False
        return True

    @print_pretty(['ItemName', 'AliasName', 'Frequency', 'Slave ID', 'Function Code', 'Slave Address','Rate', 'TYPE', 'MQTT', 'B/L Endian', 'R/W', 'Result'])
    def newitems(self, num):
        """PBox Insert Items."""
        alphabet = string.ascii_letters + string.digits
        payload = []
        for index in range(0, num):
            itemtype = ['BOOL', 'BYTE', 'DWORD', 'WORD', 'FLOAT', 'DOUBLE', 'INT16', 'INT32', 'STRING'+str(random.randint(1, 20)*2)]

            rtu = [random.randint(0, 255),  # Slave ID
                   random.randint(1, 5),    # Function Code
                   random.randint(0, 2147483647),   # Slave Address
                   random.randint(0, 1),    # Rate
                   random.choice(itemtype), # 'INT16'
                   random.randint(0, 1),    # MQTT
                   random.randint(0, 1),    # B/L Endian
                   random.randint(0, 1)     # R/W Mode
                  ]

            item = [''.join(random.choice(alphabet) for i in range(20)),    # Item Name
                    'test%d'%index, # Alias Name
                    str(random.randint(4999, 3600000)),  # Frequency
                    'a',
                    '0',
                    '1',
                    ';'.join([str(x) for x in rtu]),
                   ]
            payload.insert(-1, item[:3] + rtu + [str(self.newitem(item))])
        return payload

    @msg_register('POST', 'DeleteDataitem.cgi')
    def delitems(self):
        """PBox Delelte Items"""
        self.pboxinfo = msg_register('GET', 'Pboxgetsetupinfo.cgi')(lambda x, y: y)(self, None)
        size = len(dict(self.pboxinfo)['pboxsetup']['model']['device']['commDataItems'][0]['dataItem'])
        iids = []
        for index in range(0, size):
            iids.append(dict(self.pboxinfo)['pboxsetup']['model']['device']['commDataItems'][0]['dataItem'][index]['_id'])

        payload = ['TokenNumber=' + self.token, 'DelItemsID=' + ','.join(iids), 'DelDeviceID=' + self.jdid['id']]

        return '&'.join(payload)


def main():
    """Main Function Entry."""
    web = PBoxWebAPI('http://192.168.3.77')
    print(web.login())
    web.newchannel(items=['Modbus-RTU', '/dev/ttymxc1', '9600', 'None', '8', '1', '500'])
    web.newdevice(name='Default')
    web.newitems(50)
    # for i in range(0,5):
    #     print(web.newitem(['python', 'test', '5000', 'a', '0', '1', '1;3;2;1;INT16;0;0;0']))
    # print(web.delitems())

if __name__ == '__main__':
    main()