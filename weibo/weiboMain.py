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
import weiboPage
import urllib2
import urllib
import time

COPYRIGHT = {
        'SOFTWARE': '@weibo crawler',
        'AUTHOR': '@author: xspyhack@gmail.com',
        'VERSION': 'version: 0.01, GUET'
}

account = './config/account.conf'  #save username and password

if __name__ == '__main__':
    for x in COPYRIGHT:
        print x, COPYRIGHT[x]
    WBLogin = weiboLogin.weiboLogin()
    if WBLogin.login(account) == 1:
        print 'Login success! <@weiboMain>'
    else:
        print 'Login error! <@weiboMain>'
        exit()

    WBMsg = weiboPage.weiboPage()
    #url = 'http://weibo.com/5107000912?from=otherprofile?topnav=1&wvr=5&loc=tagweibo'
    url = 'http://weibo.com/bl4ckra1sond3tre/home?topnav=1&wvr=5'
    WBMsg.get_first_page(url)
    WBMsg.get_second_page(url)
    WBMsg.get_third_page(url)

