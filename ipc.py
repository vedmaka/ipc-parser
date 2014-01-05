__author__ = 'vedmaka'
#-*- coding: UTF-8 -*-

import re
import xml.etree.ElementTree


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
                v = re.sub(r'<[^>]*?>', '', part.text)
                v = v.rstrip(' ')
                self.titleParts.append(v)

            if len(self.titleParts):
                self.title = ';'.join(self.titleParts)