#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BitVector
import cmath
import random

class HashType():  
    
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed
    
    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap-1) & ret

class BloomFilter():
    '''类名是Bloom_Fileter，初始化时传入储存空间的大小(bits)，默认为 2^26 bits，约等于7千万
    mark_value 函数是用于标记值的函数，应传入想要标记的值
    exists 函数是用于检测某个值是否已经被标记的函数，应传入想要检测的值'''

    def __init__(self, amount = 1 << 26):
        '''amount是储存空间的个数(bits)'''
        self.container_size = amount
        self.hash_amount = 7 #哈希函数的个数
        self.container = BitVector.BitVector(size = int(self.container_size)) #分配内存
        self.hash_seeds = [5, 7, 11, 13, 31, 37, 61]

        self.hash = []
        for i in range(int(self.hash_amount)): #生成哈希函数
            self.hash.append(HashType(self.container_size, self.hash_seeds[i]))
        return 

    def exists(self, value):
        '''存在返回真，否则返回假'''
        if value == None:
            return False 
        for func in self.hash :
            if self.container[func.hash(str(value))] == 0 :
                return False
            return True

    def mark_value(self, value):
        '''value是要标记的元素'''
        for func in self.hash :
            self.container[func.hash(str(value))] = 1
        return
