#!/usr/bin/env python3
import redis
import time
#from startRedis import r

r = redis.Redis(host='localhost', port=6379, decode_responses=True)# redis.Redis(host='localhost', port=6379)

def setUser(alias,ipport):
    #global r # poso això per dir que faci servir la variable global r
    r.set(alias,ipport)
    return
     
def getUser(alias):
    #global r # poso això per dir que faci servir la variable global r
    return r.get(alias)

def getAllKeys():   #Per tal d'obtenir la llista d'usuaris conectats
    return r.keys()