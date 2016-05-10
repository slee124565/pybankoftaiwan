from django.shortcuts import render
from django.http import HttpResponse

import goldpassbook
from models_gae import GoldPassbookModel, GoldPassbookMetaModel

def httphandler_init_datastore(request, 
                               p_index_type = goldpassbook.TYPE_SELLING, 
                               p_currency = goldpassbook.CURRENCY_TWD):
    """HTTP request handler for GAE datastore initilaization process
    """
    GoldPassbookModel.init_datastore(p_index_type, p_currency)
    t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
    t_model = GoldPassbookMetaModel.get_by_key_name(t_keyname)
    return HttpResponse('datastore init with start date %s and end data %s' % (t_model.date_start,
                                                                              t_model.date_end))
