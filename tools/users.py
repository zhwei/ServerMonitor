#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'zhwei'


import bcrypt

from tools.db import db, update

def gen_code(password):
    """ Generate Encrypted Password
    """
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_code(raw_password, crypt_password):
    """ Check Password
    raw_password: from login page
    crypt_password: from mongodb
    """
    raw_hash = bcrypt.hashpw(raw_password.encode('utf-8'), crypt_password.encode('utf-8'))
    return raw_hash == crypt_password

def create_admin(username, password, real_name):
    """
    user = {
        'username': str,
        'password': str,
        'real_name': str,
    }
    """
    dic = {
        'username': username,
        'password': gen_code(password),
        'real_name': real_name
    }
    db.user.insert(dic)

def update_admin(oid, user, pw, real):
    passwd = gen_code(pw)
    dic = {'username': user,
           'password': passwd,
           'real_name':real}
    update(oid, db.user, dic)