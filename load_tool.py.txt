#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script downloads information about all games from www.somesite.ru
and save data to file in csv format.

Usage:
    load_tool.py [--th=<thread_count>] [--pc=<page_count>] [--of=<output_file>] [--oc=<catalog_file>]

Options:
    --th=<thread_count> Count of working threads [ default: 1 ].
    --pc=<page_count>   Count of page to download [ default: 69 ].
    --of=<output_file>  Output file name [ default: data.csv ].
    --oc=<catalog_file>  Output file name for catalog [ default: None ].
"""

from BeautifulSoup import BeautifulSoup
import requests
import re
import datetime
from multiprocessing import Pool
import sys
from docopt import docopt
from clint.textui import progress


date = datetime.datetime.now()
date_str = unicode(date.strftime("%Y.%m.%d"))

price_re = re.compile('(\d{1,}\s+)?\d{2,}(\.\d{1,})?')
def load_game_info(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            raise ValueError('Staus code: %s'%r.status_code)

        soup = BeautifulSoup(r.text)
        name = soup.find(id='pagetitle').text

        price = u'nan'
        price_tag = soup.find('div',{'class':'item_current_price'})
        if  price_tag:
            m = price_re.search(price_tag.text)
            if m:
                price = u''.join(m.group(0).split())


        quant_limit = u'nan'
        quant_limit_tag = soup.find('p', id=re.compile('quant'))
        if quant_limit_tag:
            quant_limit = re.sub("\D", "", quant_limit_tag.text)

        is_leader = len([ tag for tag in soup.findAll('dt') if u'Лидер' in tag.text ])
        is_recommended = len([ tag for tag in soup.findAll('dt') if u'Теория игр рекомендует' in tag.text ])

        return {'status': True, 'data': {'date':date_str, 'name':(name), 'price':(price),
                    'count':(quant_limit), 'is_leader':unicode(is_leader),
                    'is_recommended':unicode(is_recommended)} }
    except Exception as ex:
        return {'status': False, 'data': "%s can't load %s" % (url,str(ex)) }

def get_urls_from_page(page_num):
    try:
        r = requests.get('http://www.teo'+'games.ru',params={'PAGEN_1':page_num})
        if r.status_code != 200:
            raise ValueError('Staus code: %s'%r.status_code)
        soup = BeautifulSoup(r.text)
        return {'status': True, 'data': [ tag['href'] for tag in soup('a',{'class':'bx_catalog_item_images'}) ] }

    except Exception as ex:
        return {'status': False, 'data': "page %s can't load %s" % (page_num,str(ex)) }

if __name__ == "__main__":
    arguments = docopt(__doc__)
    thread_count = int(arguments['--th'] or '1')
    page_count = int(arguments['--pc'] or '69')
    output_file = arguments['--of'] or 'data.csv'
    catalog_file = arguments['--oc']

    mapf = Pool(thread_count).imap

    urls = set()
    for d, _ in zip( mapf(get_urls_from_page, range(1,page_count+1)),  progress.bar(range(1,page_count+1), 'Searching urls')):
        if d['status']:
            urls.update( [ 'http://www.teo'+'games.ru/' + url for url in  d['data'] ] )
        else:
            sys.stderr.write(d['data'])

    if catalog_file:
        with open(catalog_file,'a') as f:
            for url in urls:
                f.write('\t'.join([date_str, url])+'\n' )

    data = []
    for d, _ in zip( mapf(load_game_info, urls) ,  progress.bar(range(len(urls)),'Loading games info') ):
        if d['status']:
            data.append(d['data'])
        else:
            sys.stderr.write(d['data'])

    with open(output_file,'a') as f:
        for d in data:
            f.write('\t'.join([ d['date'], d['name'],d['price'],d['count'],d['is_leader'],d['is_recommended'] ]).encode('utf-8')+'\n' )
