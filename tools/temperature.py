#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'zhwei'

import datetime

from pymongo import Connection
from serial import Serial

from tools.db import db

#Temperature Fomat
#
#temp = {
#    "name": "server or location",
#    "description": "",
#    "temp": "Temperature",
#    "datetime": datetime.datetime.now()
#}

ser = Serial(0)

def temperature():
    t = []
    while True:
        if db.control.find_one()['temp_monitor']:
            c = ser.read()
            if c == "\r":
                temp = ''.join(t[2:])
                temp1 = {
                    "name": "room_611",
                    "description": "鸿远楼611室",
                    "temp": float   (temp)/1000,
                    "datetime": datetime.datetime.now()
                }
                db.temperature.insert(temp1)
                print temp1
                t = []
            else:
                t.append(c)
        else:
            pass

temperature()