'''
Created on 11 Jan 2021

@author: jacklok
'''
from google.oauth2 import service_account 
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import logging
from datetime import datetime, date, time
from google.cloud.bigquery.dataset import DatasetReference
import uuid

#logger = logging.getLogger('import')
logger = logging.getLogger('target_debug')

def create_bigquery_client(info=None, credential_filepath=None, project_id=None):
    cred = None
    
    if info:
        cred = service_account.Credentials.from_service_account_info(info)
        
    else:
        logger.info('create_bigquery_client debug: credential_filepath=%s', credential_filepath)
        if credential_filepath:
            cred = service_account.Credentials.from_service_account_file(credential_filepath)
        
    logger.info('create_bigquery_client debug: project_id=%s', project_id)        
    if cred:
        client = bigquery.Client(project=project_id, credentials=cred)
        
        return client 

def create_dataset_reference(project_id, dataset_name):
    #dataset_ref = DatasetReference(lib_conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name)
    dataset_ref = DatasetReference(project_id, dataset_name)
    return dataset_ref


def if_dataset_exists(bigquery_client, dataset_ref):
    
    try:
        bigquery_client.get_dataset(dataset_ref)
        return True
    except NotFound:
        return False
    
def if_table_exists(bigquery_client, table_ref):
    try:
        bigquery_client.get_table(table_ref)
        return True
    except NotFound:
        return False    


def create_table_from_template(dataset_name, table_name, table_scheme, table_name_surfix=None, 
                               partition_value=None, bigquery_client=None, final_table_name=None):
    if bigquery_client is None:
        bigquery_client   = create_bigquery_client()
    
    project_id = bigquery_client.project
    
    logger.debug('create_table_from_template: project_id=%s', project_id)
    
    dataset_ref = create_dataset_reference(project_id, dataset_name)
    
    if if_dataset_exists(bigquery_client, dataset_ref) is False:
        logger.debug('dataset(%s) is not exist, thus going to create it', dataset_name)
        bigquery_client.create_dataset(dataset_ref, timeout=30)
    
    
    logger.debug('dataset_ref=%s' , dataset_ref)
    if final_table_name is None:
        final_table_name = table_name    
    
        if table_name_surfix:
            final_table_name = final_table_name+'_'+table_name_surfix
            
        if partition_value:
            final_table_name = final_table_name+'_'+partition_value
        
    logger.debug('final_table_name=%s' , final_table_name)
    
    table_ref = dataset_ref.table(final_table_name)
    
    logger.debug('table_ref=%s' , table_ref)
    
    if if_table_exists(bigquery_client, table_ref):   
        logger.debug('table(%s) is exist already', final_table_name)
        created_table =  bigquery_client.get_table(table_ref)
    
        return created_table
        
    else:
        
        logger.debug('table(%s) is not exist, thus going to create it', table_name)
        if table_scheme:
            table = bigquery.Table(table_ref, schema=table_scheme)
            created_table = bigquery_client.create_table(table)
                
            return created_table
        else:
            logger.debug('table(%s) scheme is required') 
    
            return None
        
def update_table_column(dataset_name, table_name, table_scheme, table_name_surfix=None, 
                               partition_value=None, bigquery_client=None, final_table_name=None,
                               column_name=None, column_data_type=None,
                               ):
    if bigquery_client is None:
        bigquery_client   = create_bigquery_client()
    
    project_id = bigquery_client.project
    
    logger.debug('create_table_from_template: project_id=%s', project_id)
    
    dataset_ref = create_dataset_reference(project_id, dataset_name)
    
    if if_dataset_exists(bigquery_client, dataset_ref) is False:
        logger.debug('dataset(%s) is not exist, thus going to create it', dataset_name)
        bigquery_client.create_dataset(dataset_ref, timeout=30)
    
    
    logger.debug('dataset_ref=%s' , dataset_ref)
    if final_table_name is None:
        final_table_name = table_name    
    
        if table_name_surfix:
            final_table_name = final_table_name+'_'+table_name_surfix
            
        if partition_value:
            final_table_name = final_table_name+'_'+partition_value
        
    logger.debug('final_table_name=%s' , final_table_name)
    
    table_ref = dataset_ref.table(final_table_name)
    
    logger.debug('table_ref=%s' , table_ref)
    
    if if_table_exists(bigquery_client, table_ref):   
        logger.debug('table(%s) is exist already', final_table_name)
        created_table =  bigquery_client.get_table(table_ref)
        
        new_schema = created_table.schema[:]
        new_schema.append(bigquery.SchemaField(column_name, column_data_type))
        
        created_table.schema = new_schema
        
        updated_table = bigquery_client.update_table(created_table, ["schema"])
    
        return updated_table
        
    else:
        
        logger.debug('table(%s) is not exist, thus going to create it', table_name)
        if table_scheme:
            table = bigquery.Table(table_ref, schema=table_scheme)
            created_table = bigquery_client.create_table(table)
                
            return created_table
        else:
            logger.debug('table(%s) scheme is required') 
    
            return None

def list_all_table_from_dataset(dataset_name, bigquery_client=None):
    if bigquery_client is None:
        bigquery_client   = create_bigquery_client()
    dataset_ref = create_dataset_reference(dataset_name)
    #dataset_ref = bq_client.dataset(dataset_name)
    
    logger.debug('dataset_ref=%s' , dataset_ref)
    tables_list = []
    
    if if_dataset_exists(bigquery_client, dataset_ref) is True:
        dataset = bigquery_client.get_dataset(dataset_ref)
        tables = list(bigquery_client.list_tables(dataset))
        
        logger.debug('tables=%s', tables)
        
        return tables
        
    return tables_list

def list_all_table_full_id_from_dataset(dataset_name, bigquery_client=None):
    tables_list = list_all_table_from_dataset(dataset_name, bigquery_client=bigquery_client)
    return ["{}.{}.{}".format(table.project, table.dataset_id, table.table_id) for table in tables_list]

def detele_table_from_dataset(dataset_name, table_name, bigquery_client=None):
    if bigquery_client is None:
        bigquery_client   = create_bigquery_client()
    dataset_ref = create_dataset_reference(dataset_name)
    #dataset_ref = bq_client.dataset(dataset_name)
    
    logger.debug('dataset_ref=%s' , dataset_ref)
    
    if if_dataset_exists(bigquery_client, dataset_ref) is True:
        
        table_ref = dataset_ref.table(table_name)
        
        logger.debug('table_ref=%s' , table_ref)
        
        bigquery_client.delete_table(table_ref, not_found_ok=True)
    
    return table_ref

def detele_all_tables_from_dataset(dataset_name, table_name, bigquery_client=None):
    
    if bigquery_client is None:
        bigquery_client   = create_bigquery_client()
    dataset_ref = create_dataset_reference(dataset_name)
    #dataset_ref = bq_client.dataset(dataset_name)
    
    if if_dataset_exists(bigquery_client, dataset_ref) is False:
        logger.debug('dataset(%s) is not exist, thus going to create it', dataset_name)
        bigquery_client.create_dataset(dataset_ref, timeout=30)
    
    
    logger.debug('dataset_ref=%s' , dataset_ref)
        
    table_ref = dataset_ref.table(table_name)
    
    logger.debug('table_ref=%s' , table_ref)
    
    bigquery_client.delete_table(table_ref, not_found_ok=True)
    
    
    
    return table_ref

def detele_dataset(dataset_name, bq_client=None):
    if bq_client is None:
        bq_client   = create_bigquery_client()
    dataset_ref = create_dataset_reference(dataset_name)
    
    if if_dataset_exists(bq_client, dataset_ref) is True:
        logger.debug('dataset(%s) is not exist, thus going to create it', dataset_name)
        bq_client.delete_dataset(dataset_ref)
    
    return dataset_ref

def is_dataset_exist(dataset_name, bigquery_client=None):
    if bigquery_client is None:
        bigquery_client   = create_bigquery_client()
        
    dataset_ref = create_dataset_reference(dataset_name)
    #dataset_ref = bq_client.dataset(dataset_name) 
    
    is_exist = if_dataset_exists(bigquery_client, dataset_ref)

    return is_exist

def default_serializable(val, none_as_empty_string=False):

    if isinstance(val, datetime):
        value = val.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(val, date):
        value = val.strftime('%Y-%m-%d')
    elif isinstance(val, time):
        value = val.strftime('%H:%M')
    elif isinstance(val, list):
        if val is None:
            value=[]
        else:    
            value = ','.join(val)    
    else:
        if val is None:
            if none_as_empty_string:
                value = ''
            else:
                value = val
        else:
            if isinstance(val, (bytes, bytearray)):
                value = val.decode('utf-8')
            else:
                value = val
            
    return value

def update_stream_data(bigquery_client, dataset_name, table_template_name, table_scheme, table_name, update_data_list_to_stream, 
                ):
    created_table       = create_table_from_template(dataset_name, table_template_name, table_scheme,
                                            final_table_name=table_name, 
                                             bigquery_client=bigquery_client)
    expected_fields = set(field.name for field in table_scheme)
    
    logger.debug('expected_fields=%s', expected_fields)
    
    for update_data_dict in update_data_list_to_stream:
        
        updated_fields_dict     = update_data_dict.get('updated_fields')
        condition_fields_dict   = update_data_dict.get('condition_fields')
        
        logger.debug('updated_fields_dict=%s', updated_fields_dict)
        logger.debug('condition_fields_dict=%s', condition_fields_dict)
        
        updated_field_list      = []
        condition_fields_list   = []
        using_fields_list       = []
        
        
        merged_condition_fields_list = []
        for k,v in condition_fields_dict.items():
            if k in expected_fields:
                serizalized_value = default_serializable(v)
                
                condition_query         = "T.{field_name}='{field_value}'".format(field_name=k, field_value=serizalized_value)
                using_query             = "'{field_value}' AS {field_name}".format(field_name=k, field_value=serizalized_value)
                merged_condition_query  = "T.{field_name}=S.{field_name}".format(field_name=k, field_value=serizalized_value)
                
                condition_fields_list.append(condition_query)
                using_fields_list.append(using_query)
                merged_condition_fields_list.append(merged_condition_query)
        
        for k,v in updated_fields_dict.items():
            if k in expected_fields:
                serizalized_value = default_serializable(v)
                updated_query   = "T.{field_name}=S.{field_name}".format(field_name=k, field_value=serizalized_value)
                using_query     = "'{field_value}' AS {field_name}".format(field_name=k, field_value=serizalized_value)
                
                updated_field_list.append(updated_query)
                using_fields_list.append(using_query)
        
        updated_fields_query            = ','.join(updated_field_list)
        condition_fields_query          = ','.join(condition_fields_list)
        using_fields_query              = ','.join(using_fields_list)
        merged_condition_fields_query   = ' and '.join(merged_condition_fields_list)
            
        
        logger.debug('updated_fields_query=%s', updated_fields_query)
        logger.debug('condition_fields_query=%s', condition_fields_query)
        
        query = '''
                MERGE `{table_name}` T
                USING (SELECT {using_fields} ) S
                ON {condition_fields} and {merged_condition}
                WHEN MATCHED THEN
                UPDATE SET {updated_fields}
                
                '''.format(
                    table_name          = created_table,
                    merged_condition    = merged_condition_fields_query,
                    updated_fields      = updated_fields_query, 
                    condition_fields    = condition_fields_query,
                    using_fields        = using_fields_query,
                    )
        #query = 'UPDATE {table} SET {updated_fields} WHERE {condition_fields}'.format(table=created_table, merged_condition=merged_condition_fields_query ,updated_fields=updated_fields_query, condition_fields=condition_fields_query)        
             
        
        logger.debug('query=%s', query)
        
        
        #query_job = bigquery_client.query(query)
        #query_job.result()
    
        

def stream_data(bigquery_client, dataset_name, table_template_name, table_scheme, table_name, data_list_to_stream, 
                partition_datetime=None):
    
    errors              = []
    created_table       = create_table_from_template(dataset_name, table_template_name, table_scheme,
                                            final_table_name=table_name, 
                                             bigquery_client=bigquery_client)
            
            
    logger.debug('==============================================')
    logger.debug('created_table=%s' , created_table)
    logger.debug('==============================================')
    
    serialize_data_to_stream_list = []
    
    expected_fields = set(field.name for field in table_scheme)
    
    for data_dict in data_list_to_stream:
        
        serialized_dict = {}
        if partition_datetime:
            serialized_dict['PartitionDateTime'] = datetime.strftime(partition_datetime, '%Y-%m-%d %H:%M:%S')
        
        for k,v in data_dict.items():
            if k in expected_fields:
                serialized_dict[k] = default_serializable(v)
        
        logger.debug('serialized_dict=%s', serialized_dict)
            
        serialize_data_to_stream_list.append(serialized_dict)
        
    logger.debug('serialize_data_to_stream_list=%s' , serialize_data_to_stream_list)
            
    __errors = bigquery_client.insert_rows_json(table=created_table, json_rows=serialize_data_to_stream_list, skip_invalid_rows=False, ignore_unknown_values=False)
    
    logger.debug('==============================================')
    logger.debug('__errors=%s' , __errors)
    logger.debug('==============================================')
            
    if len(__errors)>0:
        errors.extend(__errors)
            
    return errors

def stream_data_by_datetime_partition(bigquery_client, dataset_name, table_template_name, table_scheme, data_dict_to_stream, column_name_used_to_partition=None, 
                             partition_date=False, partition_month=False, partition_year=False):
    
    errors                      = []
    partition_date_formation    = None
    logger.debug('table_scheme=%s' , table_scheme)
    logger.debug('column_name_used_to_partition=%s' , column_name_used_to_partition)
    
    if column_name_used_to_partition and (partition_date or partition_month or partition_year):
        logger.debug('partition_date=%s' , partition_date)
        logger.debug('partition_month=%s' , partition_month)
        logger.debug('partition_year=%s' , partition_year)
        
        if partition_date:
            partition_date_formation = '%Y%m%d'
            
        elif partition_month:
            partition_date_formation = '%Y%m'
            
        elif partition_year:
            partition_date_formation = '%Y'
        
        logger.debug('partition_date_formation=%s', partition_date_formation)
    
    
    for table_name_suffix, data_list_to_stream in data_dict_to_stream.items():
    
        partition_dict              =  {}
        partition_value_str         = ''
        #partition data first
        for data_dict in data_list_to_stream:
            if partition_date_formation:
                partition_value         = data_dict.get(column_name_used_to_partition)
                
                logger.debug('partition_value=%s', partition_value)
                
                if partition_value:
                    partition_value_str     = partition_value.strftime(partition_date_formation)
                
            
            partition_list = partition_dict.get(partition_value_str)
            if partition_list is None:
                partition_list = []
            
            serialized_dict = {}
            
            for k,v in data_dict.items():
                serialized_dict[k] = default_serializable(v)
                
            partition_list.append(serialized_dict)
            partition_dict[partition_value_str] = partition_list
        
        logger.debug('*****************************************')
        logger.debug('table_name_suffix=%s' , table_name_suffix)
        logger.debug('partition_dict=%s' , partition_dict)
        logger.debug('*****************************************')
        
        #stream partiion data
        for partition_value_str, partition_list in partition_dict.items():
            
            
            
            
            created_table   = create_table_from_template(dataset_name, table_template_name, table_scheme,
                                            table_name_surfix=table_name_suffix, partition_value=partition_value_str, 
                                             bigquery_client=bigquery_client)
            
            
            logger.debug('==============================================')
            logger.debug('partition_value_str=%s' , partition_value_str)
            logger.debug('partition_list=%s' , partition_list)
            logger.debug('created_table=%s' , created_table)
            logger.debug('==============================================')
            
            __errors = bigquery_client.insert_rows_json(created_table, partition_list)
            
            if len(__errors)>0:
                errors.extend(__errors)
            
    return errors
    
def wait_for_job(job):
    while True:
        job.reload()  # Refreshes the state via a GET request.
        if job.state == 'DONE':
            if job.error_result:
                raise RuntimeError(job.errors)
            return
        time.sleep(1)  

def execute_query(bigquery_client, query):
    job_id = str(uuid.uuid4())
    if bigquery_client:
        query_job = bigquery_client.query(query, job_id=job_id)
        
        return query_job.result()
        
def process_job_result_into_category_and_count(job_result_rows):
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        category_value = row[0]
        
        if category_value is None:
            category_value = 'unknown'
            
        count = row[1]
        
        column_dict['category']  = category_value
        column_dict['count']     = count
        
        row_list.append(column_dict)
    
    return row_list          
        
    
