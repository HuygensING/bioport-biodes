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
