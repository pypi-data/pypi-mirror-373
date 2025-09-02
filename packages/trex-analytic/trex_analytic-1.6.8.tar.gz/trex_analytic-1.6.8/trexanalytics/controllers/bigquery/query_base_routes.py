'''
Created on 19 Jan 2021

@author: jacklok
'''

from flask_restful import Resource
from trexconf import conf
import logging
from trexlib.utils.log_util import get_tracelog

from trexlib.utils.google.bigquery_util import execute_query, process_job_result_into_category_and_count, create_bigquery_client
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexlib.utils.common.cache_util import getFromCache, setCache
import json

#logger = logging.getLogger('analytics')
logger = logging.getLogger('target_debug')

class BaseResource(Resource):
    
    def post(self):
        return self.get()
    
    def get(self):
        logger.info('base resource')
        
        return 'Base'
        

class QueryBaseResource(Resource):
    
    def post(self):
        return self.get()
    
    @request_values
    def get(self, request_values):
        logger.info('query base resource from QueryBaseResource') 
        
        #if is_not_empty(content):
        query           = self.prepare_query(**request_values)
        
        logger.info('query=%s', query)
        
        bg_client       = create_bigquery_client(
                            credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH,
                            project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID,
                            )
        
        if bg_client is not None:
            logger.info('BigQuery Client is not none, thus going to execute query')
        
            try:
                result_rows = execute_query(bg_client, query)
                        
                logger.debug('result_rows=%s', result_rows)
                job_result_rows = [dict(row) for row in result_rows]
                logger.debug('job_result_rows=%s', job_result_rows)
                
                bg_client.close()
            except:
                job_result_rows = []
                logger.error('Failed to execute query due to %s', get_tracelog())
        else:
            job_result_rows = []
            
        query_result    = self.process_query_result(job_result_rows)
        
        logger.info('query_result=%s', query_result)
        
        return query_result
        #else:
        #    return {}
        
    def prepare_query(self, **kwrgs):
        pass
    
    def process_query_result(self, job_result_rows):
        pass

class CachedQueryBaseResource(QueryBaseResource):
    
    def is_cached(self):
        return True
    
    def get_timeout_amount(self):
        return 600
    
    @request_values
    def get(self, request_values):
        logger.info('query base resource from QueryBaseResource') 
        
        query           = self.prepare_query(**request_values)
        logger.info('query=%s', query)
        try:
            to_cache = self.is_cached()
            if to_cache:
                job_result_rows = getFromCache(query)
                logger.debug('result from cache=%s', job_result_rows)
                
                if job_result_rows is None:
                    
                    bg_client       = create_bigquery_client(
                                        credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH,
                                        project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID,
                                        )
        
                    if bg_client is not None:
                        logger.info('BigQuery Client is not none, thus going to execute query')
                        
                        result_rows = execute_query(bg_client, query)
                        logger.debug('result_rows=%s', result_rows)
                        job_result_rows = [dict(row) for row in result_rows]
                        logger.debug('job_result_rows=%s', job_result_rows)
                        
                        serialized_data = json.dumps(job_result_rows)
                        
                        setCache(query, serialized_data, timeout=self.get_timeout_amount())
                        
                        bg_client.close()
                    else:
                        job_result_rows = []
                        
                else:
                    
                    job_result_rows = json.loads(job_result_rows)
            else:
                bg_client       = create_bigquery_client(
                                        credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH,
                                        project_id=conf.BIGQUERY_GCLOUD_PROJECT_ID,
                                        )
        
                if bg_client is not None:
                    logger.info('BigQuery Client is not none, thus going to execute query')
                    job_result_rows = execute_query(bg_client, query)
                    
                    rows = [dict(row) for row in job_result_rows]
                        
                    job_result_rows = json.dumps(rows)
                    
                    bg_client.close()
                else:
                    job_result_rows = []
                    
            
            
        except:
            job_result_rows = []
            logger.error('Failed to execute query due to %s', get_tracelog())
            
        query_result    = self.process_query_result(job_result_rows)
        
        
        
        logger.info('query_result=%s', query_result)
        
        return query_result
    
    
    
class CategoryAndCountQueryBaseResource(QueryBaseResource):
    
    def process_query_result(self, job_result_rows):
        return process_job_result_into_category_and_count(job_result_rows)
    
class FieldnameAndValueQueryBaseResource(QueryBaseResource):
    
    def process_query_result(self, job_result_rows):
        return process_job_result_into_category_and_count(job_result_rows)    
    
    
        