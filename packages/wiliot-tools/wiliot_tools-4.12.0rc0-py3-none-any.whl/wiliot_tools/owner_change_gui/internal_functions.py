from datetime import datetime

import databricks.sql
import pandas as pd
import json
import time
PUBLIC_VERSION = False
try:
    from wiliot_api import InternalClient, TagNotFound
except:
    PUBLIC_VERSION = True


def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in: {execution_time:.4f} seconds")
        return result

    return wrapper


def get_databricks_config():
    try:
        config_path = "databricks_config.json"
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print("Config file not found")
        return


@time_it
def check_cloud_issues(row, expected_owner_id, client):
    tag_id = row['tag_id']
    group_id = row['group_id']
    to_return = None
    res = {}
    try:
        res = client.get_tag_status(tag_id, group_id)
    except TagNotFound:
        to_return = 'TAG_NOT_EXIST_IN_CLOUD'
    if to_return is not None:
        pass
    elif 'ownerId' not in res or 'externalId' not in res:
        to_return = 'ERROR_GET_STATUS_API'
    elif res['ownerId'] != expected_owner_id:
        to_return = f'OWNER_ID_IS_{res["ownerId"]}'
    elif row['external_id'] != res['externalId']:
        to_return = f'SERIALIZATION_ISSUE'
    else:
        to_return = "UNKNOWN"
    print(to_return, row['external_id'], res)
    return to_return


def databricks_sql(sql_query):
    config = get_databricks_config()
    if config is None:
        return
    http_path = config['http_path']
    databricks_instance = config['databricks_instance']
    token = config['token']
    print("connecting to databricks")
    with databricks.sql.connect(
            server_hostname=databricks_instance,
            http_path=http_path,
            access_token=token
    ) as connection:
        with connection.cursor() as cursor:
            print("connected to databricks")
            cursor.execute(sql_query)
            result = cursor.fetchall()
            print("query executed")
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(result, columns=columns)
    return df


@time_it
def get_all_tags(request_id):
    return databricks_sql(f"""
        with failed_ids as (
            select externalId
            from owner_change_tags_info
            where requestid = '{request_id}'
              and status = 'failed'
        ),
        failed_prefixes as (
            select distinct split(externalid, 'T')[0] as prefix
            from failed_ids
        ),
        crn_tags_info as (
        select common_run_name, external_id, tag_id, group_id, fail_bin_str, tag_run_location
        from offline_test_tag_locations
        where common_run_name in (select common_run_name
                                    from offline_test_runs
                                    where external_id_prefix in (
                                        select prefix from failed_prefixes
                                        union 
                                        select concat('010085002786501021', prefix) from failed_prefixes
                                    )))
        select *
        from crn_tags_info
        order by tag_run_location asc
    """)


@time_it
def get_fails_ids(request_id):
    return databricks_sql(f"""
        with failed_ids as (
            select externalId
            from owner_change_tags_info
            where requestId = '{request_id}'
              and status = 'failed'
        )
        select externalId as external_id
        from failed_ids
    """)

def get_owner_details(owner_id):
    try:
        config = get_databricks_config()
        if config is None:
            return
        client = InternalClient(config.get("owner_details_key"))
        data = client.get_owner_details(owner_id)
        data = data.get('data')
        if data is None or len(data) == 0:
            client = InternalClient(config.get("gcp_owner_details_key"), cloud='gcp', region='us-central1', env='wmt-prod')
            data = client.get_owner_details(owner_id)
            data = data.get('data')
        return data
    except Exception as ex:
        print(repr(ex))

if __name__ == '__main__':
    print(get_owner_details(832742983939))
