#!/usr/bin/env python

"""
.. moduleauthor:: Lee Shiueh <lee.shiueh@gmail.com>

goldpassbook: a Python module provide BANK OF TAIWAN Gold Passbook 
price index information
"""
__author__   = 'Lee Shiueh'
__email__    = 'lee.shiueh@gmail.com'
__url__      = 'https://github.com/slee124565/pybankoftaiwan/tree/master/bot/goldpassbook'
__license__  = 'Apache License, Version 2.0'

import sys
if sys.version_info > (3,2):
    import urllib.request
else:
    import urllib
from datetime import date, datetime, timedelta
from lxml.html import document_fromstring
from time import sleep

#####################
## Named constants ##
#####################

TYPE_SELLING = 1
"""Constant for ``get_date_price_index`` function argument ``index_type``. 
Means the type of bank selling price"""

TYPE_BUYING = 2
"""Constant for ``get_date_price_index`` function argument ``index_type``. 
Means the type of bank buying price"""

CURRENCY_TWD = 'TWD'
"""Constant for ``get_date_price_index`` function argument ``price_currency``. 
Means the type of price currency"""

CURRENCY_USD = 'USD'
"""Constant for ``get_date_price_index`` function argument ``price_currency``. 
Means the type of price currency"""

RATE_URL = 'http://rate.bot.com.tw/Pages/UIP005/UIP00511.aspx?\
lang=zh-TW&whom=GB0030001000&date={Ymd}&afterOrNot={closed}&curcd={currency}'

COL_BUYING = 3
COL_SELLING = 4

VERBOSE = False
    
def get_date_price_index(target_date = date.today(), index_type = TYPE_SELLING, \
                         price_currency = CURRENCY_TWD):
    """read the Gold Passbook price index from BANK OF TAIWAN via internet
    
    Args:
        - target_date (datetime.date): target date for the price index 
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``
    
    Returns:
        The price index tuple (date,open,high,low,close)
        
    Example::
        
        today,open,high,low,close = get_date_price_index(
                                            datetime.date.today(),
                                            TYPE_SELLING,
                                            CURRENCY_TWD)
    """
    if (not type(target_date) is date) or (not price_currency in [CURRENCY_TWD,CURRENCY_USD]):
        raise ValueError('argument target_date should be type datetime.date')
    
    rate_selling = []
    rate_buying = []
    
    #-> read rate for open hour
    open_hour_url = RATE_URL.format(Ymd = target_date.strftime('%Y%m%d'),
                                    closed = '0',
                                    currency = price_currency)
    _print_out('open_hour_url: %s' % open_hour_url)
    if sys.version_info > (3,2):
        html_content = urllib.request.urlopen(open_hour_url).read()
    else:
        html_content = urllib.urlopen(open_hour_url).read()
    html_doc = document_fromstring(html_content)
    rate_table = html_doc.xpath('/html/body/ul/li[2]/center/table[5]')
    if len(rate_table) > 0 and len(rate_table[0][0]) > 4 and len(rate_table[0]) >= 2:
        for row in rate_table[0][1:]:
            if len(row) == (COL_SELLING+1):
                rate_selling.append(float(row[COL_SELLING].text))
                rate_buying.append(float(row[COL_BUYING].text))

    #-> read rate for closed hour
    closed_hour_url = RATE_URL.format(Ymd = target_date.strftime('%Y%m%d'),
                                      closed = '1',
                                      currency = price_currency)
    _print_out('closed_hour_url: %s' % closed_hour_url)
    if sys.version_info > (3,2):
        html_content = urllib.request.urlopen(closed_hour_url).read()
    else:
        html_content = urllib.urlopen(closed_hour_url).read()
    html_doc = document_fromstring(html_content)
    rate_table = html_doc.xpath('/html/body/ul/li[2]/center/table[5]')
    if len(rate_table) > 0 and len(rate_table[0][0]) > 4 and len(rate_table[0]) >= 2:
        for row in rate_table[0][1:]:
            if len(row) == (COL_SELLING+1):
                rate_selling.append(float(row[COL_SELLING].text))
                rate_buying.append(float(row[COL_BUYING].text))
            
    _print_out('rate_selling: %s' % rate_selling)
    _print_out('rate_buying: %s' % rate_buying)
    #-> get quote date quotation
    if len(rate_selling) > 0:
        index_selling = [target_date, rate_selling[0], max(rate_selling), 
                         min(rate_selling),rate_selling[-1]]
    else:
        index_selling = None
    if len(rate_buying) > 0:
        index_buying = [target_date, rate_buying[0], max(rate_buying), 
                        min(rate_buying),rate_buying[-1]]  
    else:
        index_buying = None
     
    #-> return value according to argument quote_type
    if index_type == TYPE_SELLING:
        return index_selling
    if index_type == TYPE_BUYING:
        return index_buying
    return (index_selling,index_buying)

def save_price_index_year_history(date_before = date.today(), index_type = TYPE_SELLING, \
                         price_currency = CURRENCY_TWD):
    """read the year of Gold Passbook price index from BANK OF TAIWAN via internet 
    and save to subdirectory `history` with filename format {yyyy}.json
    
    Args:
        - date_before (datetime.date): read the price index before that date 
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``
    
    Example::
        
        save_price_index_year_history(datetime.date.today(),
                                    TYPE_SELLING,
                                    CURRENCY_TWD)
    """
    index_year_history = []
    t_date = date_before
    t_count = 0
    _print_out('fetch index before date %s' % date_before)
    while t_date >= date(date_before.year,1,1):
        date_index = get_date_price_index(t_date, index_type, price_currency)
        if not date_index is None:
            index_year_history.append(date_index)
        t_count += 1
        _print_out(date_index)
        t_date -= timedelta(days=1)
        sleep(datetime.now().second % 3)
        if t_count > 14:
            break
    pass

def _print_out(text):
    if VERBOSE:
        sys.stdout.write(str(text) + '\n')

if __name__ == '__main__':
    VERBOSE = True
    save_price_index_year_history()
    '''
    for i in range(6):
        t_date = date.today() - timedelta(days=i)
        print('date %s price index for TWD: %s' % (t_date, get_date_price_index(t_date,index_type = 3)))
        print('date %s price index for USD: %s' % (t_date, get_date_price_index(t_date,index_type = 3, 
                                                                price_currency = CURRENCY_USD)))
    '''
        
    