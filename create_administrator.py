#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tools.users import create_user


_user = raw_input('请输入管理员用户名：')
_password = raw_input('请输入管理员密码：')
_real = raw_input('请输入管理员真实姓名：')

create_user(_user, _password,_real)

print('管理员 %s 创建成功'%_user)




