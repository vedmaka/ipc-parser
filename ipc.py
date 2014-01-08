from simplemysql.simplemysql import SimpleMysql
import sys

__author__ = 'vedmaka'
#-*- coding: UTF-8 -*-

import re
import xml.etree.ElementTree as et
import simplemysql
import logging

class IpcParser:
    def __init__(self):
        self.tree = None
        self.entries = []
        self.filename = ''

    def parse(self, filename):
        #we need to remove these tags from xml text:
        #<img src="fig[0-9]?[0-9]?.gif"\/>
        #<rlinkt/>
        #<sub>
        #</sub>
        #<emdash/>
        #<ge/>

        self.filename = filename

        self.tree = et.parse(self.filename)
        '''@type root: Element'''
        root = self.tree.getroot().find('revisionPeriod').find('ipcEdition').find('en').find('staticIpc')

        #Parse xml to entries
        self.entries = []
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
                            item3.children.append(item5)
            self.entries.append(item)
        return self.entries

    def build_indexes(self, host, db, login, password):
        db = SimpleMysql(
            host=host,
            db=db,
            user=login,
            passwd=password
        )
        #Check for table
        res = db.query('SHOW TABLES LIKE "ipc_indexes"')
        tableExists = res.rowcount
        if tableExists == 0:
            print "Creating table.."
            tableCode = '''
CREATE TABLE ipc_indexes (
  id int(11) NOT NULL AUTO_INCREMENT,
  level int(11) DEFAULT NULL,
  word varchar(255) DEFAULT NULL,
  category varchar(512) DEFAULT NULL,
  code varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX UK_ipc_indexes_code (code),
  INDEX UK_ipc_indexes_word (word),
  INDEX IDX_ipc_indexes_level (level)
)
ENGINE = INNODB
AUTO_INCREMENT = 2142
AVG_ROW_LENGTH = 224
CHARACTER SET utf8
COLLATE utf8_general_ci;
'''
            db.query(tableCode)
        else:
            db.query('TRUNCATE TABLE ipc_indexes')
        db.conn.commit()
        #Build indexes
        #LEVEL 2
        # :type entry: ipc.IpcEntry
        for rootItem in self.entries:
            #Skip level 1
            for entry in rootItem.children:
                for titlePart in entry.titleParts:
                    if not len(titlePart.replace("\n", "").replace(u'\xa0', u'')):
                        continue
                    db.insert('ipc_indexes', {
                        "level": 2,
                        "word": titlePart[:255],
                        "code": entry.symbol,
                        "category": entry.title[:235]
                    })
                #level 3
                for entry3 in entry.children:
                    for titlePart in entry3.titleParts:
                        if not len(titlePart.replace("\n", "").replace(u'\xa0', u'')):
                            continue
                        db.insert('ipc_indexes', {
                        "level": 3,
                        "word": titlePart[:255],
                        "code": entry3.symbol,
                        "category": entry3.title[:235]
                        })
                    #level 4
                    for entry4 in entry3.children:
                        for titlePart in entry4.titleParts:
                            if not len(titlePart.replace("\n", "").replace(u'\xa0', u'')):
                                continue
                            db.insert('ipc_indexes', {
                            "level": 5 if entry4.kind == "m" else 4,
                            "word": titlePart[:255],
                            "code": entry4.symbol,
                            "category": entry4.title[:235]
                            })
                        #level 5 wtfwtf
                        '''for entry5 in entry4.children:
                            for titlePart in entry5.titleParts:
                                if not len(titlePart.replace("\n","").replace('\xa0', '')):
                                    continue
                                db.insert('ipc_indexes', {
                                "level": 5,
                                "word": titlePart[:255],
                                "code": entry5.symbol,
                                "category": entry5.title[:235]
                                })'''
        db.conn.commit()
        db.conn.close()
        return True

    def get_indexes(self, host, db, login, password, level=None):
        res = None
        db = SimpleMysql(
            host=host,
            db=db,
            user=login,
            passwd=password
        )
        if level is None:
            res = db.getAll('ipc_indexes')
        else:
            res = db.getAll('ipc_indexes', '*', ("level=%s", [level]))

        ind = []

        if res is None:
            print "No indexes! at level " +str(level)
            sys.exit()
            return ind

        for r in res:
            item = IpcIndex()
            item.id = r.id
            item.level = r.level
            item.word = r.word
            item.code = r.code
            item.category = r.category
            ind.append(item)

        db.conn.commit()
        db.conn.close()
        return ind


class IpcIndex:
    def __init__(self):
        self.id = -1
        self.level = 0
        self.word = ''
        self.code = ''
        self.category = ''


class IpcEntry:

    def __init__(self, xmlElement = None):

        self.kind = ''
        self.symbol = ''
        self.ipcLevel = ''
        self.entryType = ''
        self.lang = ''
        self.priorityOrder = 0
        ''':type parentElement: IpcEntry'''
        self.parentElement = None
        ''':type children: IpcEntry[]'''
        self.children = []
        self.titleParts = []

        if xmlElement is not None:
            self.kind = xmlElement.get('kind', 0)
            self.symbol = xmlElement.get('symbol', 0)
            self.ipcLevel = xmlElement.get('ipcLevel', 0)
            self.entryType = xmlElement.get('entryType', 0)
            self.lang = xmlElement.attrib.get('lang', 0)
            self.priorityOrder = xmlElement.attrib.get('priorityOrder', 0)

            if self.kind == 'i':
                titleParts = xmlElement.findall('./textBody/index/indexEntry/text')
            else:
                titleParts = xmlElement.findall('./textBody/title/titlePart/text')

            for part in titleParts:
                if part.text is not None:
                    v = re.sub(r'<[^>]*?>', '', part.text)
                    v = v.rstrip(' ')
                    self.titleParts.append(v)

            if len(self.titleParts):
                self.title = '; '.join(self.titleParts)
                self.title = self.title[:235]

def replace_chars(stri):
    # remove annoying characters
    chars = {
        '\xc2\x82' : '',        # High code comma
        '\xc2\x84' : '',       # High code double comma
        '\xc2\x85' : '',      # Tripple dot
        '\xc2\x88' : '',        # High carat
        '\xc2\x91' : '',     # Forward single quote
        '\xc2\x92' : '',     # Reverse single quote
        '\xc2\x93' : '',     # Forward double quote
        '\xc2\x94' : '',     # Reverse double quote
        '\xc2\x95' : '',
        '\xc2\x96' : '',        # High hyphen
        '\xc2\x97' : '',       # Double hyphen
        '\xc2\x99' : '',
        '\xc2\xa0' : ' ',
        '\xc2\xa6' : '',        # Split vertical bar
        '\xc2\xab' : '',       # Double less than
        '\xc2\xbb' : '',       # Double greater than
        '\xc2\xbc' : '',      # one quarter
        '\xc2\xbd' : '',      # one half
        '\xc2\xbe' : '',      # three quarters
        '\xca\xbf' : '',     # c-single quote
        '\xcc\xa8' : '',         # modifier - under curve
        '\xcc\xb1' : '',          # modifier - under line
        '\xa0' : ''          # modifier - under line
    }
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, stri)


def replace_chars2(match):
    # remove annoying characters
    chars = {
        '\xc2\x82' : '',        # High code comma
        '\xc2\x84' : '',       # High code double comma
        '\xc2\x85' : '',      # Tripple dot
        '\xc2\x88' : '',        # High carat
        '\xc2\x91' : '',     # Forward single quote
        '\xc2\x92' : '',     # Reverse single quote
        '\xc2\x93' : '',     # Forward double quote
        '\xc2\x94' : '',     # Reverse double quote
        '\xc2\x95' : ' ',
        '\xc2\x96' : '',        # High hyphen
        '\xc2\x97' : '',       # Double hyphen
        '\xc2\x99' : ' ',
        '\xc2\xa0' : ' ',
        '\xc2\xa6' : '',        # Split vertical bar
        '\xc2\xab' : '',       # Double less than
        '\xc2\xbb' : '',       # Double greater than
        '\xc2\xbc' : '',      # one quarter
        '\xc2\xbd' : '',      # one half
        '\xc2\xbe' : '',      # three quarters
        '\xca\xbf' : '',     # c-single quote
        '\xcc\xa8' : '',         # modifier - under curve
        '\xcc\xb1' : '',          # modifier - under line
        '\xa0' : ''          # modifier - under line
    }
    char = match.group(0)
    return chars[char]