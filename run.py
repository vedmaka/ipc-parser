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
#entries = ipc.parse('ipcr.xml')
# root = pywikibot.Page(pywikibot.getSite(), "Category:IPCT topics")
# root.put("This is core category for all topics in IPCT")
# [recursiveCreateCategories(x, "Category:IPCT topics") for x in entries]

#
#PHASE 2 BUILDING INDEXES and
#ipc.build_indexes('localhost', 'ipc', 'mysql', 'mysql')
wf = mwclient.Site('dokuwiki.wikivote.ru', '/')

# PHASE 3 ADDING CATEGORIES TO WIKIPAGE #Category: EU Awards
for page in wf.Categories['EU Awards']:

    if page.namespace != 0:
        print "- skipped template: "+page.page_title
        continue

    print "\n\n==Working with page: "+page.page_title+'=='

    page = wf.Pages['Deterministic Forecasting of Rogue Waves in the Ocean']

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

    #Group array found by index.category
    newFound = {}
    for iIndex, iCount in found:
        if iIndex.code + '. ' + iIndex.category not in newFound.keys():
            newFound[iIndex.code + '. ' + iIndex.category] = []
        newFound[iIndex.code + '. ' + iIndex.category].append([iIndex, iCount])

    print 'Page will be set with categories:'

    editText = "\n<!-- ___________IPC MARKER START___________ -->\n"
    arCats = []
    mLeader = ''
    maxOc = 0
    for catName, ff in newFound.iteritems():
        #ff - grouped by category
        arCats.append(catName)

        occurencies = 0
        for f in ff:
            occurencies += f[1]

        if occurencies > maxOc:
            maxOc = occurencies
            mLeader = catName

        print str(occurencies) + '/' + catName

        subobject = ("\n{{#subobject:IPCT categories statistics" +
               "|category = " + catName +
               "|occurencies = " + str(occurencies) +
               "|parentPage = " + page.page_title +
               "}}\n")
        editText += subobject

    for cc in arCats:
        editText += "\n[[Category:"+cc+"]]"
    if mLeader:
        editText += "\n[[Category leader::"+mLeader+"]]"

    editText += "\n<!-- ___________IPC MARKER END_________ -->\n"

    print editText
    #sys.exit()

sys.exit()


