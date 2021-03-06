#!/usr/bin/python    

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


import os
import unittest
from lxml import etree
from  biodes import Name, is_url, is_date, BioDesDoc, create_xml,  parse_list, parse_document, BDException

this_dir = os.path.dirname(__file__)

class BiodesTestCase(unittest.TestCase):
    kw = {
          'url_biografie':'http://www.gerbrandy.com/bio',
          'url_publisher':'http://www.gerbrandy.com',
          'naam_publisher':'Website van Jelle',
          'titel_biografie':'Bio van Jelle',
          'naam':'Jelle Gerbrandy',
          }
 
    def create_element(self, **args):
        kw = {
                'url_biografie':'http://www.gerbrandy.com/bio',
                'url_publisher':'http://www.gerbrandy.com',
                'naam_publisher':'Website van Jelle',
                'titel_biografie':'Bio van Jelle',
                'naam':'Jelle Gerbrandy',
            }
        kw.update(args)
        s = create_xml(**kw)
        return etree.fromstring(s)
    
 
    def test_create_xml(self):
        create_element = self.create_element 

        #should raise an error if no argument are given         
        self.assertRaises(Exception, create_xml) 
        url = 'file:///%s' % os.path.join(this_dir, 'biodes10_minimal.xml')
        BioDesDoc().from_url(url)
        
        #minimale informatie
        biodes = create_element()

        self.assertEqual(biodes.tag, 'biodes')
        self.assertEqual(biodes.xpath('//publisher/ref')[0].attrib['target'], 'http://www.gerbrandy.com')
        self.assertEqual(biodes.xpath('//publisher/name')[0].text, 'Website van Jelle')
        self.assertEqual(biodes.xpath('//fileDesc/ref')[0].attrib['target'], 'http://www.gerbrandy.com/bio')
        self.assertEqual(biodes.xpath('//fileDesc/title')[0].text, 'Bio van Jelle')
        self.assertEqual(biodes.xpath('//person/persName')[0].text, 'Jelle Gerbrandy')
#        self.assertEqual(biodes.xpath('//text')[0].text, 'tekst van de biografie')

        #Namen
        biodes = create_element(
            naam='Jelle Gerbrandy',
            geslachtsnaam='Gerbrandy',
            )

        self.assertEqual(biodes.xpath('//person/persName/name[@type="geslachtsnaam"]/text()')[0], 'Gerbrandy')
        biodes = create_element(
            geslachtsnaam='Gerbrandy',
            )

        self.assertEqual(biodes.xpath('//person/persName/name[@type="geslachtsnaam"]/text()')[0], 'Gerbrandy')
        self.assertRaises(BDException, create_element, naam='x', geslachtsnaam='z')
        biodes = create_element(
            naam=None,
            prepositie = 'a',
            voornaam = 'b', 
            intrapositie = 'c',
            geslachtsnaam =  'd',
            postpositie = 'e',
            )
        tagged_name = etree.tostring(biodes.xpath('//persName')[0]).strip()
        expected_result = '<persName><name type="prepositie">a</name> <name type="voornaam">b</name> <name type="intrapositie">c</name> <name type="geslachtsnaam">d</name> <name type="postpositie">e</name></persName>'

        biodes = create_element(
            namen = ['Jan K.', ('', 'Jan', '', 'K.', ''), ('dr.','Jan', 'van', 'K', 'graaf van X')]
            )

        self.assertEqual(tagged_name, expected_result, '\n%s|\n%s|\n' % (tagged_name, expected_result))
#       assert 0, etree.tostring(biodes)

        #kijk of alle elementen worden opgepikt
        biodes = create_element(illustraties = ['http://www.gerbrandy.com/p/1'])
        biodes = create_element(auteur = 'pietje')
        biodes = create_element(geboortedatum_tekst = 'pietje')
        biodes = create_element(sterfdatum_tekst = 'pietje')
        biodes = create_element(tekst = 'tekst van de biogafie')

        #hoe naam en geslachtnaam interageren
        biodes = create_element(naam = 'voornaam achternaam nogwat', geslachtsnaam='achternaam')
        persname = biodes.xpath('//persName')[0]
        result = '<persName>voornaam <name type="geslachtsnaam">achternaam</name> nogwat</persName>'
        self.assertEqual(etree.tostring(persname).strip(), result)


    def test_set_value(self):
        doc = BioDesDoc().from_element(self.create_element())
        
        def test_round_trip(**args):
            doc.set_value(**args)
            for k in args:
                self.assertEqual(doc.get_value(k) or '', args[k], '%s ==> %s\n%s' % (k, args[k], doc.to_string()))
            #test the round trip twice
            for k in args:
                self.assertEqual(doc.get_value(k) or '', args[k], '%s ==> %s\n%s' % (k, args[k], doc.to_string()))
        
        test_round_trip(naam_publisher='abcdefg')
        test_round_trip(url_biografie='http://abcdefg')
        test_round_trip(url_publisher='http://abcdefg')
        test_round_trip(geboortedatum='2000-01-01')
        test_round_trip(sterfdatum='2000-01-02')
        test_round_trip(bioport_id=['12345678'])
        
        test_round_trip(geboortedatum='')
        test_round_trip(sterfdatum='')
        test_round_trip(geboortedatum_tekst='')
        
        test_round_trip(geslacht='1')
        test_round_trip(geslacht='2')
        test_round_trip(geslacht='')
        
        test_round_trip(tekst='some tekst')
        test_round_trip(tekst='some tekst2')
        
        #TEST ALSO ENGLISCH VALUES
        test_round_trip(name_publisher='abcdefg')
        test_round_trip(url_biography='http://abcdefg')
        test_round_trip(url_publisher='http://abcdefg')
        test_round_trip(birth_date='2000-01-01')
        test_round_trip(death_date='2000-01-02')
        
        test_round_trip(birth_date='')
        test_round_trip(death_date='')
        test_round_trip(birth_date_text='')
        
        test_round_trip(sex='1')
        test_round_trip(sex='2')
        test_round_trip(sex='')
        
        test_round_trip(text='some tekst')
        test_round_trip(text='some tekst2')
        
        
    def test_type_checking(self):
        self.assertTrue(is_url('http://www.inghist.nl'))
        self.assertFalse(is_url('xhttp://www.inghist.nl'))

        #date

        self.assertTrue(is_date('2000'))
        self.assertTrue(is_date('2344'))
        self.assertTrue(is_date('2000-12'))
        self.assertTrue(is_date('2000-12-01'))
        self.assertFalse(is_date('2000-12-1'))
        self.assertFalse(is_date('2000/12/1'))
        self.assertFalse(is_date(''))
        self.assertTrue(is_date('0001'))
        self.assertTrue(is_date('0111'))
        self.assertTrue(is_date('-0011'))
        
    def test_parse_list(self):
        url = os.path.join(this_dir, "list.xml")
        self.assertEqual(len(parse_list(url)), 2)
#        url = "http://magnum.inghist.nl/Onderzoek/Projecten/BWN/biodes/list"
#        self.assertEqual(len(parse_list(url)), 2031)

    def test_parse_document(self):
        url = "biodes02_example.xml"
        url = os.path.join(this_dir, url)
        doc = parse_document(url)
        #see if &lt; has become <
        self.assertEqual(doc['tekst'][0], '<')


        
    def test_analyze_element(self):

        def test_round_trip(k, o, **dict):
            """test a 'round trip': create a biodes doc with 'from_args', and then parse the file using 'to_dict'
            
            k = the key
            o = the expected oubput
            dict : the data used to create the biodes document
            """
            if not dict:
                dict = {k:o}
            el = self.create_element(**dict)
            doc = BioDesDoc().from_element(el)
            dct = doc.to_dict()
            assert dct.has_key(k), doc.to_string()
            assert dct[k] == o, '%s shoudl be "%s", not "%s"\n%s'  % (k, o,  dct[k], doc.to_string())
            
        #we make round trips: creaet an xml string, parse it, extract the content
        test_round_trip('url_publisher', 'http://www.gerbrandy.com')
        test_round_trip('url_biografie', 'http://www.gerbrandy.com?a&b', url_biografie='http://www.gerbrandy.com?a&b')
        test_round_trip('titel_biografie', 'Bio van Jelle')
        test_round_trip('naam_publisher', 'y',naam_publisher='y' )
        test_round_trip('auteur', ['x'], auteur='x')
        test_round_trip('beroep', ['x'], beroep='x')
        test_round_trip('beroep', ['1', '2'], beroep=['1', '2'])
        test_round_trip('tekst', 'abcdef', tekst='abcdef')
        
        
        test_round_trip('laatst_veranderd', '1922-02-01',laatst_veranderd='1922-02-01' )
        test_round_trip('geboortedatum', '1922-02-01',geboortedatum='1922-02-01' )
        test_round_trip('geboortedatum_tekst', 'y',geboortedatum_tekst='y' )
        test_round_trip('sterfdatum', '1922-02-01',sterfdatum='1922-02-01' )
        test_round_trip('sterfdatum_tekst', 'y',sterfdatum_tekst='y' )
        test_round_trip('geslacht', '1',geslacht='1' )
        test_round_trip('illustraties', ['http://www.domain.nl/1', 'http://www.domain.nl/2'],illustraties=['http://www.domain.nl/1', 'http://www.domain.nl/2'] )
        test_round_trip('illustraties', ['http://www.domain.nl/1'],illustraties='http://www.domain.nl/1' )
        test_round_trip('figures', [('http://www.domain.nl/1', 'This is figure 1')] )
        
#        test_round_trip('namen', [('abc', '', '', '', '', '',  'abc')],naam='abc' )
#        test_round_trip('namen', [('a bc', '', '', '', 'a', '', 'a, bc')],naam='a bc', geslachtsnaam='a' )
#        test_round_trip('namen', [('a', '', '', '', 'a', '', 'a')],naam='', geslachtsnaam='a' )
#        test_round_trip('namen', [('a b c d e', 'a', 'b', 'c', 'd', 'e', 'd, a b c e')],naam='', prepositie='a', voornaam='b', intrapositie='c', geslachtsnaam='d', postpositie='e')
#
        test_round_trip('bioport_id', ['BP-NL-12345'], bioport_id='BP-NL-12345')

    def test_get_names(self):
        url = os.path.join(this_dir, 'bio.xml')
        doc = BioDesDoc().from_url(url)
        self.assertEqual(len(doc.get_names()), 1)
        n = doc.get_names()[0]
        self.assertEqual(u'C. van Heynsbergen', n.volledige_naam())
        
    def test_normalize_name(self):
        s = """<persName> <name type="voornaam">Trijn</name> <name type="intrapositie">van</name> <name type="geslachtsnaam">Leemput</name></persName>"""
        el = etree.fromstring(s)
        self.assertEqual(BioDesDoc().normalize_name(el), 'Leemput, Trijn van')
        s = "<persName>abc</persName>"
        el = etree.fromstring(s)
        self.assertEqual(BioDesDoc().normalize_name(el), 'abc')

    def test_from_args(self):
        kw = {
            'url_biografie':'http://www.gerbrandy.com/bio?a&b',
            'url_publisher':'http://www.gerbrandy.com',
            'naam_publisher':'Website van Jelle',
            'titel_biografie':'Bio van Jelle',
            'naam':'Jelle Gerbrandy',
            'local_id': '123',
        }

        doc = BioDesDoc()
        doc.from_args(**kw)
        self.assertEqual(doc.get_idno(), '123')
    def test_from_dict(self):
        d = self.kw 
        doc = BioDesDoc()
        doc.from_dict(d)
        
    def test_sanity(self):
        doc = BioDesDoc()
        
        assert 'naam' in BioDesDoc.possible_arguments, BioDesDoc.possible_arguments
        assert 'naam' in doc.possible_arguments, doc.possible_arguments
        
    def test_create_some_samples(self, **args):
        #create a very simple file
        kw = {
            'url_biografie':'http://www.gerbrandy.com/bio',
            'url_publisher':'http://www.gerbrandy.com',
            'naam_publisher':'Website van Jelle',
            'titel_biografie':'Bio van Jelle',
            'naam':'Jelle Gerbrandy',
        }

        doc = BioDesDoc()
        doc.from_args(**kw)
        doc.to_file('biodes10_minimal.xml')

        #the most complex case includes everyting
        kw = {
            'bioport_id':'biodesid',   
            'url_biografie':'http://url_van_de_biografie',
            'url_publisher':'http://url_van_de_publisher',
            'titel_biografie':'titel van de biografie',
            'naam_publisher':'naam van depublisher',
#            'naam':'naam',
            'auteur':'auteur',
    #        'beroep':'beroep',
            'prepositie':'prepositie',
            'voornaam':'voornaam',
            'intrapositie':'intrapositie', 
            'geslachtsnaam': 'geslachtsnaam',
            'postpositie':'postpositie',
            'laatst_veranderd':'2009-11-11',   
            'publicatiedatum':'2009-11-11',
            'geboortedatum':'2009-11-11',
            'geboortedatum_tekst':'2009-11-11 in tekst',
            'geboorteplaats':'geboorteplaats',
            'sterfdatum':'2011-11-11',
            'sterfdatum_tekst':'sterfdatum_tekst',
            'sterfplaats':'sterfplaats',
            'geslacht':'1',
            'illustraties':['http://illustratie1.jpg', 'http://illustratie2.jpg'],
            'namen':['Naam1', ('mr.', 'Jan', 'van', 'Voorbeeld', 'Esq.')], 
            'namen_en':['John'],
            'tekst':'tekst van de biografie kan <em>Markup</em> <p>bevatten</p>', 
        }
        doc.from_args(**kw)
        doc._add_event(
            type='marriage',
            when='1901-12-12',
            text='getrouwd met marietje',
        )
        doc.add_state(
            type='occupation',
            frm='1940', 
            to='1960',
            text='schilder',
            )
        doc.add_state(
            type='residence',
            frm='1940', 
            to='1960',
            text='Amsterdam',
            )

        doc.add_state(
            type='claim_to_fame',
            text='Superbekende persoon!',
            )

        doc.add_state(
            type='occupation',
            frm='1940', 
            to='1960',
            text='schilder',
            place="Amsterdam",
            )
    
        doc.to_file('biodes10_maximal.xml')
        
    def test_to_dict(self):
        doc = BioDesDoc()
        doc.from_url(os.path.join(this_dir, 'bio.xml'))
        d = doc.to_dict()
        assert 'geboortedatum' in d, d
        assert doc.get_value('geboortedatum')
        self.assertEqual(type(doc.get_value('geboortedatum')), type(u''))
        
    def test_get_value(self):
        doc = BioDesDoc()
        doc.from_url(os.path.join(this_dir, 'bio.xml'))
        value = [n.volledige_naam() for n in doc.get_value('namen')]
        should_be = ['C. van Heynsbergen']
        self.failUnlessEqual(value, should_be)
    
    def test_replace_name(self):
        doc = BioDesDoc().from_xml(self.create_element())
        naam = Name('Pietje Een')
        doc._add_a_name(naam)
        naam = Name('Pietje Twee')
        doc._add_a_name(naam)
        self.assertEqual(len(doc.get_names()), 3)
        
        new_naam = Name('Newt Newman')
        self.assertEqual(new_naam.to_string(),
            u'<persName>Newt Newman</persName>') 
        doc._replace_name(new_naam, 1)
        self.assertEqual(doc.get_names()[1].to_string(), new_naam.to_string())
        
    def test_remove_name(self):
        doc = BioDesDoc().from_xml(self.create_element())
        naam = Name('Pietje Een')
        doc._add_a_name(naam)
        naam = Name('Pietje Twee')
        doc._add_a_name(naam)
        self.assertEqual(doc.get_names()[2].volledige_naam(), 'Pietje Twee', doc.get_names() )
        self.assertEqual(len(doc.get_names()), 3)
    
        doc.remove_name(1)
        self.assertEqual(len(doc.get_names()), 2)
        self.assertEqual(doc.get_names()[1].volledige_naam(), 'Pietje Twee', doc.get_names() )
                
        
    def test_read_write_events(self):
        doc = BioDesDoc().from_xml(self.create_element())
        doc.add_or_update_event(type='a', when="2009", notBefore="2010", notAfter="2011", date_text="2012", place="asd", place_id="-12345")
        events = doc.get_events(type='a')
        self.assertEqual(len(events), 1)
        e = events[0]
        self.assertEqual(e.get('when'), '2009')
        self.assertEqual(e.get('notBefore'), '2010')
        self.assertEqual(e.get('notAfter'), '2011')
        self.assertEqual(e.find('date').text, '2012')
        self.assertEqual(e.find('place').text, 'asd')
        self.assertEqual(e.find('place').get('key'), '-12345')
        doc.add_or_update_event(type='a', date_text='')
        self.assertEqual(e.find('date'), None)
        doc.add_or_update_event(type='a', place='')
        self.assertEqual(e.find('place').text, '')
        doc.add_or_update_event(type='a', place_id='', place='')
        self.assertEqual(e.find('place').get('key'), '')
        
    def test_read_write_states(self):    
        doc = BioDesDoc().from_xml(self.create_element())
        doc.add_or_update_state(type='floruit', frm="1900", to="1910", place='Zohar', place_id='1')
        state = doc.get_state(type='floruit')
        self.assertEqual(state.get('from'), '1900')
        self.assertEqual(state.get('to'), '1910')
        self.assertEqual(state.get('type'), 'floruit')
        self.assertEqual(state.find('place').text, 'Zohar')
        self.assertEqual(state.find('place').get('key'), '1')
        doc.add_or_update_state(type='floruit', place_id='', place='')
        self.assertEqual(state.find('place').get('key'), '')       
        states = doc.get_states(type='floruit')
        self.assertEqual(states, [state])
        
        doc.add_state(type='occupation', idno="1")
        self.assertEqual(len(states), 1)
        doc.add_state(type='occupation', idno="2")
        doc.add_state(type='occupation', idno="3")
        states = doc.get_states(type='occupation')
        self.assertEqual(len(states), 3)
        doc.remove_state(type='occupation', idx=1)
        states = doc.get_states(type='occupation')
        self.assertEqual(len(states), 2)
        self.assertEqual([s.get('idno') for s in states], ['1', '3'])
        
        #remove states by index number
        states = doc.get_states()
        some_state = states[1]
        some_index = some_state.getparent().index(some_state)
        doc.remove_state(idx= some_index)
        self.assertEqual(len(states)-1, len(doc.get_states()))
        
    def test_relations(self):
        doc = BioDesDoc().from_xml(self.create_element())
        doc.add_relation(person="Kwik", relation="partner")
        doc.add_relation(person="Kwek", relation="child")
        doc.add_relation(person="Kwak", relation="father")
        doc.add_relation(person="Donald", relation="mother")
        doc.add_relation(person="Dagobert", relation="parent")
        
        self.assertEqual(doc.get_relation('partner'), ['Kwik'])
        self.assertEqual(doc.get_relation('child'), ['Kwek'])
        self.assertEqual(doc.get_relation('father'), ['Kwak'])
        self.assertEqual(doc.get_relation('mother'), ['Donald'])
        self.assertEqual(doc.get_relation('parent'), ['Dagobert'])

        #make sure we are not reading the other names
        self.assertEqual(len(doc.get_names()), 1)
        
        self.assertEqual(len(doc.get_relations()), 5)
        ls =  [(el_relation.get('name'), el_person[0].text) for (el_relation, el_person) in doc.get_relations()]
        
        self.assertTrue(('child', 'Kwek') in ls, ls)
        
        el_relation, el_person = doc.get_relations()[1]
        type = el_relation.get('name')
        name = el_person[0].text
        index = el_relation.getparent().index(el_relation)
        #see if deleting and re-adding is sane
        doc.remove_relation(index)
        self.assertEqual(len(doc.get_relations()), 4)
        doc.add_relation(person=name, relation=type)
        self.assertEqual(len(doc.get_relations()), 5)
        
        
    def test_add_note(self):
        doc = BioDesDoc().from_xml(self.create_element())
        doc.add_note('text of the note', type='sometype' )

        self.assertEqual(len(doc.get_notes()), 1)
        self.assertEqual(len(doc.get_notes(type='sometype')), 1)
        self.assertEqual(doc.get_notes(type='sometype')[0].text, 'text of the note')
        doc.add_or_update_note('note2', type='sometype')
        self.assertEqual(doc.get_notes(type='sometype')[0].text, 'note2')
    
    
    def test_add_delete_update_reference(self):
        
        doc = BioDesDoc().from_xml(self.create_element())
        self.assertEqual(len(doc.get_references()), 0)
        _ref1 = doc.add_reference(uri='http://someref', text='some text')
        self.assertEqual(len(doc.get_references()), 1)
        _ref2 = doc.add_reference(uri='http://someref2', text='some text2')
        self.assertEqual(len(doc.get_references()), 2)
        index1 = doc.get_references()[0][0]
        index2 = doc.get_references()[1][0]
        doc.remove_reference(index2)
        self.assertEqual(len(doc.get_references()), 1)
        ref1 = doc.update_reference(index=index1, uri='http://somerefx', text='some textx')
        self.assertEqual(len(doc.get_references()), 1)
        index, _ref = doc.get_references()[0]
        self.assertEqual(index, 0)
        self.assertEqual(ref1.get('target'), 'http://somerefx')
        self.assertEqual(ref1.text, 'some textx')

    def test_add_delete_update_extrafield(self):
        
        doc = BioDesDoc().from_xml(self.create_element())
        self.assertEqual(len(doc.get_extrafields()), 0)
        doc.add_extrafield(key='sleutel', value='some value')
        self.assertEqual(len(doc.get_extrafields()), 1)
        doc.add_extrafield(key='sleutel2', value='some value2')
        self.assertEqual(len(doc.get_extrafields()), 2)
        index1 = 0
        index2 = 1 
        doc.remove_extrafield(index2)
        self.assertEqual(len(doc.get_extrafields()), 1)
        ref1 = doc.update_extrafield(index=index1, key='sleuteldifferent', value='different value')
        self.assertEqual(len(doc.get_extrafields()), 1)
        self.assertEqual(ref1.get('target'), 'sleuteldifferent')
        self.assertEqual(ref1.text, 'different value')
        
        #this is what happens when saveing fom the UI
        doc._replace_extrafields([])
        self.assertEqual(len(doc.get_extrafields()), 0)
        doc.add_extrafield(key='key0', value='some value')
        doc.add_extrafield(key='key1', value='some value2')
        self.assertEqual(doc.get_extrafields()[0].get('target'), 'key0')
        self.assertEqual(doc.get_extrafields()[1].get('target'), 'key1')
        doc._replace_extrafields([('key0', 'some value'), ('key1', 'some value2')])
        self.assertEqual(doc.get_extrafields()[0].get('target'), 'key0')
        self.assertEqual(doc.get_extrafields()[1].get('target'), 'key1')
        

        
    def test_add_delete_update_figure(self):
        
        doc = BioDesDoc().from_xml(self.create_element())
        self.assertEqual(len(doc.get_figures()), 0)
        _ref1 = doc.add_figure(uri='http://someref', text='some text')
        self.assertEqual(len(doc.get_figures()), 1)
        _ref2 = doc.add_figure(uri='http://someref2', text='some text2')
        self.assertEqual(len(doc.get_figures()), 2)
        index1 = doc.get_figures()[0][0]
        index2 = doc.get_figures()[1][0]
        doc.remove_figure(index2)
        self.assertEqual(len(doc.get_figures()), 1)
        _ref1 = doc.update_figure(index=index1, uri='http://somerefx', text='some textx')
        self.assertEqual(len(doc.get_figures()), 1)
        index, ill = doc.get_figures()[0]
        self.assertEqual(index, 0)
        self.assertEqual(ill.find('graphic').get('url'), 'http://somerefx')
        self.assertEqual(ill.find('head').text, 'some textx')
        
        
        
        
def test_suite():
    test_suite = unittest.TestSuite()
    tests = [BiodesTestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite 

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
