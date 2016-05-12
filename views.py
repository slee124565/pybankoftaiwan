from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import goldpassbook, httplib, os
from datetime import date, datetime

from models_gae import GoldPassbookModel, GoldPassbookMetaModel, add_passbook_update_task

def gold_passbook_add_update_task(request, p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """Handle Gold Passbook add update task in queue HTTP request"""
    
    if add_passbook_update_task(reverse('datastore_update_task')):
        return HttpResponse('Add Gold Passbook Update Task Success!')
    else:
        return HttpResponse('Add Gold Passbook Update Task Fail!')
    
    
    
def gold_passbook_update_by_date(request, p_date_str,
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """Handle Gold Passbook update price index by date HTTP request"""
    t_date = datetime.strptime(p_date_str,'%Y-%m-%d').date()
    GoldPassbookModel.update_price_index_by_date(t_date, 
                                                 p_index_type, 
                                                 p_currency)
    
    return HttpResponseRedirect(reverse('passbook_year_view', 
                                        kwargs={'p_yyyy': t_date.year}))
    
    
def gold_passbook_year_view(request, p_yyyy = date.today().year,
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """Simple HTML content to display Gold Passbook price list for a year"""
    t_price_list = GoldPassbookModel.get_price_list_by_year(p_yyyy, 
                                                            p_index_type, p_currency)
    t_content = 'BOT Gold Passbook Price for Year %s with count %d\n\n' % (p_yyyy,
                                                                           len(t_price_list))
    for entry in t_price_list:
        t_content += str(entry) + '\n'
    
    return  HttpResponse(content_type='text/plain',
                            content = t_content)
    
    
def gold_passbook_clean_view(request, 
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """Purge datastore and redirect to digest view"""
    
    GoldPassbookModel.clean_datastore(p_index_type, p_currency)
    
    return HttpResponseRedirect(reverse('passbook_digest_view'))
    
def gold_passbook_digest_view(request, 
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """Simple HTTP content to display BOT Gold Passbook price index digest"""
    response = HttpResponse(content_type='text/plain')
    response.content = GoldPassbookModel.get_price_digest(p_index_type, p_currency)
    return response

def httphandler_init_datastore(request, 
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """HTTP request handler for GAE datastore initilaization process
    """
    taskhandler_url = reverse('datastore_update_task')
    GoldPassbookModel.init_datastore(taskhandler_url, p_index_type, p_currency)

    return HttpResponseRedirect(reverse('passbook_digest_view'))

def httphandler_daily_update_chain_task(request,
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """HTTP request handler for GAE Task Queue daily update process"""
    
    taskhandler_url = reverse('datastore_update_task')
    t_update_pass = GoldPassbookModel.daily_update_chain_task(taskhandler_url, 
                                                              p_index_type, 
                                                              p_currency)
    
    response = HttpResponse()
    if t_update_pass:
        response.content = 'GoldPassbookModel.daily_update_chain_task pass'
        response.status_code = httplib.OK
    else:
        response.content = 'GoldPassbookModel.daily_update_chain_task fail'
        response.status_code = httplib.INTERNAL_SERVER_ERROR
        
    return response