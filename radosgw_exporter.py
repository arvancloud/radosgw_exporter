#!/usr/bin/env python

import argparse
import os
import sys
import radosgw
import time
import datetime
import daemon
import socket
from prometheus_client import start_http_server
from prometheus_client import Gauge
from prometheus_client import Summary


"""
# base
pip install radosgw-admin

# create rados user with this caps
"caps": [
   { "type": "buckets",
     "perm": "*" },
   { "type": "usage",
     "perm": "read" },
   { "type": "metadata",
     "perm": "read" },
   { "type": "users",
     "perm": "*" }
]

radosgw-admin caps add --uid <USER_ID> --caps "buckets=read,write"
radosgw-admin caps add --uid <USER_ID> --caps "users=read,write"


# exporter
pip install prometheus_client

# links
https://github.com/valerytschopp/python-radosgw-admin
https://github.com/ceph/ceph/blob/master/doc/radosgw/compression.rst
"""

# call argparse
parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', help='Host ip or url without http/https and port (required, env HOST)',default=os.environ.get('HOST', None), required=False)
parser.add_argument('-p', '--port', help='Port address (default 443, env PORT)',default=os.environ.get('PORT', 443))
parser.add_argument('-a', '--access-key', help='Access Key of S3 (required, env ACCESS_KEY)', default=os.environ.get('ACCESS_KEY', None), required=False)
parser.add_argument('-s', '--secret-key', help='Secret Key of S3 (required, env SECRET_KEY)', default=os.environ.get('SECRET_KEY', None), required=False)
parser.add_argument('--insecure', help='Disable ssl/tls verification (default true)', default=True, action='store_true')
parser.add_argument('--debug', help='Enable debug mode', action='store_true')
parser.add_argument('-d', '--daemon', help='Enable daemon mode (default false)', action='store_true', default=False)
parser.add_argument('--signature', help='AWS signature version to use: AWS4 or AWS2 (default AWS4)', default='AWS4')
parser.add_argument('-t', '--scrap-timeout', help='Scrap interval in seconds (default 60)', default=60)
parser.add_argument('--expose-port', help='Exporter port (default 9242)', default=9242)
parser.add_argument('--expose-address', help='Exporter address (default 0.0.0.0)', default="0.0.0.0")
args = parser.parse_args()

# set vars from args (I use this way because I think it's more usable for me in feature)
host = args.host
port = int(args.port)
access_key = args.access_key
secret_key = args.secret_key
is_secure = args.insecure
debug = args.debug
is_daemon = args.daemon
signature = args.signature
scrap_timeout = int(args.scrap_timeout)
expose_address = args.expose_address
expose_port = int(args.expose_port)

# create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# check args
def radosgw_args():
    # check host
    if not host:
        print("host variable doesn't exist.\n")
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    # check access key
    if not access_key:
        print("access-key doesn't exist.\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # check secret key
    if not secret_key:
        print("secret-key doesn't exist.\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # check expose address and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((expose_address,expose_port))
    if result == 0:
        print(f"expose address or port aren't usefull: {expose_address}:{expose_port}")
        print(f"use other address port\n")
        parser.print_help(sys.stderr)
        sys.exit(1)
    sock.close()


# create metrics
def radosgw_metrics():
    # define global metric variables
    global radosgw_bucket_total_metric
    global radosgw_bucket_owner_metric
    global radosgw_bucket_num_object_metric
    global radosgw_bucket_size_metric
    global radosgw_bucket_size_kb_metric
    global radosgw_bucket_size_actual_metric
    global radosgw_bucket_size_kb_actual_metric
    global radosgw_bucket_size_utilized_metric
    global radosgw_bucket_size_kb_utilized_metric
    global radosgw_scrap_timeout_metric

    # set help and type date for metrics
    radosgw_bucket_total_metric = Gauge('radosgw_bucket_total', 'Total number of buckets')
    radosgw_bucket_owner_metric = Gauge('radosgw_bucket_owner', 'Name of Owner(UID) in string', ['owner'])
    radosgw_bucket_num_object_metric = Gauge('radosgw_bucket_num_object_total', 'Number of Object in bucket', ['owner', 'name'])
    radosgw_bucket_size_metric = Gauge('radosgw_bucket_size', 'Size of bucket in bytes', ['owner', 'name'])
    radosgw_bucket_size_kb_metric = Gauge('radosgw_bucket_size_kb', 'Size of bucket in kilobytes', ['owner', 'name'])
    radosgw_bucket_size_actual_metric = Gauge('radosgw_bucket_size_actual', 'Actual size of bucket in bytes', ['owner', 'name'])
    radosgw_bucket_size_kb_actual_metric = Gauge('radosgw_bucket_size_kb_actual', 'Actual size of bucket in kilobytes', ['owner', 'name'])
    radosgw_bucket_size_utilized_metric = Gauge('radosgw_bucket_size_utilized', 'Utilized size (total size of compressed data) of bucket in bytes', ['owner', 'name'])
    radosgw_bucket_size_kb_utilized_metric = Gauge('radosgw_bucket_size_kb_utilized', 'Utilized size (total size of compressed data) of bucket in kilobytes', ['owner', 'name'])
    radosgw_scrap_timeout_metric = Gauge('radosgw_scrap_timeout_seconds', 'Scrap interval in seconds')


# call collector
@REQUEST_TIME.time()
def radosgw_collector():
    try:
        # create connection to radosgw
        rgwadmin = radosgw.connection.RadosGWAdminConnection(host = host,
                                                                port = port,
                                                                access_key = access_key,
                                                                secret_key = secret_key,
                                                                is_secure = not is_secure,
                                                                debug = debug,
                                                                aws_signature = signature)
    
        # get buckets and details of them
        buckets = rgwadmin.get_buckets()

        # total bucket counter
        bucket_total = 0

        for bucket in buckets:

            # set metrics of bucket owner and bucket name
            bucket_owner = bucket.owner
            radosgw_bucket_owner_metric.labels(bucket_owner).set(1)

            # count buckets
            bucket_total += 1
            radosgw_bucket_total_metric.set(bucket_total)

            # set bucket name variable to use in metrics
            bucket_name = bucket.name

            # set usage metrics of buckets
            if bucket.usage:
                bucket_num_objects = bucket.usage.num_objects
                bucket_size = bucket.usage.size
                bucket_size_kb = bucket.usage.size_kb
                bucket_size_kb_actual = bucket.usage.size_kb_actual
                bucket_size_actual = bucket.usage.size_actual
                bucket_size_utilized = bucket.usage.size_utilized
                bucket_size_kb_utilized = bucket.usage.size_kb_utilized
                # bucket_bucket = bucket.bucket

            # if usage not exist, and just bucket is exist, set usage parameters to 0
            else:
                bucket_num_objects = 0
                bucket_size = 0
                bucket_size_kb = 0
                bucket_size_kb_actual = 0
                bucket_size_actual = 0
                bucket_size_utilized = 0
                bucket_size_kb_utilized = 0

            # set data to metrics
            radosgw_bucket_num_object_metric.labels(bucket_owner, bucket_name).set(bucket_num_objects)
            radosgw_bucket_size_metric.labels(bucket_owner, bucket_name).set(bucket_size)
            radosgw_bucket_size_kb_metric.labels(bucket_owner, bucket_name).set(bucket_size_kb)
            radosgw_bucket_size_actual_metric.labels(bucket_owner, bucket_name).set(bucket_size_actual)
            radosgw_bucket_size_kb_actual_metric.labels(bucket_owner, bucket_name).set(bucket_size_kb_actual)
            radosgw_bucket_size_utilized_metric.labels(bucket_owner, bucket_name).set(bucket_size_utilized)
            radosgw_bucket_size_kb_utilized_metric.labels(bucket_owner, bucket_name).set(bucket_size_kb_utilized)


    except radosgw.exception.NoSuchBucket as err:
        print(f"problem occured: {err}")


# main fucntion of script
def radosgw_runner():
    try:
        start_http_server(expose_port, expose_address)
        print(f"exporter start listening on {expose_address}:{expose_port}")
        print(f"scrap every {scrap_timeout} seconds")
        print(f"debug mode is {debug}\n")

        if debug:
            print(f"exporter connect to {host}:{port}")
            print(f"insecure option is {is_secure}")

        # call fuction of metric creation
        radosgw_metrics()
        radosgw_scrap_timeout_metric.set(scrap_timeout)
    
        while True:
            if debug:
                now = datetime.datetime.now()
                print("start collecting at ", now.strftime("%Y-%m-%d %H:%M:%S"))

            # start collecting data
            radosgw_collector()

            if debug:
                now = datetime.datetime.now()
                print("finish collecting at ", now.strftime("%Y-%m-%d %H:%M:%S"))
                print(f"start timeout for {scrap_timeout}")

            time.sleep(scrap_timeout)
    except :
        print(f"problem occured")


# main
if __name__ == "__main__":
    # check radosgs args
    radosgw_args()

    if is_daemon:
        with daemon.DaemonContext(
            working_directory='/tmp',
            umask=0o002
            ) as context:
                radosgw_runner()
    else:
        radosgw_runner()