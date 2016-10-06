DUMP_CHROME_CMD=python dump_browser.py
DUMP_FIREFOX_CMD=${DUMP_CHROME_CMD}
FIREFOX_FILES=$(shell find "${HOME}/.mozilla/" -iname places.sqlite)
HIST_FILE=""
TABLE=browstats
SYBIL_BIN=${HOME}/go/bin/sybil
INGEST_CMD=${SYBIL_BIN} ingest -table ${TABLE}
DIGEST_CMD=${SYBIL_BIN} digest -table ${TABLE}
CHROME_ANDROID_HISTORY=.history.android_chrome.db

default: all

all: chrome-history chromium-history android-chrome-history

chrome-history: export HIST_FILE=${HOME}/.config/google-chrome/Default/History
chrome-history:
		${DUMP_CHROME_CMD} ${HIST_FILE} --chrome | ${INGEST_CMD} && ${DIGEST_CMD}

chromium-history: export HIST_FILE=${HOME}/.config/chromium/Default/History
chromium-history:
		${DUMP_CHROME_CMD} ${HIST_FILE} --chrome | ${INGEST_CMD} && ${DIGEST_CMD}

firefox-history: 
		${DUMP_FIREFOX_CMD} ${FIREFOX_FILES} --firefox | ${INGEST_CMD} && ${DIGEST_CMD}

pull-adb:
		adb root
		adb pull /data/data/com.android.chrome/app_chrome/Default/History ${CHROME_ANDROID_HISTORY}

android-chrome-history: pull-adb
android-chrome-history: export HIST_FILE=${CHROME_ANDROID_HISTORY}
android-chrome-history:
	${DUMP_CHROME_CMD} ${HIST_FILE} --chrome | ${INGEST_CMD} && ${DIGEST_CMD}

clean:
		rm db/browstats/ ${HOME}/.config/browstats/ ${CHROME_ANDROID_HISTORY} -fr

.PHONY: clean
