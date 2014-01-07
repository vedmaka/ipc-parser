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


def createCategory(name, parent):
    category = pywikibot.Page(pywikibot.getSite(), name)
    if not parent:
        category.put("[[Category:IPCT topics]]")
    else:
        category.put("[[Category:" + parent + "]]")

def recursiveCreateCategories(category, parentName):
    """

    :type category: IpcEntry
    """
    if category.kind=="i" or \
            not hasattr(category, 'symbol') or \
            not hasattr(category, 'title'):
        return

    if not category.children:
        createCategory("Category:"+category.symbol + ". " + category.title, parentName)
    else:
        createCategory("Category:"+category.symbol + ". " + category.title, parentName)
        for i in category.children:
            recursiveCreateCategories(i, category.title)

#PHASE 1 - BUILDING CATEGORY PAGES
ipc = IpcParser()
entries = ipc.parse('ipcr.xml')
root = pywikibot.Page(pywikibot.getSite(), "Category:IPCT topics")
root.put("This is core category for all topics in IPCT")
[recursiveCreateCategories(x, "Category:IPCT topics") for x in entries]

#
# #PHASE 2 BUILDING INDEXES and
# ipc.build_indexes('localhost', 'ipc', 'mysql', 'mysql')
# wf = mwclient.Site('en.wikioffuture.org')
#
#
# # PHASE 3 ADDING CATEGORIES TO WIKIPAGE
# page = wf.Pages['Agriculture and Empire in the High-Altitude Atacama Desert']
# pageText = page.edit()
# parsed = mwp.parse(pageText)
# template = parsed.filter_templates()[0]
#
# abstract = template.get('Abstract').value.lower()
#
# indexes = ipc.get_indexes('localhost', 'ipc', 'mysql', 'mysql')
# found = []
#
# for index in indexes:
#     #print 'Trying '+index.word
#     word = index.word.lower()
#     count = abstract.count(word)
#     if not len(word):
#         print "0-WORD!"
#         continue
#     if count:
#         print 'Found index id: ' + str(index.id) + ' ' + str(count) + ' times.'
#         found.append([index, count])
#
# print 'Page will be set with categories:'
# for f in found:
#     print str(f[1]) + ' / ' + f[0].code + ' ' + f[0].category