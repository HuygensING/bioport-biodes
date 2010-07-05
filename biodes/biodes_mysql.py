#text-encoding: utf-8
### This file contains utility functions for saving (parts) of a biodes file in a mysql database
### such as used for bioport
###
###
### proper biodes interfaces (writing to xml, reading from xml) can be foud in biodes.py

import MySQLdb
from biodes import BioDesDoc
from lxml import etree

#def connect(db='bioport', user='jge', passwd='G3rbr@ndy'):
def connect(db='bioport', user='root', passwd=''):
    db = MySQLdb.connect(db=db,user=user,passwd=passwd, 
             charset='utf8', 
             use_unicode=False, #need this to avoid memory leak (cf. http://jjinux.blogspot.com/2008/09/python-debugging-memory-leaks.html)
             )
    return db 

def execute(sql, **args):
    connect(**args).cursor().execute(sql)

class BioDesDocMySQL(BioDesDoc):
    """Extends the BiodesDoc class with methods to write to a mysql database"""
    def __init__(self, **args):
        self.cursor = connect(**args).cursor()

    def mysql_insert(self, biodes_id, source_id, **args):
        """insert the biografie die op 'url' te vinden is

        op url moet een biodes document staan
        returns: id van de geinserte record.
        """
        d = self.to_dict() 
        biodes_document = self.to_string() 
        db = connect(**args)
        #get a cursor
        c = db.cursor()
        #insert into biografie
        sql = """
        insert into biografie (
           id_biografie,
           url_biografie ,
           naam,
           biodes_document,
           sort_key,
           source_id,
           geboortedatum,
           sterfdatum,
           geslacht,
           normalized_name
           )
            values (%s, %s, %s,  %s, %s, %s, %s, %s,%s,%s)
            """ 

        c.execute(sql,  (
            biodes_id,
            d['url_biografie'],
            d['namen'][0].volledige_naam(),
            biodes_document,
            sort_key(d),
            source_id,
            d.get('geboortedatum',None),
            d.get('sterfdatum', None),
            d.get('geslacht', None),
            d['namen'][0][6],
        ))

        c.execute('select last_insert_id()')
        id = c.fetchone()[0]
        self.mysql_biografie_id = id
        self.update_auteurs( d.get('auteur'))
        self.update_beroepen( d.get('beroep'))

        return id



    def mysql_update(self, biodes_id, source_id, **args):
        """
        url: daar is een biodes document te vinden
        returns: de id van eht gevonden document
        """
        d = self.to_dict()
        biodes_document = self.to_string() 

        db = connect(**args)
        c = db.cursor()


        #find the id of the record to insert
        sql ="select id from biografie where id_biografie=%s"
        c.execute(sql, (biodes_id, ))
        r =  c.fetchone()
        if not r:
            raise Exception('No record found with id_biografie="%s"' % biodes_id)
        id = r[0]


        sql = """update biografie set 
            url_biografie=%s, 
            naam=%s, 
            biodes_document=%s,
            sort_key =%s,
            source_id=%s,
            geboortejaar=%s,
            sterfjaar=%s,
            normalized_name=%s,
            geslacht=%s
            where id_biografie=%s"""
        try:
            c.execute(sql,(
                d['url_biografie'],
                d['namen'][0][0], 
                biodes_document, 
                sort_key(d), 
                source_id, 
                d.get('geboortedatum',None),
                d.get('sterfdatum', None),
                d['namen'][0][6],
                d.get('geslacht', None),
                biodes_id,
                ))
        except:
            print 'Something went wroing trying to update this bio:\n %s\n%s\n' % (d, biodes_document)
            raise

        self.mysql_biografie_id = id
        self.update_auteurs( d.get('auteur'))
        self.update_beroepen( d.get('beroep'))



        return id

    def from_mysql(self, id_biografie=None,id=None, **args):
        db = connect(**args)
        c = db.cursor()
        sql = "describe biografie"
        c.execute(sql)
        flds = [r[0] for r in c.fetchall()]
        if id_biografie:
            sql = 'select * from biografie where id_biografie = %s' 
            c.execute(sql, (id_biografie, ))
        elif id:
            sql = 'select * from biografie where id = %s' 
            c.execute(sql, (id, ))
        else:
            raise Exception('Een van de argument url, id is verplicht')

        r = c.fetchone()
        if not r:
            msg = 'Geen biografie gevonden'
            if id:
                msg += ' met id %s' % id
            elif id_biografie:
                msg += ' met id_biografie %s' % id_biografie
            raise Exception(msg)


        d = {}
        for i in range(0, len(flds)):
            k = str(flds[i])
            if k in self.possible_arguments:
                d[k] = r[i]
            if k == 'id':
                self.mysql_biografie_id = r[i] 

        d['auteur'] = self.mysql_get_auteurs()
        d['beroep'] = self.mysql_get_beroepen()
        self.from_dict(d)
        assert self.root

    def mysql_get_beroepen(self):
        c = self.cursor
        result =[]
        c.execute('select beroep_id from relbiografieberoep where biografie_id = %s order by beroep_id', (self.mysql_id(), ))
        for r in c.fetchall():
            c.execute('select naam from beroep where id = %s', (r[0], ))
            result.append(c.fetchone()[0])
        return result

    def mysql_get_auteurs(self):
        c = self.cursor
        result =[]
        c.execute('select auteur_id from relbiografieauteur where auteur_id = %s', (self.mysql_id(), ))
        for r in c.fetchall():
            c.execute('select naam from auteur where id = %s', (r[0], ))
            result.append(c.fetchone()[0])
        return result

    def mysql_delete(self):
        c = self.cursor
        id = self.mysql_id()
        self.delete_auteurs()
        self.delete_beroepen()
        sql = 'delete from biografie where id = %s' 
        c.execute(sql, (id, ))
   
#    def mysql_id(self):
#        if not getattr(self, 'mysql_biografie_id', None):
#            try:
#                id_biografie =self.to_dict()['id_biografie']
#            except KeyError:
#                raise Exception(str(self.to_dict().keys()))
#            sql = 'select id from biografie where id_biografie = %s' 
#            c.execute(sql, (id_biografie, ))
#            self.mysql_biografie_id = c.fetchone()[0]
#        return self.mysql_biografie_id

    def update_auteurs(self, auteurs):
        c = self.cursor
        id_biografie = self.mysql_biografie_id
        if not auteurs: auteurs = []
        sql_select_auteur = "select id, naam from auteur where naam=%s"   
        sql_insert_auteur = """ 
            insert into auteur (
                naam)
                values (%s)
                """ 
        sql_insert_relbiografieauteur = """
            insert into relbiografieauteur (biografie_id, auteur_id) values (%s, %s)
            """

        self.delete_auteurs()

        for auteur in auteurs: 
            c.execute(sql_select_auteur, (auteur, ))
            ls = c.fetchall()
            if ls:
                id_auteur = ls[0][0]
            else:
                c.execute(sql_insert_auteur, (auteur,))
                c.execute('select last_insert_id()')
                id_auteur = c.fetchone()[0]
            c.execute(sql_insert_relbiografieauteur, (id_biografie, id_auteur))    

    def delete_auteurs(self):
        c = self.cursor
        id_biografie = self.mysql_biografie_id
        #delete all auteurs die bij deze biografie horen
        c.execute('delete from relbiografieauteur where biografie_id = %s' , (id_biografie,))

        c.execute("""delete b from auteur as b
   left join relbiografieauteur as r
    on b.id=r.auteur_id 
where auteur_id is null """)

    def update_beroepen(self, beroepen):
        c = self.cursor
        id_biografie = self.mysql_biografie_id
        if not beroepen: beroepen = []
        sql_select_beroep = "select id, naam from beroep where naam=%s"   
        sql_insert_beroep = """ 
            insert into beroep (
                naam)
                values (%s)
                """ 
        sql_insert_relbiografieberoep = """
            insert into relbiografieberoep (biografie_id, beroep_id) values (%s, %s)
            """
        self.delete_beroepen()
        for beroep in beroepen: 
            c.execute(sql_select_beroep, (beroep, ))
            ls = c.fetchall()
            if ls:
                id_beroep = ls[0][0]
            else:
                c.execute(sql_insert_beroep, (beroep,))
                c.execute('select last_insert_id()')
                id_beroep = c.fetchone()[0]
            c.execute(sql_insert_relbiografieberoep, (id_biografie, id_beroep))    


    def delete_beroepen(self):
        c = self.cursor
        #delete all beroepen die bij deze biografie horen
        c.execute('delete from relbiografieberoep where biografie_id = %s' , (self.mysql_id(),))
        c.execute("""delete b from beroep as b
   left join relbiografieberoep as r
    on b.id=r.beroep_id 
where beroep_id is null """)



def insert_or_update_biografie(url, source_id, **args):
    id_biografie = url
    if get_biografie(id_biografie=id_biografie):
        return update_biografie(url, source_id, **args)
    else:
        return insert_biografie(url, source_id, **args)

   

def get_biografie(id_biografie=None,id=None, **args):
    db = connect(**args)
    c = db.cursor()
    sql = "describe biografie"
    c.execute(sql)
    flds = [r[0] for r in c.fetchall()]
    if id_biografie:
        sql = 'select * from biografie where id_biografie = %s' 
        c.execute(sql, (id_biografie, ))
    elif id:
        sql = 'select * from biografie where id = %s' 
        c.execute(sql, (id, ))
    else:
        raise Exception('Een van de argument url, id is verplicht')

    r = c.fetchone()
    if not r:
        return
    d = {}
    for i in range(0, len(flds)):
        d[flds[i]] = r[i]

    return d



def sort_key(d):
    #XXX bij gelijke namen: sorteren op leefjaren
    #XXX normaliseer diacritische tekens!
    #is er een achternaam bekend?
    return d['namen'][0].sort_key()
#    if d['namen'][0].sort_key:
#        #achternaam + voornaam + TUSSENVOEGSELS + normalized_name
#        sort_key = '%s_%s_%s_%s' % (d['namen'][0][4] , d['namen'][0][2]  , d['namen'][0][3], d['namen'][0][6] )
#    else:
#        sort_key = d['namen'][0][0] 
#    
#    sort_key = sort_key.strip()
#    sort_key += d.get('geboortedatum', '') 
#    sort_key += d.get('sterfdatum', '')
#    for i, o in [
#        ('&auml;', u'ä'),
#        ('&euml;', u'ë'),
#        ('&eacute;', u'é'),
#        ('&uuml;', u'ü'),
#        ('&ouml;', u'ö'),
#
#        ]:
#        sort_key.replace(i, o)
#
#    return sort_key


def insert_biografie(url, source_id, **args):
    """insert the biografie die op 'url' te vinden is

    op url moet een biodes document staan
    returns: id van de geinserte record.
    """
    doc = BioDesDocMySQL()
    doc.from_url(url)
    return doc.mysql_insert(biodes_id=url, source_id=source_id, **args)

def update_biografie(url, source_id, **args):
    """
    url: daar is een biodes document te vinden
    returns: de id van eht gevonden document
    """
    doc = BioDesDocMySQL()
    doc.from_url(url)
    return doc.mysql_update(biodes_id=url,source_id=source_id, **args)   

def delete_biografie(id_biografie=None, id=None, **args):
    doc = BioDesDocMySQL(**args)
    doc.from_mysql(id_biografie=id_biografie, id=id)
    doc.mysql_delete()

def delete_biografien(source_id, **args):
    db = connect(**args)
    c = db.cursor()
    sql = 'select id from biografie where source_id = %s' 
    c.execute(sql, (source_id, ))
    for r in c.fetchall():
        delete_biografie(id=r[0]) 
    db.close()

