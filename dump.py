# Browser Accounter
# BrowseStat
# BrowseStat: or Where did my time go?

from urlparse import urlparse
import sqlite3
import time
import json
import os
import sys
import shutil
import time

if len(sys.argv) < 2:
    print "Usage: %s path/to/chrome/history" % (sys.argv[0])
    sys.exit(0)

FULL_FILE_PATH=os.path.abspath(sys.argv[1])
TEMP_HISTORY_FILE=".history.db"
RUN_AT = int(time.time())

BROWSTAT_DIR="~/.config/browstats"
try:
    os.makedirs(os.path.expanduser(BROWSTAT_DIR))
except OSError: # already exists, hopefully
    pass

LOG_FILE=os.path.expanduser(os.path.join(BROWSTAT_DIR, "state.json"))

def load_last_dump():
    d = 0
    if not os.path.exists(LOG_FILE):
        return None

    with open(LOG_FILE) as f:
        data = f.read()
        parsed = json.loads(data)

        debug("READ LOG DATA", parsed)
        return parsed

def write_last_dump():
    log_data = load_last_dump()
    if not log_data:
        log_data = { }

    log_data[FULL_FILE_PATH] = {
        "timestamp" : RUN_AT
    }

    debug("WRITING LOG DATA")

    with open(LOG_FILE, "w") as f:
        f.write(json.dumps(log_data))

shutil.copy(sys.argv[1], TEMP_HISTORY_FILE)
def debug(*args):
     print >> sys.stderr, " ".join(map(str, args))

CONN = sqlite3.connect(TEMP_HISTORY_FILE)
CURSOR = CONN.cursor()
def json_marshall_query(query, args=tuple()):
    debug("RUNNING QUERY", query, args)
    objs={}
    rows = CURSOR.execute(query, args)
    cols = [x[0] for x in CURSOR.description]

    debug("COLS ARE", cols)
    for row in rows:
        row_obj = {}
        for i, col in enumerate(row):
            row_obj[cols[i]] = row[i]

        objs[row_obj["id"]] = row_obj

    return objs

def to_windows_epoch(s):
    h = s + 11644473600
    h = h * 1e6

    return h

def to_seconds(h):
    s=float(h)/1e6 # convert to seconds
    return s-11644473600 # number of seconds from 1601 to 1970


def main():
    urls = json_marshall_query('SELECT * from urls')
    debug("NUM VISITED URLS:", len(urls))

    last_dump = load_last_dump()
    # last_dump = time.time() - (60*60*24*7)
    if last_dump and FULL_FILE_PATH in last_dump:
        timestamp = to_windows_epoch(last_dump[FULL_FILE_PATH]['timestamp'])
    else:
        timestamp = 0
    args = (timestamp,)

    visits = json_marshall_query('SELECT * FROM visits WHERE visit_time > ?', args)

    debug("NUM VISITS:", len(visits))


    visit_ids = visits.keys()

    for visit_id in visit_ids:
        visit = visits[visit_id]

        # add timing info
        visit['time'] = int(to_seconds(visit['visit_time']))
        visit['transition'] = str(visit['transition'])
        visit['visit_duration'] = visit['visit_duration'] / 1e7

        # ADD URL INFO
        url = urls[visit['url']]
        parsed = urlparse(url['url'])

        visit['dbpath'] = FULL_FILE_PATH
        visit['url'] = url['url']
        visit['scheme'] = parsed.scheme
        visit['host'] = parsed.netloc
        visit['path'] = parsed.path
        visit['query'] = parsed.query

        # ADD PREV GRAPH URL INFO
        if visit['from_visit']:
            if visit['from_visit'] in visits:
                prev_visit = visits[visit['from_visit']]
                if prev_visit['url'] in urls:
                    prev_url = urls[prev_visit['url']]
                    parsed = urlparse(prev_url['url'])
                    visit['prev_url'] = prev_url['url']
                    visit['prev_scheme'] = parsed.scheme
                    visit['prev_host'] = parsed.netloc
                    visit['prev_path'] = parsed.path
                    visit['prev_query'] = parsed.query
                else:
                    parsed = urlparse(prev_visit['url'])
                    visit['prev_url'] = prev_visit['url']
                    visit['prev_scheme'] = parsed.scheme
                    visit['prev_host'] = parsed.netloc
                    visit['prev_path'] = parsed.path
                    visit['prev_query'] = parsed.query

        del visit['segment_id']
        del visit['from_visit']

        del visit['visit_time']

        print json.dumps(visit)

    write_last_dump()

if __name__ == "__main__":
    main()
