# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy utilities"""

from settings import *
import json, csv
import logging
import bs4
import re
import codecs

def csvdump(destination, datum, delim = ';', new = True):
    if new:
        dest = open(destination, 'w')
        dest.write(codecs.BOM_UTF8)
    else:
        dest = open(destination, 'a')
    myWriter = csv.writer(dest, delimiter=delim, lineterminator='\n')
    for row in datum:
        row1 = []
        for r in row:
            try: r = r.encode('utf-8')
            except: pass
            row1.append(r)
        myWriter.writerow(row1)
    dest.close()

def csvload(source, delim = ';'):
    sour = open(source, 'r')
    myReader = csv.reader(sour, delimiter=delim, lineterminator='\n')
    worktable = []
    for row in myReader:
        row1 = []
        for element in row:
            try:
                element = element.decode('utf-8')
            except:
                pass
            try:
                element = int(element)
            except:
                try:
                    element = float(element)
                except:
                    pass
            row1.append(element)
        worktable.append(row1)
    return worktable

def jsondump(destination, data_structure):
    jtm = json.dumps(data_structure)
    dest = open(destination, 'w')
    logging.info(u'JSON-dump created: {}'.format(destination))
    dest.write(jtm)
    dest.close()

def jsonload(source):
    sour = open(source, 'r')
    ret_data = json.load(sour)
    sour.close()
    logging.info(u'JSON-dump loaded: {}'.format(source))
    return ret_data

def strip_tags(html):
    soup = bs4.BeautifulSoup('<tree>'+html+'</tree>')
    for tag in soup.findAll(True):
        tag.append(' ')
        tag.replaceWithChildren()
    result = unicode(soup)
    result = re.sub(' +', ' ', result, flags=re.UNICODE)
    result = re.sub(r' ([\.,;:?!])', r'\1', result, flags=re.UNICODE)
    return result.strip()

def strip_spaces(text):
    text = re.sub('\n[ ]+', '\n', text, flags=re.UNICODE)
    while True:
        newtext = text.replace('\n\n', '  ')
        if newtext == text:
            break
        else:
            text = newtext
    text = re.sub('(^\n)|(\n$)', '', text, flags=re.UNICODE)
    text = re.sub('\s\n', ' ', text, flags=re.UNICODE)
    return text

def check_dublicates_by_id(list_of_dicts, check_var):
    retdict = {}
    for element in list_of_dicts:
        retdict[element[check_var]] = element
    return retdict.values()

def check_dublicates_complete(list_of_dicts):
    retdict = []
    for element in list_of_dicts:
        if element not in retdict:
            retdict.append(element)
    return retdict