#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue
import threading
import parsers
import weiboDB
import time
import weiboMain

mutex = threading.RLock()

class ThreadPool(object):
    def __init__(self, thread_num = 10):
        self.work_queue = Queue.Queue()
        self.threads = []
        #self.__init_work_queue(work_num)
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        #print 'init thread pool'
        for i in range(thread_num):
            #thread = WorkThread(self.work_queue)
            self.threads.append(WorkThread(self.work_queue))

    '''
    ## @func __init_work_queue
    ## @brief initail work queue
    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            self.add_job(do_job, i)
    '''

    def add_job(self, func, *args):
        #print 'add job'
        self.work_queue.put((func, list(args)))  # push job

    ## add on thread
    def add_thread(self, num):
        self.threads.append(WorkThread(self.work_queue))

    ## wait for all thread end
    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive():
                item.join()

class WorkThread(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        while True:
            try:
                '''
                if mutex.acquire(1):
                    do, args = self.work_queue.get(block = False)
                    do(args)
                    self.work_queue.task_done()  # tell system jobs is done
                    mutex.release()
                '''
                do, args = self.work_queue.get(timeout = 30)
                #print do, args
                do(args)  # do_job(args)
                self.work_queue.task_done()
            except Exception as e:
                print e  # such as time out
                continue
                #break

def do_job(args):
    time.sleep(1)
    print threading.current_thread()
    mutex.acquire()  # lock
    wbDB = weiboDB.weiboDB('uid.db')
    sql = 'SELECT uid FROM user_id LIMIT 0,1'
    uid = wbDB.query(sql)
    #print uid
    if uid == '0':
        print 'uid is none'
        return
    sql = 'DELETE FROM user_id WHERE uid = "%s"' % str(uid)
    wbDB.execute(sql)
    mutex.release()  # unlock

    WBUser = parsers.WBUserParser(str(uid))
    if WBUser.get_user_profile() == 0:
        return
    follow_url = 'follow?relate=follow'
    fans_url = 'follow?relate=fans'
    # get follow page count
    follow_page_count = 1#WBUser.get_page_count(follow_url)
    #if follow_page_count > 10:
    #    follow_page_count = 10
    if follow_page_count is not None:
        # get follow list
        for i in range(1, follow_page_count + 1):
            if WBUser.get_list(follow_url, i) == -1:  # forbidden
                break
        #bf = bloomfilter.BoolmFilter()
        mutex.acquire()
        for i in WBUser.follow_uid:
            if weiboMain.bf.exists(i) == False:
                weiboMain.bf.mark_value(i)
                sql = 'INSERT INTO user_id(uid) VALUES("%s")' % i
                wbDB.execute(sql)
        mutex.release()

    # get last 45 weibo
    weibo_url = 'weibo?'
    for i in range(1, 4):
        WBUser.get_weibo(weibo_url, i)
    # save to db
    mutex.acquire()  #lock
    WBUser.save_user_info()
    mutex.release()  #lock
