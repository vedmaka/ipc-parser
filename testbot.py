__author__ = 'ganqqwerty'
import wikipedia as pywikibot
import config
import xml.etree.ElementTree as et
from ipc import IpcEntry
import wikipedia as pywikibot
import config as config

#we need to remove these tags from xml text:
#<img src="fig[0-9]?[0-9]?.gif"\/>
#<rlinkt/>
#<sub>
#</sub>
#<emdash/>
#<ge/>

tree = et.parse('ipcr_test.xml')
'''@type root: Element'''
root = tree.getroot().find('revisionPeriod').find('ipcEdition').find('en').find('staticIpc')

#Parse xml to entries
entries = []
#LEVEL 1 items
for levelOneItem in root:
    item = IpcEntry(levelOneItem)
    levelTwo = levelOneItem.findall("./ipcEntry")
    #LEVEL 2 items
    for levelTwoItem in levelTwo:
        if levelTwoItem.attrib.get('kind', 0) == 't':
            #aAttrib = t, this is text
            #skipping it
            pass
        else:
            #Attrib = c, this is LEVEL2 items
            #Create item for level 2
            item2 = IpcEntry(levelTwoItem)
            item2.parentElement = item
            item.children.append(item2)
            #LEVEL 3 items
            levelThree = levelTwoItem.findall('./ipcEntry[@kind="u"]')
            for levelThreeItem in levelThree:
                item3 = IpcEntry(levelThreeItem)
                item3.parentElement = item2
                item2.children.append(item3)
                #LEVEL 4 items: indexes (single)
                levelFour = levelThreeItem.find('./ipcEntry[@kind="i"]')
                item4 = IpcEntry(levelFour)
                item4.parentElement = item3
                item3.children.append(item4)
                #LEVEL 5 items
                levelFive = levelThreeItem.findall('./ipcEntry[@kind="m"]')
                for levelFiveItem in levelFive:
                    item5 = IpcEntry(levelFiveItem)
                    item5.parentElement = item3
                    item4.children.append(item5)
    entries.append(item)


print "Done!"

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
    if not category.hasChildren():
        createCategory(category.title, parentName)
    else:
        createCategory(category.title, parentName)
        for i in category.children:
            recursiveCreateCategories(i, category.title)

root = pywikibot.Page(pywikibot.getSite(), "Category:IPCT topics")
root.put("This is core category for all topics in IPCT")

entries = []
[recursiveCreateCategories(x, "Category:IPCT topics") for x in entries]


