#!local/bin/python

"""
@author  :  Rajan Khullar
@created :  12/04/16
@updated :  12/11/16
"""

import requests, json, csv, os, shutil
from datetime import datetime as dt

BASEURL = 'https://csci870.nydev.me/api'
MODES = ['W', 'L', 'T', 'TT', 'LT']
DAYS = ['X', 'Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa']
ATTRS = {
    'X'  : ['building', 'floor', 'room', 'dow', 'hour', 'quarter', 'uxt', 'bssid', 'level'],
    'W'  : ['bssid'],
    'L'  : ['building', 'floor', 'room'],
    'T'  : ['hour'],
    'TT' : ['dow', 'hour', 'quarter'],
    'LT' : ['building', 'floor', 'room', 'hour']
}
TUPLES = {
    'W'  : lambda x: (x.bssid),
    'L'  : lambda x: (x.building, x.floor, x.room),
    'T'  : lambda x: (x.hour),
    'TT' : lambda x: (x.dow, x.hour, x.quarter),
    'LT' : lambda x: (x.building, x.floor, x.room, x.hour)
}

class api:
    @staticmethod
    def count(mode):
        url = '/'.join([BASEURL, 'count', mode])
        r = requests.get(url)
        return r.json()

    @staticmethod
    def cntx(m):
        return mod.parseJSON(m, api.count(m))

    @staticmethod
    def cnts():
        d = {}
        for m in MODES:
            d[m] = api.cntx(m)
        return d

    @staticmethod
    def waps():
        return list(map(lambda o: o.bssid, api.cntx('W')))

    @staticmethod
    def locs():
        return list(map(TUPLES['L'], api.cntx('L')))

    @staticmethod
    def lstd(l, start=0):
        d = {}; i = start
        for x in l:
            d[x] = i
            i += 1
        return d

    @staticmethod
    def lsti(ld):
        di = {}
        for v in ld:
            k = ld[v]
            di[k] = v
        return di

    @staticmethod
    def lstr(ld):
        di, l = api.lsti(ld), []
        a, z = min(di), max(di)
        for i in range(a, z+1):
            l.append(di[i])
        return l


class mod:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @staticmethod
    def vectorlist():
        d = {}
        for m in MODES:
            d[m] = []
        return d

    @staticmethod
    def vectordict():
        d = {}
        for m in MODES:
            d[m] = {}
        return d

    @staticmethod
    def parseJSON(mode, ja):
        l = []
        for jo in ja:
            x = mod(**jo)
            l.append(x)
        return l

    @staticmethod
    def parseTuple(mode, t):
        m = mod()

        if mode in ['W', 'T']:
            a = ATTRS[mode][0]
            setattr(m, a, t)
            return m

        l = ATTRS[mode]
        for i in range(len(l)):
            setattr(m, l[i], t[i])
        return m

    @staticmethod
    def object2tuple(o, mode):
        return TUPLES[mode](o)

    @staticmethod
    def object2dict(obj, keys):
        d = {}
        for k in keys:
            d[k] = getattr(obj, k)
        return d

    @staticmethod
    def dict2object(d, keys):
        m = mod()
        for k in keys:
            setattr(m, k, d[k])
        return m

    @staticmethod
    def objectslice(o, keys):
        m = mod()
        for k in keys:
            v = getattr(o, k)
            setattr(m, k, v)
        return m

    @staticmethod
    def dictslice(d, keys):
        z = {}
        for k in keys:
            z[k] = d[k]
        return z

    @staticmethod
    def objects2dict(l, keys):
        d = {}
        for k in keys:
            d[k] = []
        for o in l:
            for k in keys:
                v = getattr(o, k)
                d[k].append(v)
        return d

class dec:
    @staticmethod
    def scanify(fn):
        def decorated():
            with open('data/scans.csv') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    fn(row)
        return decorated

class dsv:
    @staticmethod
    def rawscan(row):
        f = ['bssid', 'level', 'building', 'floor', 'room']
        d = mod.dictslice(row, f)
        d['floor'] = int(d['floor'])
        d['level'] = int(d['level'])
        d['uxt'] = int(row['uxt'])
        t = dt.fromtimestamp(d['uxt'])
        d['dow'] = (t.weekday() + 2) % 7
        d['hour'] = t.hour
        d['quarter'] = int(t.minute/15)
        return d

    @staticmethod
    def scan2dict(o):
        return mod.object2dict(o, ATTRS['X'])

    @staticmethod
    def scans2dict(l):
        return mod.objects2dict(l, ATTRS['X'])

    @staticmethod
    def groupscans(vector, waps, minsize=100):
        n = len(vector['level'])
        d = {}
        for w in waps:
            d[w] = {'uxt':[], 'level':[]}
        for i in range(n):
            w = vector['bssid'][i]
            t = vector['uxt'][i]
            v = vector['level'][i]
            if w in waps:
                d[w]['uxt'].append(t)
                d[w]['level'].append(v)
        for w in waps:
            if len(d[w]['level']) < minsize:
                del d[w]
        return d

class ext:
    @staticmethod
    def genpath(*args):
        return os.path.sep.join(['data', *args])

    @staticmethod
    def ispath(*args):
        p = dsv.genpath(*args)
        return os.path.exists(p)

    @staticmethod
    def rmdir(*args):
        p = dsv.genpath(*args)
        if os.path.exists(p):
            shutil.rmtree(p)
        return p

    @staticmethod
    def mkdir(*args):
        p = dsv.rmdir(*args)
        os.mkdir(p)
        return p

def fmtHQ(h, q=None):
    if h < 12:
        sfx = 'AM'
    else:
        sfx = 'PM'
    t = h % 12
    if t == 0:
        t = 12
    if q != None:
        return  '%d:%02d%s' % (t, q*15, sfx)
    else:
        return  '%d%s' % (t, sfx)

def extUXT(uxt):
    t = dt.fromtimestamp(uxt)
    dow = (t.weekday() + 2) % 7
    hr = t.hour
    qt = int(t.minute/15)
    return mod(uxt=uxt, dow=dow, hour=hr, quarter=qt)

if __name__ == '__main__':
    for x in api.cntx('L'):
        print(x.building, x.floor, x.room, x.count)