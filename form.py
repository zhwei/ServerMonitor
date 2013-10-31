#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Form:
    """
    this is form model
    just for fun
    and simple
    """

    def __init__(self, label, help_text=None):
        pass



class Input(object):

    def __init__(self, name, label, help_text, ):
        self.name = name
        self.label = label
        self.help_text = help_text

class TextBox(input):
    """
    input text
    """
    def __init__(self,  name, label, help_text, value=''):
        super.__init__(name, label, help_text,)

        self.value = value
        self.type = 'text'

class TextArea(input):
    """
    <textarea />
    """
    def __init__(self,  name, label, help_text, value='', placeholder='', **kwargs):
        super.__init__(name, label, help_text,)

        self.value = value
        self.placeholder = placeholder
        self.cols =kwargs.pop('cols')
        self.rows = kwargs.pop('rows')