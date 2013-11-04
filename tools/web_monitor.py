#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
More information and apis about PyCurl in this link
http://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
"""

import re
import pycurl
import requests
from BeautifulSoup import BeautifulSoup

class WebMonitor:

    def __init__(self, url):

        self.url = url
        self.real_url = requests.get(url).url

    def __soup(self):
        """Use beautiful soup process html
        """
        content = self.get_content()
        return BeautifulSoup(content)

    def __curl(self):
        """Init the pyCurl
        """
        _curl = pycurl.Curl()
        _curl.setopt(pycurl.URL, self.url)
        _curl.perform()
        return _curl

    def req(self):
        """
        return requests object
        """
        return requests.get(self.url)

    def get_status_code(self):
        """Get the status code
        something like 200,404,500
        """
        return self.req().status_code

    def get_content(self):
        """ Get page content
        """
        return self.req().content

    def get_text(self):
        """Get page text
        """
        return self.req().text

    def get_title(self):
        """Get title
        in <title></title>
        eg: 山东理工大学
        """
        return self.__soup().find('title').text

    def get_encoding(self):
        """ Get content encoding
        eg: utf-8
        """
        return self.req().encoding

    def name_look_up(self):
        """ time about name resolving
        in seconds
        """
        return self.__curl().getinfo(pycurl.NAMELOOKUP_TIME)

    def total_time(self):
        """ Total time
        including name resolving, TCP connect etc.
        in seconds
        """
        return self.__curl().getinfo(pycurl.TOTAL_TIME)

    def connect_time(self):
        """ Connect time
        it took from the start until the connect to the remote host (or proxy) was completed.
        in seconds
        """
        return self.__curl().getinfo(pycurl.CONNECT_TIME)

    def per_transfer_time(self):
        """ Per-Transfer time
        it took from the start until the file transfer is just about to begin.
        This includes all pre-transfer commands and negotiations that are specific
        to the particular protocol(s) involved. It does not involve the sending of
        the protocol- specific request that triggers a transfer.
        in seconds
        """
        return self.__curl().getinfo(pycurl.PRETRANSFER_TIME)

    def start_transfer_time(self):
        """ Start Transfer Time
        从开始到curl接收到第一个字节为止
        in sceonds
        """
        return self.__curl().getinfo(pycurl.STARTTRANSFER_TIME)

    def content_type(self):
        """ Connect type
        返回内容的类型 eg：text/html; charset=utf-8
        """

    def test(self):

        return self.__curl().getinfo(pycurl.CONTENT_TYPE)



w = WebMonitor('http://jwch.sdut.edu.cn')
#print w.get_status_code()
#print w.get_content()
#print w.get_title()
#print w.name_look_up()
#print w.test()
print w.get_encoding()