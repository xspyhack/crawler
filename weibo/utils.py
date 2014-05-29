#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

def beautiful_soup(html):
    try:
        from bs4 import BeautifulSoup, FeatureNotFound
    except ImportError:
        print 'BeautifulSoup4 Error!'
        #raise DependencyNotInstalledError("BeautifulSoup4")

    return BeautifulSoup(html, 'lxml')
