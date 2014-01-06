import sys

__author__ = 'vedmaka'
#-*- coding: UTF-8 -*-

import mwclient
import mwparserfromhell as mwp
from ipc import IpcParser
from collections import Counter
import re

ipc = IpcParser()
entries = ipc.parse('ipcr.xml')
ipc.build_indexes('localhost', 'ipc', 'mysql', 'mysql')

wf = mwclient.Site('en.wikioffuture.org')
page = wf.Pages['Agriculture and Empire in the High-Altitude Atacama Desert']

pageText = page.edit()
parsed = mwp.parse(pageText)
template = parsed.filter_templates()[0]

abstract = template.get('Abstract').value.lower()

indexes = ipc.get_indexes('localhost', 'ipc', 'mysql', 'mysql')
found = []

for index in indexes:
    #print 'Trying '+index.word
    word = index.word.lower()
    count = abstract.count(word)
    if not len(word):
        print "0-WORD!"
        continue
    if count:
        print 'Found index id: '+str(index.id)+' '+str(count)+' times.'
        found.append([index, count])

print 'Page will be set with categories:'
for f in found:
    print str(f[1])+' / '+f[0].code + ' ' + f[0].category