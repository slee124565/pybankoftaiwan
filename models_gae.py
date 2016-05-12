from google.appengine.ext import db
from google.appengine.api import taskqueue

from datetime import date, datetime, timedelta
import logging, json
import goldpassbook as gpbk
from bot import goldpassbook

logger = logging.getLogger(__name__)

UPDATE_TASK_COUNTDOWN = 5

def add_passbook_update_task(p_update_task_url, p_index_type = gpbk.TYPE_SELLING, 
                               p_currency = gpbk.CURRENCY_TWD):
    """To add a task in GAE taskqueue for update Passbook datastore"""
    
    queue_name = '%s-%s-%s' % ( 'passbook', p_currency, p_index_type )
    
    try:
        taskqueue.Queue(queue_name).purge()
        taskqueue.add(method = 'GET',
                  queue_name = queue_name,
                  url = p_update_task_url,
                  countdown = UPDATE_TASK_COUNTDOWN
              )
        logger.info('add passbook update task')
        return True
    except:
        logger.error('add passbook update task fail', exc_info = True)
        return False
    
class GoldPassbookMetaModel(db.Model):
    """datastore module to log the last date for model `GoldPassbookModel`
    it keeps.
    """
    date_start = db.DateProperty()
    date_end = db.DateProperty()
    err_date_list = db.BlobProperty(default='[]')
    
    @classmethod
    def get_date_start_end(cls, p_index_type, p_currency):
        t_keyname = cls.get_model_key_name(p_index_type, p_currency)
        t_model = cls.get_by_key_name(t_keyname)
        return t_model.date_start, t_model.date_end
        
    @classmethod
    def get_model_key_name(cls,p_index_type,p_currency):
        return '{}-{}'.format(p_index_type,p_currency)
    
    @classmethod
    def add_no_price_index_date(cls,p_index_type,p_currency,p_date):
        t_keyname = cls.get_model_key_name(p_index_type, p_currency)
        t_model_meta = cls.get_by_key_name(t_keyname)
        t_err_date_list = json.loads(t_model_meta.err_date_list)
        logger.debug('pre err_date_list: %s' % str(t_err_date_list))
        if not str(p_date) in t_err_date_list:
            t_err_date_list.append(str(p_date))
            logger.debug('new err_date_list: %s' % str(t_err_date_list))
            t_model_meta.err_date_list = json.dumps(t_err_date_list)
            t_model_meta.put()
            logger.info('log the date %s failed to get price index' % p_date) 
    
class GoldPassbookModel(db.Model):
    """datastore model to keep yearly BOT Gold Passbook price data
    """
    year_price_index_json = db.BlobProperty(default='[]')
    #last_price_date = db.DateProperty()
    
    def add_price_index(self, p_price_index):
        t_year_price_index = json.loads(self.year_price_index_json)
        t_date_list = [t_entry[0] for t_entry in t_year_price_index]
        
        if str(p_price_index[0]) in t_date_list:
            t_index = t_date_list.indexof(str(p_price_index[0]))
            logger.warning('price index already exist; replace %s with %s' % (t_year_price_index[t_index],
                                                                              p_price_index[0]))
            del t_year_price_index[t_index]
        
        p_price_index[0] = str(p_price_index[0])
        t_year_price_index.append(p_price_index)
        t_year_price_index.sort(key = lambda x : x[0])
        self.year_price_index_json = json.dumps(t_year_price_index)
        self.put()
        logger.info('add price index %s' % p_price_index)
    
    @classmethod
    def get_price_list_by_year(cls, p_yyyy, p_index_type = gpbk.TYPE_SELLING, 
                               p_currency = gpbk.CURRENCY_TWD):
        """return a list of price index list for the given year"""
        t_model = cls.get_or_insert_entity(p_yyyy, p_index_type, p_currency)
        t_list = json.loads(t_model.year_price_index_json) 
        logger.debug('get_price_list_by_year for year %s has len %d' % (p_yyyy,len(t_list)))
        return t_list
       
    @classmethod
    def get_or_insert_entity(cls, p_yyyy, p_index_type = gpbk.TYPE_SELLING, p_currency = gpbk.CURRENCY_TWD):
        """return entity from datastore with related parent object GoldPassbookMetaModel
        """
        t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_meta = GoldPassbookMetaModel.get_or_insert(t_keyname)
        
        t_keyname = GoldPassbookModel.get_model_key_name(p_yyyy, p_index_type, p_currency)
        t_model = GoldPassbookModel.get_or_insert(t_keyname, parent=t_meta)
        
        return t_model
        
    @classmethod
    def get_price_digest(cls, p_index_type = gpbk.TYPE_SELLING, p_currency = gpbk.CURRENCY_TWD):
        """return a digest information about current data in datastore,
        combined with first few price index and last few price index
        """
        t_content = 'BOT Gold Passbook Simple Digest'
        t_content += '\n'+ '=' * len(t_content) + '\n\n'
        
        keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_meta = GoldPassbookMetaModel.get_by_key_name(keyname)
        date_start = t_meta.date_start
        date_end = t_meta.date_end
        err_list = json.loads(t_meta.err_date_list)
        logger.debug('err_list: %s' % str(err_list))

        t_content += 'from %s to %s\n\n' % (date_start, date_end)
        
        t_model = cls.get_or_insert_entity(date_start.year, p_index_type, p_currency)
        t_year_index_list = json.loads(t_model.year_price_index_json)
        for entry in t_year_index_list[:5]:
            t_content += str(entry) + '\n'
        t_content += '\n...\n\n'
        
        t_model = cls.get_or_insert_entity(date_end.year, p_index_type, p_currency)
        t_year_index_list = json.loads(t_model.year_price_index_json)
        for entry in t_year_index_list[-10:]:
            t_content += str(entry) + '\n'
        
        t_content += '\n=== err date list ===\n\n'
        for entry in err_list:
            t_content += '%s (%s)\n' %(entry, datetime.strptime(entry,'%Y-%m-%d').strftime('%a'))
        t_content += '\ncount %d\n' % len(err_list)
        
        t_content += '\n=== task queue ===\n'
        t_queue_stat = taskqueue.Queue().fetch_statistics()
        t_content += '\nThere is %d tasks in taskqueue' % t_queue_stat.tasks
        
        return t_content
    
    @classmethod
    def get_model_key_name(cls, p_yyyy,p_index_type,p_currency):
        """define model key_name format"""
        return '{}-{}-{}'.format(p_yyyy,p_index_type,p_currency)
        
    @classmethod
    def clean_datastore(cls, p_index_type = gpbk.TYPE_SELLING, p_currency = gpbk.CURRENCY_TWD):
        
        t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_ancestor = GoldPassbookMetaModel.get_or_insert(t_keyname)
        t_entities = cls.all().ancestor(t_ancestor)
        logger.info('remove %d entities for GoldPassbookModel with index_type %d and currency %s.' \
                    % (t_entities.count(), p_index_type, p_currency))
        db.delete(t_entities)
        
        t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_meta = GoldPassbookMetaModel.get_by_key_name(t_keyname)
        db.delete(t_meta)
    
    @classmethod
    def init_datastore(cls, p_update_task_url, p_index_type = gpbk.TYPE_SELLING, 
                       p_currency = gpbk.CURRENCY_TWD):
        """a class method is used to initialize datastore with price
        index data under history directory
        """
        logger.debug('== init_datastore begin ==')
        
        #-> remove existing GoldPassbookModel entities
        cls.clean_datastore(p_index_type, p_currency)
        
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
                t_model = cls.get_or_insert_entity(t_year, p_index_type, p_currency)
                t_model.year_price_index_json = json.dumps(t_year_index)
                #t_model.last_price_date = datetime.strptime( t_year_index[-1][0], '%Y-%m-%d').date()
                t_model.put()
                logger.info('year %d init with count %d' % (t_year,len(t_year_index)))
            t_year += 1
            
        #-> update model GoldPassbookMetaModel
        t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_model = GoldPassbookMetaModel.get_or_insert(t_keyname)
        t_model.date_start = t_date_start
        t_model.date_end = t_date_end 
        t_model.put()
        logger.debug('init_datastore with date_start: %s , date_end: %s' % (str(t_date_start),
                                                                            str(t_date_end)))
        #-> activate datastore upate process
        cls.daily_update_chain_task(p_update_task_url, p_index_type, p_currency)

        logger.debug('== init_datastore end ==')
    
    @classmethod
    def update_price_index_by_date(cls, p_date, p_index_type = gpbk.TYPE_SELLING, 
                                   p_currency = gpbk.CURRENCY_TWD):
        """a class method is used to update model `GoldPassbookModel` 
        by targe date `p_date` and will not update `GoldPssbookMetaModel`
        """
        #-> fetch price index
        t_price_index = goldpassbook.get_date_price_index(p_date, p_index_type, p_currency)
        
        if t_price_index is None:
            if p_date.weekday() <= 4: #-> not weekend, log err date
                logger.warning('could not get price index for date %s' % p_date)
                GoldPassbookMetaModel.add_no_price_index_date(p_index_type, p_currency, p_date)

        else:
            #-> update GoldPassbookModel & GoldPassbookMetaModel
            t_model = cls.get_or_insert_entity(p_date.year, p_index_type, p_currency)
            t_model.add_price_index(t_price_index)

        return True
           
    @classmethod
    def daily_update_chain_task(cls, p_update_task_url, p_index_type = gpbk.TYPE_SELLING, 
                                p_currency = gpbk.CURRENCY_TWD):
        """a class method is used to update model `GoldPassbookModel` 
        in datastore with Chain Task pattern. It will get daily price
        index by attribute `date_end` in model `GoldPassbookMetaModel` 
        and setup another daily update task for next day in queue until 
        the next day is today.
        """
        logger.debug('== daily_update_chain_task begin ==')
        
        t_keyname = GoldPassbookMetaModel.get_model_key_name(p_index_type, p_currency)
        t_model_meta = GoldPassbookMetaModel.get_by_key_name(t_keyname)
        t_date_end = t_model_meta.date_end
        t_target_date = t_date_end + timedelta(days=1)
        
        #-> check the next day of date_end is not today cause price will vary by time
        if t_target_date >= date.today():
            logger.info('the last date %s of datastore is already up-to-date' % t_date_end)
            return True 
        
        #-> fetch price index
        cls.update_price_index_by_date(t_target_date, p_index_type, p_currency)
        
        #-> update meta
        t_model_meta.date_end = t_target_date
        t_model_meta.put()
        
        #-> setup next task if next day is not today
        t_next_date = t_target_date + timedelta(days=1)
        if t_next_date < date.today():
            add_passbook_update_task(p_update_task_url,p_index_type,p_currency)
             
        logger.debug('== daily_update_chain_task end ==')
        return True
                
