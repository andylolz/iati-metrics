from random import shuffle

from io import BytesIO
import json
from time import sleep
import os

import requests
import boto3
from rq import Queue

from worker import conn


s3 = boto3.client('s3')
bucket_name = os.getenv('S3_BUCKET_NAME', 'iati-data.codeforiati.org')
extra_args_xml = {'ACL': 'public-read', 'ContentType': 'text/xml'}
extra_args = {'ACL': 'public-read', 'ContentType': 'application/json'}
api_url = 'https://iatiregistry.org/api/3/action/package_show'


def fetch_data(dataset_name):
    meta = request_with_backoff(
        'post', api_url, data={'id': dataset_name}).json()['result']
    res = meta.get('resources', [])
    org_name = meta.get('organization', {}).get('name')
    if res == [] or not org_name:
        return
    url = res[0]['url']
    headers = {
        'Accept': 'application/xhtml+xml,application/xml,*/*;q=0.9',
        'User-Agent': 'IATI data dump',
    }
    res = request_with_backoff(
        'get', url, headers=headers, verify=False)
    # upload the data
    s3.upload_fileobj(
        BytesIO(res.content),
        bucket_name,
        f'data/{org_name}/{dataset_name}.xml',
        ExtraArgs=extra_args_xml)
    # upload the metadata
    s3.upload_fileobj(
        BytesIO(json.dumps(meta).encode('utf-8')),
        bucket_name,
        f'metadata/{org_name}/{dataset_name}.json',
        ExtraArgs=extra_args)


def request_with_backoff(*args, attempts=5, backoff=0.5, **kwargs):
    for attempt in range(attempts):
        try:
            result = requests.request(*args, **kwargs)
            return result
        except requests.exceptions.ConnectionError:
            wait = (attempt + 1) * backoff
            print(f'Rate limited! Retrying after {wait} seconds')
            sleep(wait)
    raise Exception(f'Failed after {attempts} attempts. Giving up.')


def enqueue():
    q = Queue(connection=conn)
    api_url = 'https://iatiregistry.org/api/3/action/package_list'
    dataset_names = request_with_backoff('post', api_url).json()['result']
    shuffle(dataset_names)
    for dataset_name in dataset_names:
        print(f'Enqueuing: {dataset_name}')
        q.enqueue(fetch_data, dataset_name, result_ttl=0)

    # # Restart on completion
    # q = Queue('low', connection=conn)
    # q.enqueue(enqueue, result_ttl=0)
