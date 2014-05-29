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
import parsers
import weiboDB
from works import ThreadPool
from works import do_job
import urllib2
import urllib
import time
import logging.config
from bloomfilter import bloomfilter

COPYRIGHT = {
        '>>>>SOFTWARE': '@weibo crawler',
        '>>>>AUTHOR': '@author: xspyhack@gmail.com',
        '>>>>VERSION': 'version: 0.01, GUET'
}

ACCOUNT = './config/account.conf'  #save username and password
bf = bloomfilter.BloomFilter()
logging.config.fileConfig("./config/logging.conf")
log = logging.getLogger('logger_weibo')

if __name__ == '__main__':
    for x in COPYRIGHT:
        print x, COPYRIGHT[x]
    #logging.config.fileConfig("./config/logging.conf")
    #log = logging.getLogger('logger_weibo')
    WBLogin = weiboLogin.weiboLogin()
    if WBLogin.login(ACCOUNT) == 1:
        print '****Login success! <@weiboMain>****'
    else:
        print '++++Login error! <@weiboMain>++++'
        exit()

    #WBMsg = weiboPage.weiboPage()
    #url = 'http://weibo.com/5107000912?from=otherprofile?topnav=1&wvr=5&loc=tagweibo'
    #url = 'http://weibo.com/bl4ckra1sond3tre/home?topnav=1&wvr=5'
    #WBMsg.get_first_page(url)
    #WBMsg.get_second_page(url)
    #WBMsg.get_third_page(url)

    # initial db
    wbDB_user = weiboDB.weiboDB('weibodb.db')
    wbDB_user.create_user_table()
    wbDB_uid = weiboDB.weiboDB('uid.db')
    wbDB_uid.create_uid_table()

    # start parser
    WBUser = parsers.WBUserParser(str(2576470935))
    WBUser.get_user_profile()
    follow_url = 'follow?relate=follow'
    fans_url = 'follow?relate=fans'
    follow_page_count = WBUser.get_page_count(follow_url)
    if follow_page_count is not None:
        #print '>>>>follow page count: ' + str(follow_page_count)
        for i in range(1, follow_page_count + 1):
            WBUser.get_list(follow_url, i)
        wbDB = weiboDB.weiboDB('uid.db')
        #wbDB.create_uid_table()
        for i in WBUser.follow_uid:
            bf.mark_value(i)
            sql = 'INSERT INTO user_id(uid) VALUES("%s")' % i
            wbDB.execute(sql)
    else:
        print '++++Get follow failed! exit!****'
        exit()
    '''
    fans_page_count = WBUser.get_page_count(fans_url)
    print '>>>>fans page count: ' + str(fans_page_count)
    for i in range(1, fans_page_count + 1):
        WBUser.get_list(fans_url, i)'''
    weibo_url = 'weibo?'
    WBUser.get_weibo(weibo_url, 1)
    WBUser.get_weibo(weibo_url, 2)
    WBUser.get_weibo(weibo_url, 3)
    WBUser.save_user_info()

    ## threadpool
    print '****Start thread pool****'
    tp = ThreadPool(5)
    for i in range(10000):
        time.sleep(0.2)
        tp.add_job(do_job, i)
    print '****for end****'
    tp.wait_allcomplete()
    print '****Thread pool is empty!****'
