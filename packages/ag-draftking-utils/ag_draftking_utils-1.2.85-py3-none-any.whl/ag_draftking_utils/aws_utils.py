from io import StringIO
import boto3


def csv_to_s3(df, bucket, key, index=False):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=index)
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())


def dump_string_to_s3(string, bucket, key):
    s3 = boto3.resource('s3')
    object = s3.Object(bucket, key)
    object.put(Body=string)
    print(f'Successfully wrote to file s3://{bucket}/{key}')


def get_all_filenames_in_s3_bucket(bucket, prefix='', suffix=''):
    """
    Input:
    :param bucket: str - the AWS S3 bucket name
    :param prefix: str - optionally search by a prefix
    :param suffix: str - optionally search by a suffix
    :return: list[str] - list of files in s3 bucket matching criteria.
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    files = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith(suffix):
                files.append(obj['Key'])
    return files
