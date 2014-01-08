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
    additionalText = "This category represents " + \
                     "[http://web2.wipo.int/ipcpub/#refresh=page&notion=scheme&version=20100101&symbol=" \
                     + name.replace('Category:', '').replace('.', '') + " " + name.replace('Category:', '').replace('.', '') + "] topic of International Patent Classification (IPC). \n"
    category = pywikibot.Page(pywikibot.getSite(), name)
    if not parent:
        category.put(additionalText + "[[Category:IPC topics]]")
    else:
        category.put(additionalText + "[[Category:" + parent + "]]")

def recursiveCreateCategories(category, parentName):
    """
    :type category: IpcEntry
    """
    if category.kind == "i" or \
            not hasattr(category, 'symbol') or \
            not hasattr(category, 'title'):
        return

    print category.kind

    if not category.children:
        createCategory("Category:"+category.symbol + ". " + category.title, parentName)
        #print "Category:"+category.symbol + ". " + category.title.encode('utf-8') +' (parent: '+parentName.encode('utf-8')+')'
    else:
        #print "Category:"+category.symbol + ". " + category.title.encode('utf-8') +' (parent: '+parentName.encode('utf-8')+')'
        createCategory("Category:"+category.symbol + ". " + category.title, parentName)
        for i in category.children:
            recursiveCreateCategories(i, category.symbol + ". " + category.title)

#PHASE 1 - BUILDING CATEGORY PAGES
ipc = IpcParser()
#entries = ipc.parse('ipcr.xml')
#root = pywikibot.Page(pywikibot.getSite(), "Category:IPC topics")
#root.put("This is core category for all topics in IPC")
#[recursiveCreateCategories(x, "IPC topics") for x in entries]

#sys.exit()

#
#PHASE 2 BUILDING INDEXES and
#ipc.build_indexes('localhost', 'ipc', 'mysql', 'mysql')

#for ent in entries:
#    if ent.kind == "m":
#        print ent.symbol +'. '+ent.title

#sys.exit()

wf = mwclient.Site('dokuwiki.wikivote.ru', '/')
wf.login('botik', 'q1w2e3r4')

indexes = ipc.get_indexes('localhost', 'ipc', 'mysql', 'mysql')

# PHASE 3 ADDING CATEGORIES TO WIKIPAGE #Category: EU Awards
for page in wf.Categories['EU Awards']:

    if page.namespace != 0:
        print "- skipped template: "+page.page_title
        continue

    print "Working with page: "+page.page_title

    page = wf.Pages['Investigation of a Novel Dew Point Cooling Heat and Mass Exchanger for Air Conditioning of Buildings in Europe']

    pageText = page.edit()

    if '___________IPC MARKER START___________' in pageText:
        print "[!WARNING!] This page already marked"
        continue

    parsed = mwp.parse(pageText)
    parsedTemplates = parsed.filter_templates()

    if not len(parsedTemplates):
        print "No templates!"
        continue

    template = None
    for temp in parsedTemplates:
        if temp.name.matches("EU Awards"):
            template = temp
            break

    if template is None:
        print "No template with given name!"
        continue

    #Abstract

    if not template.has('Short_description'):
        print "No field in template!"
        continue

    abstract = template.get('Short_description')
    if abstract is None:
        print "[!] No abstract field, skip."
        continue
    abstract = abstract.value.lower()

    found = []

    for index in indexes:
        #print 'Trying '+index.word
        word = index.word.lower().replace("\n", "")
        if not len(word):
            print "0-WORD!"
            continue
        count = abstract.count(word)
        if count:
            #print 'Found index id: ' + str(index.id) + ' = ' + index.word + ' ' + str(count) + ' times.'
            found.append([index, count])

    #Group array found by index.category
    newFound = {}
    for iIndex, iCount in found:
        if iIndex.code + '. ' + iIndex.category not in newFound.keys():
            newFound[iIndex.code + '. ' + iIndex.category] = []
        newFound[iIndex.code + '. ' + iIndex.category].append([iIndex, iCount])

    if not len(newFound) or not len(found):
        print "No matches, skip"
        continue

    #print 'Page will be set with categories:'

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

        #print str(occurencies) + '/' + catName

        subobject = ("\n\n{{#subobject:|category = " + catName +
               "|occurencies = " + str(occurencies) +
               "|parentPage = " + page.page_title +
               "}}\n")
        editText += subobject

    for cc in arCats:
        editText += "\n[[Category:"+cc+"]]"
    if mLeader:
        editText += "\n[[Category leader::"+mLeader+"| ]]"

    editText += "\n<!-- ___________IPC MARKER END_________ -->\n"

    #print editText
    page.text = pageText + editText
    page.save()
    sys.exit()

sys.exit()


