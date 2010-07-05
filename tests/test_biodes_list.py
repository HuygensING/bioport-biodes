#! /usr/bin/python    
#encoding=utf-8

import sys
import os
import unittest

from biodes import BioDesList


THISDIR = os.path.split(os.path.abspath(__file__))[0]


class BiodesListTestCase(unittest.TestCase):

    def test_something(self):
        l = BioDesList()
        l.from_url(os.path.join(THISDIR, 'list.xml'))
        l.get_biodes_documents()

        
def test_main():
    test_suite = unittest.TestSuite()
    tests = [BiodesListTestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    unittest.TextTestRunner(verbosity=2).run(test_suite)
    
if __name__=='__main__':
    test_main()


