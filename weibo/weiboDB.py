#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

class weiboDB():
    def __init__(self, db_name):
        self.conn = sqlite3.connect("./data/" + db_name)
        self.cur = self.conn.cursor()

    def create_user_table(self):
        sql = 'CREATE TABLE user_model(\
            id integer primary key autoincrement,\
            nickname varchar(32),\
            location varchar(64),\
            sex char(4),\
            birth date,\
            regday date,\
            email char(32),\
            qq char(16),\
            edu varchar(64),\
            career varchar(64),\
            tags varchar(64),\
            fans integer,\
            follows integer,\
            weibo varchar(15000))'
        self.cur.execute(sql)
        self.conn.commit()

    def create_uid_table(self):
        sql = 'CREATE TABLE user_id(id integer primary key autoincrement, uid char(11))'
        self.cur.execute(sql)
        self.conn.commit()

    def execute(self, sql):
        if sql != '':
            #print sql
            self.cur.execute(sql)
            self.conn.commit()

    def query(self, sql):
        if sql != '':
            self.cur.execute(sql)
            #print 'return'
            res = self.cur.fetchone()
            if res is not None:
                return res[0]
            else:
                return str(0)
    
    def get_count(self):
        return self.cur.lastrowid
