#!python3.5

import requests
import glob
from os import path , makedirs
from bs4 import BeautifulSoup
import xml.etree.cElementTree as et
import xml.dom.minidom as md
import unicodecsv as csv

class TmMaker :

    '''
    Read table and prepare TM.
    '''
    
    def __init__(self):
        self.files = glob.glob("*.htm")
                
    def _make_soup( self, file ):
    
        ''' 
        Turns HTML to soup. 
        '''
        
        r_url = file
        soup = BeautifulSoup( open( r_url, encoding='utf-8' ), 'html.parser' )
        return soup
        
    def _get_rows(self, file):
    
        soup = self._make_soup( file )
        tr = soup.findAll('tr')
        return tr
    
    def _get_column(self, file, lang) :
        if lang == 'zh':
            col_num = 1
        elif lang == 'en':
            col_num = 0
        tr = self._get_rows( file )
        rows = []
        for i in tr:
            row = i.findAll('td')[col_num].text.replace( "\n", '' )
            rows.append(row)
        return rows
        
    def _get_pairs(self, file) :
        tr = self._get_rows( file )
        pairs = []
        for r in tr:
            pair = []
            pair.append( r.findAll('td')[0].text.replace( "\n", '' ))
            pair.append( r.findAll('td')[1].text.replace( "\n", '' ))
            pairs.append(pair)
        return pairs
        
    def _make_file(self, file, lang):
        if lang != 'zh' or 'en':
            lang == 'en'
        if not path.exists('zh'):
            makedirs('zh')
        if not path.exists('en'):
            makedirs('en')
        with open ( lang + '/' + file + ".txt", 'ab') as f :
            rows = self._get_column(file, lang)
            for row in rows:
                f.write( row.encode( 'utf-8' ) + "\n".encode( 'utf-8' ) )
        print ( file + ' saved.\n')
    
    def make_xml(self):
        root = et.Element("tmx", attrib={"version":"1.4"})
        file_count = 0
        seg_count = 0
        skip_count = 0
        header = et.SubElement(root, 'header', attrib={
                    'creationtool':"XTmMaker", 
                    'creationtoolversion':"0.1", 
                    'datatype':"PlainText", 
                    'segtype':"sentence", 
                    'adminlang':"en-us",
                    'srclang':"en",
                    'o-tmf':"txt"})
        body = et.SubElement(root, "body")
        for file in self.files :
            pairs = self._get_pairs(file)
            for pair in pairs:
                if len(pair[0]) > 0 and len(pair[1]) > 0 :
                    tu = et.SubElement(body, "tu")
                    tuv_en = et.SubElement(tu, "tuv", attrib={"xml:lang": "en"})
                    tuv_zh = et.SubElement(tu, "tuv", attrib={"xml:lang": "zh-CN"})
                    seg_en = et.SubElement(tuv_en, "segment").text=pair[0]
                    seg_zh = et.SubElement(tuv_zh, "segment").text=pair[1]
                    seg_count += 1
                else:
                    skip_count += 1
            file_count += 1
            print("Processed " + str(file_count) + " files, " + str(seg_count) + " segments in total.\n")
        tree = et.ElementTree(root)
        tree_string = et.tostring(root)
        xml_string = '<?xml version="1.0" encoding="UTF-8" ?><!DOCTYPE tmx SYSTEM "tmx14.dtd">' + tree_string.decode('utf-8')
        xml = md.parseString(xml_string)
        string = xml.toprettyxml()
        with open ('unog.tmx', 'wb') as f:
            f.write(string.encode('utf-8'))
        print ("All tasks completed. " + str(seg_count) + " segments processed, " + str(skip_count) + " segments skipped.\n")
    
    def make_csv(self):
        all_pairs = []
        counter = 0
        for file in self.files : 
            pairs = self._get_pairs(file)
            clean_pairs = []
            for pair in pairs:
                if len(pair[0]) > 0 and len(pair[1]) > 0 :
                    clean_pairs.append(pair)
                    counter += 1
            all_pairs += clean_pairs
        with open ('unog.csv', 'wb') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerows(all_pairs)
        print ('CSV created for ' + str(counter) + " rows.")
    
    def make_tm(self):
        for file in self.files:
            self._make_file(file, 'en')
            self._make_file(file, 'zh')
