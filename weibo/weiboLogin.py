#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib2
import urllib
import cookielib
import base64
import re
import json
import hashlib
import rsa
import binascii

class weiboLogin:
    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    post_data = {
            'entry': 'weibo',
            'gateway': '1',
            'form': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'sp': '',
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': '',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
    }

    def get_servertime(self, username):
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % username
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/4.0')
        res = urllib2.urlopen(req)
        data = res.read()
        #print data
        p = re.compile("\{(.*)\}")
        try:
            json_data = p.search(data).group(0)
            #print json_data
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            pubkey = data['pubkey']
            rsakv = data['rsakv']
            return servertime, nonce, pubkey, rsakv
        except:
            print 'Get servertime error! <@weiboLogin.get_servertime>'
            return None

    ## @func get_pwd
    ## @brief
    def get_pwd(self, password, servertime, nonce, pubkey):
        rsa_pubkey = int(pubkey, 16)
        key = rsa.PublicKey(rsa_pubkey, 65537)  # create public key
        msg = str(servertime) + '\t' + str(nonce) + '\n' + str(password) # 
        passwd = rsa.encrypt(msg, key) # encrypt
        passwd = binascii.b2a_hex(passwd) # encrypt to hex
        return passwd

    def get_user(self, username):
        username_ = urllib.quote(username)
        username = base64.encodestring(username_)[:-1]
        return username

    ## @func get_account
    def get_account(self, config):
        fd = file(config)
        flag = 0
        for line in fd:
            if flag == 0:
                username = line.strip()
                flag += 1
            else:
                pwd = line.strip()
        fd.close()
        return username, pwd

    ## @func check_retcode
    ## brief
    def check_retcode(self, url):
        if (re.match('(.*?)retcode=[0](.*?)', url)):
            return 0
        elif (re.match('(.*?)retcode=[101](.*?)', url)):
            return 1
        elif (re.match('(.*?)retcode=[4049](.*?)', url)):
            return 2
        else:
            return -1

    ## @func login
    ## @brief
    def login(self, config):
        username, pwd = self.get_account(config)
        print username

        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)'
        try:
            servertime, nonce, pubkey, rsakv = self.get_servertime(username)
            #print servertime
            #print nonce
            #print pubkey
            #print rsakv
        except:
            print 'Get servertime error! <@weiboLogin.login>'
            return

        weiboLogin.post_data['servertime'] = servertime
        weiboLogin.post_data['nonce'] = nonce
        weiboLogin.post_data['rsakv'] = rsakv
        weiboLogin.post_data['su'] = self.get_user(username)
        weiboLogin.post_data['sp'] = self.get_pwd(pwd, servertime, nonce, pubkey)
        weiboLogin.post_data = urllib.urlencode(weiboLogin.post_data)

        headers = {'User-Agent': 'Mozilla/4.0 (X11; Linux i686; rv:8.0) Firefox/8.0 Chrome/20.0.1132.57 Safari/536.11'}
        req = urllib2.Request(
                url = url,
                data = weiboLogin.post_data,
                headers = headers
        )
        res = urllib2.urlopen(req)
        html = res.read()
        #u_html = html.decode("utf-8")
        print html

        p = re.compile('location\.replace\(\"(.*)\"\)')
        try:
            login_url = p.search(html).group(1)
            # if retcode=4049, need to enter checkcode
            # if retcode=101, pwd error
            # if retcode=0, login success
            print login_url
            retcode = self.check_retcode(login_url)
            if retcode == 0:
                urllib2.urlopen(login_url)
                return 1
            elif retcode == 2:
                print 'Login error! (error: 4049, check code!) <@weiboLogin.login>'
            elif retcode == 1:
                print 'Login error! (error: 101, username or password error!) <@weiboLogin.login>'
            else:
                print 'Login error! (unknow error!) <@weiboLogin.login>'
            return 0
        except:
            return 0
