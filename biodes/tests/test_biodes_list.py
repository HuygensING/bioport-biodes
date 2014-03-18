#!/usr/bin/python    
#encoding=utf-8

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


#import sys
import os
import unittest

from biodes import BioDesList


THISDIR = os.path.split(os.path.abspath(__file__))[0]


class BiodesListTestCase(unittest.TestCase):

    def test_something(self):
        l = BioDesList()
        l.from_url(os.path.join(THISDIR, 'list.xml'))
        l.get_biodes_documents()

        
def test_suite():
    test_suite = unittest.TestSuite()
    tests = [BiodesListTestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite
    
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

