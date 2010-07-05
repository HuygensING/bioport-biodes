#! /usr/bin/python    
#encoding=utf-8
import sys,os
from unittest import TestCase, TestSuite, main, makeSuite
from BioDes.biodes import *
from BioDes.biodes_list import BioDesList

this_dir = os.path.split(os.path.abspath(__file__))[0]

class BiodesListTestCase(TestCase):
    def test_something(self):
        l = BioDesList()
        l.from_url(os.path.join(this_dir, 'list.xml'))
        l.get_biodes_documents()
def test_suite():
    return TestSuite((
        makeSuite(BiodesListTestCase),
        ))


if __name__=='__main__':
    main(defaultTest='test_suite')
    

