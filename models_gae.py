from google.appengine.ext import db

from datetime import date, datetime
import logging, json
from django.http import HttpResponse
import goldpassbook as gpbk

logger = logging.getLogger(__name__)

class GoldPassbookMetaModel(db.Model):
    """datastore module to log the last date for model `GoldPassbookModel`
    it keeps.
    """
    date_start = db.DateProperty()
    date_end = db.DateProperty()
    
    @classmethod
    def get_model_key_name(cls,p_index_type,p_currency):
        return '{}-{}'.format(p_index_type,p_currency)
    
class GoldPassbookModel(db.Model):
    """datastore model to keep yearly BOT Gold Passbook price data
    """
    year_price_index_json = db.BlobProperty(default='[]')
    last_price_date = db.DateProperty()
    
    @classmethod
    def get_model_key_name(cls, p_yyyy,p_index_type,p_currency):
        return '{}-{}-{}'.format(p_yyyy,p_index_type,p_currency)
        
    @classmethod
    def init_datastore(cls, p_index_type = gpbk.TYPE_SELLING, p_currency = gpbk.CURRENCY_TWD):
        """a class method is used to initialize datastore with price
        index data under history directory
        """
        logger.info('== init_datastore begin ==')
        t_date_start = date(gpbk.HISTORY_YEAR_START,12,31)
        t_date_end = t_date_start
        t_year = gpbk.HISTORY_YEAR_START
        while t_year <= gpbk.HISTORY_YEAR_END:
            t_date = date(t_year,1,1)
            t_year_index = gpbk.load_year_history(t_date,p_index_type,p_currency)
            if len(t_year_index) > 0:
                #-> check for t_date_start
                if t_date_start > datetime.strptime(t_year_index[0][0],'%Y-%m-%d').date():
                    logger.debug('t_date_start is changed from %s to %s' % (t_date_start,t_year_index[0][0]))
                    t_date_start = datetime.strptime(t_year_index[0][0],'%Y-%m-%d').date()
                #-> check for t_date_end
                if t_date_end < datetime.strptime(t_year_index[-1][0],'%Y-%m-%d').date():
                    logger.debug('t_date_end is changed from %s to %s' % (t_date_end,t_year_index[-1][0]))
                    t_date_end = datetime.strptime(t_year_index[-1][0],'%Y-%m-%d').date()
                #-> update model GoldPassbookModel   
                t_keyname = GoldPassbookModel.get_model_key_name(t_year,p_index_type,p_currency)
                t_model = GoldPassbookModel.get_or_insert(t_keyname)
                t_model.year_price_index_json = json.dumps(t_year_index)
                t_model.last_price_date = datetime.strptime( t_year_index[-1][0], '%Y-%m-%d').date()
                t_model.put()
                logger.info('year %d init with count %d and last price date %s' % (
                                                                                   t_year,
                                                                                   len(t_year_index),
                                                                                   t_model.last_price_date))
            t_year += 1
        #-> update model GoldPassbookMetaModel
        t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_model = GoldPassbookMetaModel.get_or_insert(t_keyname)
        t_model.date_start = t_date_start
        t_model.date_end = t_date_end 
        t_model.put()
        logger.debug('init_datastore with date_start: %s , date_end: %s' % (str(t_date_start),
                                                                            str(t_date_end)))
        
        logger.info('== init_datastore end ==')
        
    @classmethod
    def daily_update_chain_task(cls):
        """a class method is used to update model `GoldPassbookModel` 
        in datastore with Chain Task pattern. It will get daily price
        index by attribute `date_end` in model `GoldPassbookMetaModel` 
        and setup another daily update task for next day in queue until 
        the next day is today.
        """
        logger.info('== daily_update_chain_task begin ==')
        logger.info('== daily_update_chain_task end ==')
        pass
                
