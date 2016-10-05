default: all

all: chrome-history

chrome-history:
		python dump.py ~/.config/chromium/Default/History | sybil ingest -table browser_history | sybil digest -table browser_history 

chromium-history:
		python dump.py ~/.config/chromium/Default/History | sybil ingest -table browser_history | sybil digest -table browser_history 

clean:
		rm db/browser_history/ -fr

.PHONY: clean
