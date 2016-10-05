default: all

all: chrome-history chromium-history

chrome-history:
		python dump.py ~/.config/google-chrome/Default/History | sybil ingest -table browstats && sybil digest -table browstats 

chromium-history:
		python dump.py ~/.config/chromium/Default/History | sybil ingest -table browstats && sybil digest -table browstats 

clean:
		rm db/browstats/ ~/.config/browstats/ -fr

.PHONY: clean
