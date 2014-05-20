#!/usr/bin/env python
# -*- coding: utf-8 -*-

##################################
##                              ##
## @file: weiboMain.py          ##
## @data: 2014-5-20             ##
## @author: xspyhack@gmail.com  ##
## @brief: weibo crawler        ##
##                              ##
##################################

import weiboLogin
import urllib2
import urllib
import time

COPYRIGHT = {
        'SOFTWARE': '@weibo crawler',
        'AUTHOR': '@author: xspyhack@gmail.com',
        'VERSION': 'version: 0.01, GUET'
}

config = './account.conf'  #save username and password

if __name__ == '__main__':
    for x in COPYRIGHT:
        print x, COPYRIGHT[x]
    WBLogin = weiboLogin.weiboLogin()
    if WBLogin.login(config) == 1:
        print 'Login success!'
    else:
        print 'Login error!'
        exit()

