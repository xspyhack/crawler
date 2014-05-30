#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: xspyhack
'''

from utils import beautiful_soup
import weiboMain
import models
import urllib2
import urllib
import json
import re
import weiboDB

class WBUserParser():
    def __init__(self, uid):
        self.uid = uid
        self.url = 'http://weibo.com/p/100505%s/' % uid 
        self.headers = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'
        self.user_info = models.UserInfo()
        self.page_count = 0
        self.follow_uid = []
        self.body = {
            '__rnd': '',
            'feed_type': '0',
            'script_uri': '/p/100505' + uid + '/weibo',
            'id': '100505' + uid,
            'pl_name': 'Pl_Official_Left_ProfileFeed__23',
            'filtered_min_id': '',
            'max_msign': '',
            'count': '15',
            'end_id': '',
            'max_id': '',
            'page': 1,
            'pagebar': '',
            'pre_page': '1',
            'domid': '10050'
        }
        
    ## @func get_user_profile
    ## @brief get user info which is public to every one
    def get_user_profile(self):
        weiboMain.log.info('****@func get_user_profile****')
        info_url = self.url# + 'info'  # this is user info url
        try:
            req = urllib2.Request(info_url)
            req.add_header('User-Agent', self.headers)
            res = urllib2.urlopen(req)
            html = res.read()
        except urllib2.HTTPError, e:
            weiboMain.log.error('++++Open url [%s] failed. (Error code: %d) <@parser.get_user_profile>++++' % (info_url, e.code))
            return 0
        #res = urllib2.urlopen(info_url)
        #weiboMain.log.info(html)
        soup = beautiful_soup(html)  # use bs4 to parser xml
        if soup is None:
            return 0

        header_div = None
        profile_div = None
        contact_div = None
        career_div = None
        edu_div = None
        tags_div = None

        for script in soup.find_all('script'):
            text = script.text
            #print text
            if text.startswith('FM.view'):
                text = text.strip().replace(';', '').replace('FM.view(', '')[:-1]
                data = json.loads(text)
                domid = data['domid']
                if domid.startswith('Pl_Official_LeftInfo__'):
                    info_soup = beautiful_soup(data['html'])
                    if info_soup is None:
                        return 0
                    info_div = info_soup.find('div', attrs = {'class': 'profile_pinfo'})
                    if info_div is None:
                        return 0
                    for block_div in info_div.find_all('div', attrs = {'class': 'infoblock'}):
                        block_title = block_div.find('form').text.strip()
                        # get info block
                        if block_title == u'基本信息':
                            profile_div = block_div
                        elif block_title == u'联系信息':
                            contact_div = block_div
                        elif block_title == u'工作信息':
                            career_div = block_div
                        elif block_title == u'教育信息':
                            edu_div = block_div
                        elif block_title == u'标签信息':
                            tags_div = block_div
                elif domid == 'Pl_Official_Header__1':
                    #print 'header__1'
                    header_soup = beautiful_soup(data['html'])
                    #profile_header = header_soup.find('div', attrs = {'class': 'PRF_profile_header'})
                    #profile_top = profile_header.find(attrs = {'class': 'profile_top'})
                    header_div = header_soup.find('div', attrs = {'class': 'pf_head'})

            elif 'STK' in text:
                print 'STK'
                text = text.replace('STK && STK.pageletM && STK.pageletM.view(', '')[:-1]
                data = json.loads(text)
                pid = data['pid']
                if pid == 'pl_profile_infoBase':
                    profile_div = beautiful_soup(data['html'])
                elif pid == 'pl_profile_infoContact':
                    contact_div = beautiful_soup(data['html'])
                elif pid == 'pl_profile_infoCareer':
                    career_div = beautiful_soup(data['html'])
                elif pid == 'pl_profile_infoEdu':
                    edu_div = beautiful_soup(data['html'])
                elif pid == 'pl_profile_infoTag':
                    tags_div = beautiful_soup(data['html'])

        profile_map = {
            u'昵称': {'field': 'nickname'},
            u'所在地': {'field': 'location'},
            u'性别': {'field': 'sex'},
            u'生日': {'field': 'birth'},
            u'注册时间': {'field': 'regday'},
            u'邮箱': {'field': 'email'},
            u'QQ': {'field': 'qq'}
        }

        # header info
        if header_div is not None:
            #print 'header_div'
            for li in header_div.find_all(attrs = {'class': 'S_line1'}):
                follow = li.find(attrs = {'node-type': 'follow'})
                fans = li.find(attrs = {'node-type': 'fans'})
                if follow is not None:
                    weiboMain.log.info('follow ' + follow.text)
                    #setattr(self.user_info, follows, follow.text)
                    self.user_info.follows = int(follow.text)
                if fans is not None:
                    weiboMain.log.info('fans ' + fans.text)
                    #setattr(self.user_info, fans, fans.text)
                    self.user_info.fans = int(fans.text)
                if fans is not None and follow is not None:
                    if (int(follow.text) / int(fans.text)) > 3:
                        return 0

        # base info
        if profile_div is not None:
            #print 'profile_div'
            for div in profile_div.find_all(attrs = {'class': 'pf_item'}):
                k = div.find(attrs = {'class': 'label'}).text.strip()
                v = div.find(attrs = {'class': 'con'}).text.strip()
                if k in profile_map:
                    #func = (lambda s: s) \
                    #        if 'func' not in profile_map[k] \
                    #        else profile_map[k]['func']
                    #v = func(v)
                    setattr(self.user_info, profile_map[k]['field'], v)
                    weiboMain.log.info(k + v)

        # contact info
        if contact_div is not None:
            #print 'contact_div'
            for div in contact_div.find_all(attrs = {'class': 'pf_item'}):
                k = div.find(attrs = {'class': 'label'}).text.strip()
                v = div.find(attrs = {'class': 'con'}).text.strip()
                if k in profile_map:
                    setattr(self.user_info, profile_map[k]['field'], v)
                    weiboMain.log.info(k + v)

        # career info
        if career_div is not None:
            #print 'career_div'
            for div in career_div.find_all(attrs = {'class': 'con'}):
                if div is None:
                    break
                ps = div.find_all('p')
                for p in ps:
                    a = p.find('a')
                    if a is not None:
                        weiboMain.log.info('career:' + a.text)
                        self.user_info.career.append(a.text)

        # edu info
        if edu_div is not None:
            #print 'edu_div'
            for div in edu_div.find_all(attrs = {'class': 'con'}):
                if div is None:
                    break
                ps = div.find_all('p')
                for p in ps:
                    a = p.find('a')
                    if a is not None:
                        weiboMain.log.info('edu:' + a.text)
                        self.user_info.edu.append(a.text)
                        
        # tag info
        if tags_div is not None:
            #print 'tags_div'
            for div in tags_div.find_all(attrs = {'class': 'con'}):
                if div is None:
                    break
                for a in div.find_all('a'):
                    weiboMain.log.info('tags:' + a.text)
                    self.user_info.tags.append(a.text)
        return 1

    ##@func get_weibo
    ##
    def get_weibo(self, url, page = 0):
        weiboMain.log.info('****@func get_weibo****')
        page_url = self.url + url
        if page == 1:
            page_url = page_url# + 'from=page_100505&mod=TAB&ajaxpagelet=1&__ret=/u/' + self.uid
        elif page == 2:
            self.body['pagebar'] = '0'
            self.body['pre_page'] = self.body['page']
            page_url = page_url + urllib.urlencode(self.body)
        elif page == 3:
            self.body['pagebar'] = '1'
            self.body['pre_page'] = self.body['page']
            page_url = page_url + urllib.urlencode(self.body)

        try:
            #print page_url
            req = urllib2.Request(page_url)
            req.add_header('User-Agent', self.headers)
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            weiboMain.log.error('++++Open url [%s] failed. (Error code: %d) <@parser.get_weibo>++++' % (page_url, e.code))
            return
        soup = beautiful_soup(res.read())
        if soup is None:
            return 0

        for script in soup.find_all('script'):
            text = script.text
            if text.startswith('FM.view'):
                text = text.strip().replace(';', '').replace('FM.view(', '')[:-1]
                data = json.loads(text)
                domid = data['domid']
                if domid.startswith('Pl_Official_LeftProfileFeed__'):
                    page_soup = beautiful_soup(data['html'])
                    if page_soup is None:
                        weiboMain.log.error('++++Can not get weibo feed! <@parser.get_weibo>++++')
                        return 0
                    weibo_list = page_soup.find('div', attrs = {'class': 'WB_feed'})
                    if weibo_list is None:
                        weiboMain.log.error('++++Can not get weibo feed! <@parser.get_weibo>++++')
                        return 0
                    for weibo in weibo_list.find_all(attrs = {'class': 'WB_feed_type'}):
                        wb_text = weibo.find(attrs = {'class': 'WB_text'}).text.strip()
                        if wb_text is not None:
                            self.user_info.weibo.append(wb_text.replace('\\', '').replace('@', 'At:').replace('\'', ''))
                            weiboMain.log.info(wb_text)

    ##@func get_page_count
    def get_page_count(self, url):
        weiboMain.log.info('****@func get_follow_or_fans_page_count>****')
        page_url = self.url + url
        try:
            req = urllib2.Request(page_url)
            req.add_header('User-Agent', self.headers)
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            weiboMain.log.error('++++Open url [%s] failed. (Error code: %d) <@parser.get_page_count>++++' % (page_url, e.code))
            return
        #res = urllib2.urlopen(page_url)
        soup = beautiful_soup(res.read())
        if soup is None:
            weiboMain.log.error('++++Read html failed! <@parser.get_page_count>++++')
            return

        count = 0
        for script in soup.find_all('script'):
            text = script.text
            if text.startswith('FM.view'):
                text = text.strip().replace(';', '').replace('FM.view(', '')[:-1]
                data = json.loads(text)
                domid = data['domid']
                if domid == 'Pl_Official_LeftHisRelation__29':
                    page_soup = beautiful_soup(data['html'])
                    pages = page_soup.find('div', attrs = {'class': 'W_pages'})
                    if pages is None:
                        weiboMain.log.error('++++Find div W-pages failed! <parser.get_page_count>++++')
                        continue
                    for page in pages.find_all('a', attrs = {'class': 'S_bg1'}):
                        p = re.compile('page=(.*?)#place')
                        #print page['href']
                        try:
                            count = p.search(page['href']).group(1)
                        except:
                            weiboMain.log.error('++++Can not get page count! <@WBUserParser.get_page_count>++++')
                            continue
                        
        #print 'follow page count: ' + str(count)
        self.page_count = int(count)
        return self.page_count

    ## @func get_list
    ## @brief get follows or fans list
    def get_list(self, url, page = 0):
        weiboMain.log.info('****@func get_list****')
        if page > self.page_count:
            weiboMain.log.error('++++No this page! <@WBUserParser.get_list>++++')
            return 0
        weiboMain.log.info('>>>>page ' + str(page))
        follow_url = self.url + url +  '&page=' + str(page)
        try:
            req = urllib2.Request(follow_url)
            req.add_header('User-Agent', self.headers)
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            weiboMain.log.error('++++Open url [%s] failed. (Error code: %d) <@parser.get_list>++++' % (follow_url, e.code))
            return 0
        soup = beautiful_soup(res.read())

        for script in soup.find_all('script'):
            text = script.text
            if text.startswith('FM.view'):
                text = text.strip().replace(';', '').replace('FM.view(', '')[:-1]
                data = json.loads(text)
                domid = data['domid']
                if domid == 'Pl_Official_LeftHisRelation__29':
                    follow_soup = beautiful_soup(data['html'])
                    if follow_soup is None:
                        weiboMain.log.error('++++Can not get list because system forbidden! <@WBUserParser.get_list>++++')
                        return -1
                    follow_list = follow_soup.find('ul', attrs = {'class': 'cnfList'})
                    if follow_list is None:
                        weiboMain.log.error('++++Can not get list because system forbidden! <@WBUserParser.get_list>++++')
                        return -1
                    for li in follow_list.find_all('li', attrs = {'class': 'S_line1'}):
                        p = re.compile('uid=(.*?)&fnick')
                        #print li.text
                        try:
                            fo_uid = p.search(li['action-data']).group(1)
                            self.follow_uid.append(fo_uid)
                            #print fo_uid
                        except:
                            return 0
        return 1
    def save_user_info(self):
        weiboMain.log.info('****save user info****')
        wbDB = weiboDB.weiboDB('weibodb.db')
        #wbDB.create_user_table()
        sql = r'INSERT INTO user_model(nickname, location, sex, birth, regday, email, qq, edu, career, tags, fans, follows, weibo)'
        sql += ' VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %d, %d, "%s")' % (self.user_info.nickname, self.user_info.location, self.user_info.sex, self.user_info.birth, self.user_info.regday, self.user_info.email, self.user_info.qq, self.user_info.edu, self.user_info.career, self.user_info.tags, int(self.user_info.fans), int(self.user_info.follows), self.user_info.weibo)

        wbDB.execute(sql)
        weiboMain.log.info('****save user info end****')
