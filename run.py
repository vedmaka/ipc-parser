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
            recursiveCreateCategories(i, category.symbol + ". " + category.title)

#PHASE 1 - BUILDING CATEGORY PAGES
ipc = IpcParser()
entries = ipc.parse('ipcr.xml')
# root = pywikibot.Page(pywikibot.getSite(), "Category:IPCT topics")
# root.put("This is core category for all topics in IPCT")
# [recursiveCreateCategories(x, "Category:IPCT topics") for x in entries]

#
#PHASE 2 BUILDING INDEXES and
ipc.build_indexes('localhost', 'ipc', 'mysql', 'mysql')
wf = mwclient.Site('dokuwiki.wikivote.ru', '/')

# PHASE 3 ADDING CATEGORIES TO WIKIPAGE #Category: EU Awards
for page in wf.Categories['EU Awards']:

    if page.namespace != 0:
        print "- skipped template: "+page.page_title
        continue

    print "\n\n==Working with page: "+page.page_title+'=='

    pageText = page.edit()
    parsed = mwp.parse(pageText)
    template = parsed.filter_templates()[0]

    #Abstract
    abstract = template.get('Short_description')
    if abstract is None:
        print "[!] No abstract field, skip."
        continue
    abstract = abstract.value.lower()

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
            print 'Found index id: ' + str(index.id) + ' = ' + index.word + ' ' + str(count) + ' times.'
            found.append([index, count])

    print 'Page will be set with categories:'
    for f in found:
        print str(f[1]) + ' / ' + f[0].code + ' ' + f[0].category
        print ("{{#subobject:IPCT categories statistics" +
               "|category = " + f[0].code + '. ' + f[0].category +
               "|occurencies = " + str(f[1]) +
               "|parentPage = " + page.page_title +
               "}}")

sys.exit()


