__author__ = 'ganqqwerty'
#-*- coding: UTF-8 -*-
import wikipedia as pywikibot
import config
import xml.etree.ElementTree as et
from ipc import IpcEntry
import wikipedia as pywikibot
import config as config
import sys
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


print "Done!"
abstract = template.get('Abstract').value.lower()

print [x.title for x in entries]
print [x.title for x in entries[0].children]
print [x.title for x in entries[0].children[0].children]
print [x.title for x in entries[0].children[0].children[0].children]
print [x.title for x in entries[0].children[0].children[0].children[0].children]


def createCategory(name, parent):
    category = pywikibot.Page(pywikibot.getSite(), name)
    if not parent:
        category.put("[[Category:IPCT topics]]")
    else:
        category.put("[[Category:"+parent+"]]")

def recursiveCreateCategories(category, parentName):
    if not category.childen:
        createCategory(category.title, parentName)
    else:
        createCategory(category.title, parentName)
        for i in category.children:
            recursiveCreateCategories(i, category.title)

root = pywikibot.Page(pywikibot.getSite(), "Category:IPCT topics")
root.put("This is core category for all topics in IPCT")

[recursiveCreateCategories(x, "Category:IPCT topics") for x in entries]

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