from urlparse import urlparse
import sqlite3
import time
import json 
import sys
import shutil

if len(sys.argv) < 2:
    print "Usage: %s path/to/chrome/history" % (sys.argv[0])
    sys.exit(0)

shutil.copy(sys.argv[1], "./history.db")
conn = sqlite3.connect("./history.db")

cursor = conn.cursor()

def debug(*args):
     print >> sys.stderr, " ".join(map(str, args))



def json_marshall_query(query, args=tuple()):
    debug("RUNNING QUERY", query, args)
    objs={}
    rows = cursor.execute(query, args)
    cols = [x[0] for x in cursor.description]

    debug("COLS ARE", cols)
    for row in rows:
        row_obj = {}
        for i, col in enumerate(row):
            row_obj[cols[i]] = row[i]

        objs[row_obj["id"]] = row_obj

    return objs

urls = json_marshall_query('SELECT * from urls')

debug("NUM VISITED URLS:", len(urls))

def to_windows_epoch(s):
    h = s + 11644473600 
    h = h * 1e6

    return h

def to_seconds(h):
    s=float(h)/1e6 # convert to seconds
    return s-11644473600 # number of seconds from 1601 to 1970


# convert from 1601 based timestamp (stored as us integer)
# s = datetime(1601,1,1) + timedelta(microseconds=us)

# discover last time we dumped and use that, too, right?

last_dump = 0
# last_dump = time.time() - (60*60*24*7)
timestamp =  to_windows_epoch(last_dump)
args = (timestamp,)

visits = json_marshall_query('SELECT * FROM visits WHERE visit_time > ?', args)

debug("NUM VISITS:", len(visits))

visit_ids = visits.keys()

for visit_id in visit_ids:
    visit = visits[visit_id] 
    url = urls[visit['url']]
    parsed = urlparse(url['url'])
    visit['url'] = url['url']
    visit['scheme'] = parsed.scheme
    visit['host'] = parsed.netloc
    visit['path'] = parsed.path
    visit['query'] = parsed.query

    visit['transition'] = str(visit['transition'])
    visit['visit_duration'] = visit['visit_duration'] / 1e7

    del visit['segment_id']
    del visit['from_visit']

    visit['time'] = int(to_seconds(visit['visit_time']))
    del visit['visit_time']

    print json.dumps(visit)
