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
#if sys.version_info > (3,2):
#    import urllib.request
#else:
#    import urllib
import urllib
from datetime import date, datetime, timedelta
from lxml.html import document_fromstring
from time import sleep
import json, os, logging

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

HISTORY_YEAR_START = 2004
HISTORY_YEAR_END = 2016

logger = logging.getLogger(__name__)
    
def get_date_price_index(target_date = date.today(), index_type = TYPE_SELLING, \
                         price_currency = CURRENCY_TWD):
    """fetch the Gold Passbook price index from BANK OF TAIWAN website
    
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
    logger.debug('open_hour_url: %s' % open_hour_url)
#    if sys.version_info > (3,2):
#        html_content = urllib.request.urlopen(open_hour_url).read()
#    else:
#        html_content = urllib.urlopen(open_hour_url).read()
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
    logger.debug('closed_hour_url: %s' % closed_hour_url)
#    if sys.version_info > (3,2):
#        html_content = urllib.request.urlopen(closed_hour_url).read()
#    else:
#        html_content = urllib.urlopen(closed_hour_url).read()
    html_content = urllib.urlopen(closed_hour_url).read()
    html_doc = document_fromstring(html_content)
    rate_table = html_doc.xpath('/html/body/ul/li[2]/center/table[5]')
    if len(rate_table) > 0 and len(rate_table[0][0]) > 4 and len(rate_table[0]) >= 2:
        for row in rate_table[0][1:]:
            if len(row) == (COL_SELLING+1):
                rate_selling.append(float(row[COL_SELLING].text))
                rate_buying.append(float(row[COL_BUYING].text))
            
    logger.debug('rate_selling: %s' % rate_selling)
    logger.debug('rate_buying: %s' % rate_buying)
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

def get_monthly_price_index(month_date=date.today(),index_type=TYPE_SELLING,price_currency=CURRENCY_TWD):
    """
    Collect every working day price index in the month set by argument ``month_date`` and
    return a list of (date,open,high,low,close)
    
    Args:
        - month_date (datetime.date): any date of target month
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``

    Example::
        
        get_monthly_price_index(datetime.date.today(),
                                    TYPE_SELLING,
                                    CURRENCY_TWD)
    """
    t_date = date(month_date.year,month_date.month,1)
    t_list = []
    while t_date.month == month_date.month and t_date <= date.today():
        t_price_index = get_date_price_index(t_date, index_type, price_currency)
        sys.stdout.write('%s price index: %s\n' % (t_date,str(t_price_index)))
        if t_price_index:
            t_list.append(t_price_index)
        t_date += timedelta(days=1)
        sleep(datetime.now().second % 3)
    return t_list

def save_month_price_index(month_date=date.today(),index_type=TYPE_SELLING,price_currency=CURRENCY_TWD):
    """
    Collect every working day price index in the month set by argument ``month_date`` and
    save into a file ([currenty]-[type]-[%Y%m].json) under directory `history`
    
    Args:
        - month_date (datetime.date): any date of target month
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``

    Return:
        total index count for target month
    
    Example::
        
        save_month_price_index(datetime.date.today(),
                                    TYPE_SELLING,
                                    CURRENCY_TWD)
    """
    t_data = get_monthly_price_index(month_date, index_type, price_currency)
    t_data = [[entry[0].strftime('%Y-%m-%d')]+entry[1:] for entry in t_data]
    t_filename = '%s-%d-%s.json' % (price_currency,index_type,month_date.strftime('%Y%m'))
    with open('./history/%s' % t_filename, 'wb') as t_file:
        t_file.write(json.dumps(t_data))
    return len(t_data)

def save_history_price_index(month_date=date.today(),index_type=TYPE_SELLING,price_currency=CURRENCY_TWD):
    """
    Collect price index data month by month since the month set by argument ``month_date`` and
    save into a file ([currenty]-[type]-[%Y%m].json) under directory `history`
    
    Args:
        - month_date (datetime.date): any date of target month
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``

    Example::
        
        save_history_price_index(datetime.date.today(),
                                    TYPE_SELLING,
                                    CURRENCY_TWD)
    """
    t_date = month_date
    t_count = save_month_price_index(t_date, index_type, price_currency)
    while t_count > 0:
        sys.stdout.write('%s index count %d\n' %(t_date.strftime('%Y-%m') , t_count))
        if t_date.month == 1:
            t_date = date(t_date.year-1, 12, 1)
        else:
            t_date = date(t_date.year, t_date.month-1, 1)
            
        t_count = save_month_price_index(t_date, index_type, price_currency)
    
def load_year_history(year_date=date.today(),index_type=TYPE_SELLING,price_currency=CURRENCY_TWD):
    """
    Collect price index data from self-contained history data under `history` directory 
    for the year set by argument ``year_date`` and return a list of price index
    
    Args:
        - year_date (datetime.date): any date of target year
        - index_type (int): price type; either ``TYPE_SELLING`` or ``TYPE_BUYING``
        - price_currency (str): price currency type; either ``CURRENCY_TWD`` or ``CURRENCY_USD``

    Example::
        
        load_year_history(datetime.date.today(),
                                    TYPE_SELLING,
                                    CURRENCY_TWD)
    """
    t_price_list = []
    for i in range(1,13):
        t_date = date(year_date.year,i,1)
        if t_date > date.today():
            break
        t_filename = '%s-%d-%s.json' % (price_currency,index_type,t_date.strftime('%Y%m'))
        t_filename = os.path.join(os.path.dirname(__file__),'history',t_filename)
        sys.stdout.write('load history file, %s\n' %(t_filename))
        if os.path.exists(t_filename):
            with open(t_filename, 'r') as t_file:
                t_price_list += json.loads(t_file.read())
        else:
            sys.stdout.write('history file not found\n')
            
    t_price_list.sort(key=lambda x: x[0])
    
    return t_price_list


if __name__ == '__main__':
    
    if True:
        #-> test load_year_history
        sys.stdout.write('== test save_history_price_index ==\n')
        t_list = load_year_history(date(2016,2,1))
        print(t_list)
        sys.stdout.write('== test complete ==\n')
        
    
    if False:
        #-> test save_history_price_index
        sys.stdout.write('== test save_history_price_index ==\n')
        save_history_price_index(date(2016,2,1))
        sys.stdout.write('== test complete ==\n')
        
    if False:
        #-> test save_month_price_index
        sys.stdout.write('== test save_month_price_index ==\n')
        t_date = date.today()
        if t_date.month == 1:
            t_date = date(t_date.year-1, 12, 1)
        else:
            t_date = date(t_date.year, t_date.month-1, 1)

        sys.stdout.write('on %s\n' % t_date.strftime('%Y-%m'))
        save_month_price_index(t_date)
        sys.stdout.write('== test complete ==\n')

    if False:
        #-> test get_monthly_price_index
        sys.stdout.write('== test get_monthly_price_index ==\n')
        month_price_list = get_monthly_price_index()
        for entry in month_price_list:
            print(entry)
        sys.stdout.write('== test complete ==\n')
    
    if False:
        sys.stdout.write('== test get_date_price_index ==\n')
        for i in range(6):
            t_date = date.today() - timedelta(days=i)
            print('date %s price index for TWD: %s' % (t_date, get_date_price_index(t_date,index_type = 3)))
            print('date %s price index for USD: %s' % (t_date, get_date_price_index(t_date,index_type = 3, 
                                                                    price_currency = CURRENCY_USD)))
        sys.stdout.write('== test complete ==\n')
        
    