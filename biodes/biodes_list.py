##########################################################################
# Copyright (C) 2009 - 2014 Huygens ING & Gerbrandy S.R.L.
# 
# This file is part of bioport.
# 
# bioport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
##########################################################################

#
#
#
#import re, types
from lxml import etree
#from lxml.etree import Element, SubElement
#from urllib import urlopen
#from xml.sax.saxutils import unescape

from biodes import BioDesDoc

class BioDesList:
    __version__ = '1.0'

    def __init__(self):
        self.root =  None

    def from_element(self, element):
        self.root =element
        return self

    def from_document(self, document):
        self.root = etree.fromstring(document)
        return self
         
    def from_url(self, url):
        parser = etree.XMLParser(no_network=False)
        self.root = etree.parse(url, parser)
        return self

    def get_biodes_documents(self):
        for url in self.root.xpath('//a/@href'):
            yield BioDesDoc().from_url(url)
