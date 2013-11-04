#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pycurl
import requests


class WebMonitor:

    def __init__(self, url):

        self.url = url
        self.real_url = requests.get(url).url

    def req(self):
        """
        return requests object
        """
        return requests.get(self.url)

    def get_status_code(self):
        """Get the status code
        something like 200,404,500
        """

        return self.req.status_code

    def get_content(self):
        """ Get page content
        """
        return self.req.content

    def get_text(self):
        """Get page text
        """
        return self.req.text