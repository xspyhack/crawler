#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import sys
import time

reload(sys)

sys.setdefaultencoding('utf-8')

class weiboPage:
    body = {
        '__rnd': '',
        '_k': '',
        '_t': '0',
        'count': '50',
        'end_id': '',
        'max_id': '',
        'page': 1,
        'pagebar': '',
        'pre_page': '0',
        'uid': ''
    }

    uid_list = []
    charset = 'utf-8'

    def get_msg(self, uid):
        weiboPage.body['uid'] = uid
        url = self.get_url(uid)
        self.get_first_page(url)
        self.get_second_page(url)
        self.get_thrid_page(url)

    ## @func get_first_page
    ## brief
    def get_first_page(self, url):
        weiboPage.body['pre_page'] = weiboPage.body['page'] - 1
        url = url + urllib.urlencode(weiboPage.body)
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        html = res.read()
        self.writefile('./output/html_1', html)
        self.writefile('./output/result_1', eval("u'''" + html + "'''"))

    ##
    ##
    def get_second_page(self, url):
        weiboPage.body['count'] = '15'
        # weiboPage.body['end_id'] = ''
        # weiboPage.body['max_id'] = ''
        weiboPage.body['pagebar'] = '0'
        weiboPage.body['pre_page'] = weiboPage.body['page']

        url = url + urllib.urlencode(weiboPage.body)
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        html = res.read()
        self.writefile('./output/html_2', html)
        self.writefile('./output/result_2', eval("u'''" + html + "'''"))

    ##
    ##
    def get_third_page(self, url):
        weiboPage.body['count'] = '15'
        weiboPage.body['pagebar'] = '1'
        weiboPage.body['pre_page'] = weiboPage.body['page']

        url = url + urllib.urlencode(weiboPage.body)
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        html = res.read()
        self.writefile('./output/html_3', html)
        self.writefile('./output/result_3', eval(u"'''" + html + "'''"))

    ## @func get url
    ## @brief
    def get_url(self, uid):
        url = 'http://weibo.com/' + uid + '?frome=otherprofile&wvr=5&loc=tagweibo'
        return url

    ## @func get_uid
    ## @brief
    def get_uid(self, account):
        fd = file(account)
        for line in fd:
            weiboPage.uid_list.append(line)
            print line
            time.sleep(1)

    ## @func writefile
    ##
    def writefile(self, filename, content):
        fd = file(filename, 'w')
        fd.write(content)
        fd.close()
