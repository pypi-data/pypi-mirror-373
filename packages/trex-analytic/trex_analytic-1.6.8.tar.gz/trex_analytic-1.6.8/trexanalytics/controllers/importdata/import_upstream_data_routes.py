'''
Created on 26 Jan 2021

@author: jacklok
'''

from flask import Blueprint, jsonify, Response
from flask_restful import Resource
import logging
from trexlib.utils.google.bigquery_util import create_bigquery_client, stream_data,\
    update_stream_data
from trexconf import conf as analytics_conf
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexanalytics.controllers.importdata.import_data_base_routes import TriggerImportDataBaseResource, InitImportDataBaseResource, ImportDataBaseResource, TriggerImportDataByDateRangeBaseResource, ImportDataByDateRangeResource
from flask_restful import Api
from trexanalytics.bigquery_table_template_config import TABLE_SCHEME_TEMPLATE,\
    TESTING_TEMPLATE
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexanalytics.bigquery_upstream_data_config import upstream_schema_config,\
    create_test_upstream_data
from uuid import uuid1


import_upstream_data_bp = Blueprint('import_upstream_data_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/analytics/import-upstream-data')

logger = logging.getLogger('target_debug')

import_upstream_data_api = Api(import_upstream_data_bp)

class CheckUnsendUpstreamDataResource(Resource):
    
    def output_html(self, content, code=200, headers=None):
        resp = Response(content, mimetype='text/html', headers=headers)
        resp.status_code = code
        return resp
    
    def post(self):
        return self.get()
    
    def get(self):
        try:
            result = list_all_unsend_upstream_data()
        except:
            logger.debug(get_tracelog())
        
        #return self.output_html("count=%d, <br>%s"% (len(result), result))
        return jsonify({
                'count': len(result),
                'result':result,
                })
    
class ImportUpstreamDataResource(Resource):
    
    def output_html(self, content, code=200, headers=None):
        resp = Response(content, mimetype='text/html', headers=headers)
        resp.status_code = code
        return resp
    
    def post(self):
        return self.get()
    
    @request_values
    def get(self, request_values):
        import_limit    = request_values.get('limit') or 1
        imported_count  = 0
        error_count     = 0
        try:
            (imported_count, error_count) = import_upstream_data_by_limit_function(limit = int(import_limit))
        except:
            logger.debug(get_tracelog())
        
        return self.output_html("imported_count=%d, error_count=%d, import datetim=%s"% (imported_count, error_count, datetime.now()))    

class TriggerImportAllUpstreamData(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/analytics/import-upstream-data/init-import-all-upstream-data'
    
    def get_task_queue(self):
        return 'import-upstream'
    
    
class InitImportAllUpstreamData(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        count =  count_all_unsend_upstream_data()
        logger.info('InitImportAllUpstreamData debug: unsend upstream data count = %d', count)
        return count
    
    def get_import_data_page_size(self):
        return analytics_conf.STREAM_DATA_PAGE_SIZE
    
    def get_task_url(self):
        return '/analytics/import-upstream-data/import-all-upstream-data'
    
    def get_task_queue(self):
        return 'import-upstream'
    

def count_all_unsend_upstream_data():
    db_client = create_db_client(caller_info="count_all_unsend_upstream_data")
    with db_client.context():
        count       = UpstreamData.count_not_sent()
        
    return count

def list_all_unsend_upstream_data():
    db_client = create_db_client(caller_info="list_all_unsend_upstream_data")
    final_result = []
    with db_client.context():
        result       = UpstreamData.list_not_send()
        for r in result:
            final_result.append(r.to_dict())
    return final_result

def count_upstream_data_by_date_range(date_start, date_end):
    db_client = create_db_client(caller_info="count_upstream_data_by_date_range")
    with db_client.context():
        count       = UpstreamData.count_by_date_range(date_start, date_end)
    return count


class ImportAllUpstreamData(ImportDataBaseResource): 
    def import_data(self, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d', offset, limit)
        
        
        try:
            start_cursor    = kwargs.get('start_cursor')
            batch_id        = kwargs.get('batch_id')
            
            logger.info('ImportAllUpstreamData: start_cursor=%s', start_cursor)
            logger.info('ImportAllUpstreamData: batch_id=%s', batch_id)
            
            next_cursor     = import_all_unsend_upstream_data_function(dataset_name='system', limit=limit, start_cursor=start_cursor, batch_id=batch_id)
            
            logger.info('ImportAllUpstreamData: next_cursor=%s', next_cursor)
            
            return next_cursor
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
    
    def get_task_url(self):
        return '/analytics/import-upstream-data/import-all-upstream-data'
    
    def get_task_queue(self):
        return 'import-upstream'

class TriggerImportUpstreamDataByDateRange(TriggerImportDataByDateRangeBaseResource):
    
    def get_task_url(self):
        return '/analytics/import-upstream-data/init-import-all-upstream-data-by-date-range'
    
    def get_task_queue(self):
        return 'import-upstream'    
    

class InitImportUpstreamDataByDateRange(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        date_start  = kwargs['date_start']
        date_end    = kwargs['date_start']
        
        date_start_in_dt    = datetime.strptime(date_start, '%d-%m-%Y')
        date_end_in_dt      = datetime.strptime(date_end, '%d-%m-%Y')
        
        return count_upstream_data_by_date_range(date_start_in_dt, date_end_in_dt)
    
    def get_task_url(self):
        return '/analytics/import-upstream-data/import-all-upstream-data-by-date-range'
    
    
class ImportUpstreamDataByDateRange(ImportDataByDateRangeResource): 
    def import_data(self, date_start, date_end, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d date_start=%s date_end=%s', offset, limit, date_start, date_end)
        
        
        try:
            start_cursor    = kwargs.get('start_cursor')
            batch_id        = kwargs.get('batch_id')
            
            logger.debug('ImportUpstreamDataByDateRange: start_cursor=%s', start_cursor)
            logger.debug('ImportUpstreamDataByDateRange: batch_id=%s', batch_id)
            
            next_cursor     = import_upstream_data_by_date_range_function(date_start, date_end, dataset_name='system', limit=limit, start_cursor=start_cursor, batch_id=batch_id)
            
            logger.debug('ImportUpstreamDataByDateRange: next_cursor=%s', next_cursor)
            
            return next_cursor
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
    
    def get_task_url(self):
        return '/analytics/import-upstream-data/import-all-upstream-data-by-date-range'
    
    def get_task_queue(self):
        return 'import-upstream'    
    
def import_all_unsend_upstream_data_function(credential_info=None, dataset_name='system_dataset', 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None):
    
    
    logger.debug('credential_filepath=%s', analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    logger.debug('bg_client.project=%s', bg_client.project)
    
    db_client = create_db_client(info=credential_info, caller_info="import_all_unsend_upstream_data_function")
    import_upstream_dict = {}
    
    logger.debug('import_all_unsend_upstream_data_function (%s): start_cursor=%s', batch_id, start_cursor)
    
    with db_client.context():
        (upstream_data_list, next_cursor) = UpstreamData.list_not_send(limit = limit, start_cursor=start_cursor, return_with_cursor=True)
        #(upstream_data_list, next_cursor) = UpstreamData.list_all(limit = limit, start_cursor=start_cursor, return_with_cursor=True)
    
    errors          = []    
    imported_count  = 0
    
    for u in upstream_data_list:
        
        table_template_name = u.table_template_name
        dataset_name        = u.dataset_name
        table_name          = u.table_name
        stream_content      = u.stream_content
        
        partition_datetime  = u.partition_datetime
        
        import_upstream_dict = {'': stream_content}

        logger.debug('################################ batch_id= %s ############################################', batch_id)
        logger.info(import_upstream_dict)
        logger.debug('#####################################################################################################')
        
        __errors = stream_data(bg_client, dataset_name, table_template_name, 
                               TABLE_SCHEME_TEMPLATE.get(table_template_name), table_name, stream_content,
                               partition_datetime=partition_datetime
                                                   )
        
        if len(__errors)>0:
            errors.extend(__errors)
        else:
            with db_client.context():
                u.is_sent = True
                u.put()
                logger.debug("New rows have been added")
                
            imported_count+=1
            
    bg_client.close()
    
    if errors==[]:
        logger.debug('imported_count=%d', imported_count)
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    return next_cursor


def import_testing_upstream_data(testing_json ):
    logger.debug('credential_filepath=%s', analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    logger.debug('bg_client.project=%s', bg_client.project)
    
    #if credential_info is None:
    #    credential_info = current_app.config['credential_config']
        
    dataset_name    = 'testing'
    schema          = upstream_schema_config.get(TESTING_TEMPLATE)
    stream_content  = create_test_upstream_data(testing_json, schema)
    
    stream_data(bg_client, dataset_name, TESTING_TEMPLATE, 
                                                   TABLE_SCHEME_TEMPLATE.get(TESTING_TEMPLATE), TESTING_TEMPLATE, [stream_content]
                                                   )
    

def update_testing_upstream_data(update_testing_data_json):
    logger.debug('credential_filepath=%s', analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    logger.debug('bg_client.project=%s', bg_client.project)
    
    dataset_name    = 'testing'
    
    schema          = upstream_schema_config.get(TESTING_TEMPLATE)
    
    updated_fields      = update_testing_data_json.get('updated_fields')
    condition_fields    = update_testing_data_json.get('condition_fields')
    
    updated_fields      = create_test_upstream_data(updated_fields, schema)
    condition_fields    = create_test_upstream_data(condition_fields, schema)
    
    update_testing_data_json['updated_fields']      = updated_fields
    update_testing_data_json['condition_fields']    = condition_fields
    
    update_stream_data(bg_client, dataset_name, TESTING_TEMPLATE, 
                                                   TABLE_SCHEME_TEMPLATE.get(TESTING_TEMPLATE), 
                                                   TESTING_TEMPLATE, 
                                                   [update_testing_data_json]
                                                   )
        

def import_upstream_data_by_limit_function(credential_info=None, dataset_name='system_dataset', 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE
                                            ):
    
    
    logger.debug('credential_filepath=%s', analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    logger.debug('bg_client.project=%s', bg_client.project)
    
    #if credential_info is None:
    #    credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="import_upstream_data_by_date_range_function")
    import_upstream_dict = {}
    
    logger.debug('import_upstream_data_by_limit_function limit=%s', limit)
    
    
    
    with db_client.context():
        upstream_data_list= UpstreamData.list_not_send(limit = limit)
    
    import_count    = len(upstream_data_list)
    error_count     = 0
    errors          = []    
    imported_count  = 0
    
    for u in upstream_data_list:
        
        table_template_name = u.table_template_name
        dataset_name        = u.dataset_name
        table_name          = u.table_name
        stream_content      = u.stream_content
        
        import_upstream_dict = {'': stream_content}


    
        logger.debug('################################ import_upstream_data_by_limit_function ############################################')
        logger.debug('upstream data key=%s', u.key_in_str)
        logger.debug(import_upstream_dict)
        logger.debug('#####################################################################################################')
        
        
        
        __errors = stream_data(bg_client, dataset_name, table_template_name, 
                                                   TABLE_SCHEME_TEMPLATE.get(table_template_name), table_name, stream_content
                                                   )
        
        if len(__errors)>0:
            errors.extend(__errors)
            with db_client.context():
                u.delete()
            error_count+=1
        else:
            with db_client.context():
                u.is_sent = True
                u.put()
                logger.debug("New rows have been added")
                
            imported_count+=1
            
    bg_client.close()
    
    if errors==[]:
        logger.debug('imported_count=%d', imported_count)
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    return (imported_count, error_count)

def import_upstream_data_by_date_range_function(date_start, date_end, credential_info=None, dataset_name='system_dataset', 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None,
                                            
                                            ):
    
    
    logger.debug('credential_filepath=%s', analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    logger.debug('bg_client.project=%s', bg_client.project)
    
    #if credential_info is None:
    #    credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="import_upstream_data_by_date_range_function")
    import_upstream_dict = {}
    
    logger.debug('import_upstream_data_by_date_range_function (%s): start_cursor=%s', batch_id, start_cursor)
    
    
    
    with db_client.context():
        (upstream_data_list, next_cursor) = UpstreamData.list_by_date_range(date_start, date_end, limit = limit, start_cursor=start_cursor, return_with_cursor=True)
    
    import_count    = len(upstream_data_list)
    errors          = []    
    imported_count  = 0
    
    for u in upstream_data_list:
        
        table_template_name = u.table_template_name
        dataset_name        = u.dataset_name
        table_name          = u.table_name
        stream_content      = u.stream_content
        
        import_upstream_dict = {'': stream_content}


    
        logger.debug('################################ batch_id= %s ############################################', batch_id)
        logger.debug(import_upstream_dict)
        logger.debug('#####################################################################################################')
        
        __errors = stream_data(bg_client, dataset_name, table_template_name, 
                                                   TABLE_SCHEME_TEMPLATE.get(table_template_name), table_name, stream_content
                                                   )
        
        if len(__errors)>0:
            errors.extend(__errors)
        else:
            with db_client.context():
                u.is_sent = True
                u.put()
                logger.debug("New rows have been added")
                
            imported_count+=1
            
    bg_client.close()
    
    if errors==[]:
        logger.debug('imported_count=%d', imported_count)
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    return next_cursor
    
@import_upstream_data_bp.route('/upstream/data-content/<upstream_data_key>')
def read_upstream_data_content(upstream_data_key):
    
    logger.debug('upstream_data_key=%s', upstream_data_key)
    
    try:
        db_client = create_db_client(caller_info="read_upstream_data_content")
        with db_client.context():
            upstream_data = UpstreamData.fetch(upstream_data_key)
            
        if upstream_data:
            return jsonify(upstream_data.stream_content)
    except:
        logger.debug('Failed to fetch upstream data due to %s', get_tracelog())
    
    return 'Not found', 200

@import_upstream_data_bp.route('/upstream/data-content/date-start/<date_start>/date-end/<date_end>')
def read_upstream_data_content_by_date_range(date_start, date_end, limit=5):
    
    logger.debug('date_start=%s', date_start)
    logger.debug('date_end=%s', date_end)
    
    data_list = []
    
    date_start_in_dt    = datetime.strptime(date_start, '%d-%m-%Y')
    date_end_in_dt      = datetime.strptime(date_end, '%d-%m-%Y')
    
    try:
        db_client = create_db_client(caller_info="read_upstream_data_content_by_date_range")
        with db_client.context():
            result = UpstreamData.list_by_date_range(date_start_in_dt, date_end_in_dt, limit=limit)
            
            for r in result:
                data_list.append(r.to_dict()) 
            
            
        if data_list:
            return jsonify(data_list)
    except:
        logger.debug('Failed to fetch upstream data due to %s', get_tracelog())
    
    return 'Not found', 200


import_upstream_data_api.add_resource(CheckUnsendUpstreamDataResource,         '/check-unsend-upstream-data')
import_upstream_data_api.add_resource(ImportUpstreamDataResource,         '/import-unsend-upstream-data')

import_upstream_data_api.add_resource(TriggerImportAllUpstreamData,         '/trigger-import-all-upstream-data')
import_upstream_data_api.add_resource(InitImportAllUpstreamData,            '/init-import-all-upstream-data')
import_upstream_data_api.add_resource(ImportAllUpstreamData,                '/import-all-upstream-data')

import_upstream_data_api.add_resource(TriggerImportUpstreamDataByDateRange, '/trigger-import-all-upstream-data-by-date-range')
import_upstream_data_api.add_resource(InitImportUpstreamDataByDateRange,    '/trigger-import-all-upstream-data-by-date-range')
import_upstream_data_api.add_resource(ImportUpstreamDataByDateRange,        '/import-all-upstream-data-by-date-range')

        