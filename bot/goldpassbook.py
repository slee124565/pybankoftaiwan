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

import urllib2
import sys
from datetime import date, timedelta
from lxml.html import document_fromstring

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

VERBOSE = True
    
def get_date_price_index(target_date = date.today(), index_type = TYPE_SELLING, \
                         price_currency = CURRENCY_TWD):
    """read the Gold Passbook price index from BANK OF TAIWAN via internet
    
    Args:
        - target_date (datetime.date): target date for the price index 
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``
    
    Returns:
        The price index tuple (date,open,high,low,close)
    """
    if (not type(target_date) is date) or (not price_currency in [CURRENCY_TWD,CURRENCY_USD]):
        raise ValueError('argument target_date should be type datetime.date')
    
    rate_selling = []
    rate_buying = []
    
    #-> read rate for open hour
    open_hour_url = RATE_URL.format(Ymd = target_date.strftime('%Y%m%d'),
                                    closed = '0',
                                    currency = price_currency)
    html_content = urllib2.urlopen(open_hour_url).read()
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
    html_content = urllib2.urlopen(closed_hour_url).read()
    html_doc = document_fromstring(html_content)
    rate_table = html_doc.xpath('/html/body/ul/li[2]/center/table[5]')
    if len(rate_table) > 0 and len(rate_table[0][0]) > 4 and len(rate_table[0]) >= 2:
        for row in rate_table[0][1:]:
            if len(row) == (COL_SELLING+1):
                rate_selling.append(float(row[COL_SELLING].text))
                rate_buying.append(float(row[COL_BUYING].text))
            
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

def _print_out(text):
    if VERBOSE:
        sys.stdout.write(text + '\n')

if __name__ == '__main__':
    print('today price index for TWD:', get_date_price_index(index_type = 3))
    print('today price index for USD:', get_date_price_index(index_type = 3, price_currency = CURRENCY_USD))
    
    t_date = date.today() + timedelta(days=1)
    print('tommorrow price index for TWD:', get_date_price_index(target_date = t_date,
                                                                 index_type = 3))
    print('tommorrow price index for USD:', get_date_price_index(target_date= t_date,
                                                                 index_type = 3, price_currency = CURRENCY_USD))
    t_date = date.today() - timedelta(days=1)
    print('yesterday price index for TWD:', get_date_price_index(target_date = t_date,
                                                                 index_type = 3))
    print('yesterday price index for USD:', get_date_price_index(target_date= t_date,
                                                                 index_type = 3, price_currency = CURRENCY_USD))
