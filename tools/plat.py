#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform

def get_uname():
    """
    system uname
    eg:
    ('Linux', 'fedora.echorand', '3.7.4-204.fc18.x86_64',
    '#1 SMP Wed Jan 23 16:44:29 UTC 2013', 'x86_64')
    """
    return platform.uname()

def get_system():
    '''
    get system platform eg: linux or windows
    '''
    return platform.system()

def get_release():
    """
    get release version num
    """
    return platform.release()

def get_linux_distribution():
    '''
    get info about linux distribution
    '''
    return platform.linux_distribution()

def get_architecture():
    """
    return 64bit or 32bit
    """
    return platform.architecture()[0]