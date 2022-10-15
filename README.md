# Rados Gateway Exporter (radosgw_exporter)
## Introduction
This is Rados Gateway Exporter written in python3 for prometheus.
You can run it in simple linux or container.
I've check some repos in GitHub and Gitlab, but they have some problems with ceph and radosgw.

## Requirements
This script needs prometheus-client, radosgw-admin, python-daemon, and some other libraries as modules, so I wrote it with Python 3.8.2.
This is `requirements.txt` :
```bash
boto==2.49.0
docutils==0.19
lockfile==0.12.2
prometheus-client==0.15.0
python-daemon==2.3.1
radosgw-admin==1.7.2
```
## Preparing environment
Also you need a S3 user to get data from rados gateway. 

For creating a suitable rados user, use the following instructions:

In case of not having radosgw-admin command, install the following package:
```bash
pip install radosgw-admin
```
Then create rados user with these caps:
```json
"caps": [
   { "type": "buckets",
     "perm": "read" },
   { "type": "usage",
     "perm": "read" },
   { "type": "metadata",
     "perm": "read" },
   { "type": "users",
     "perm": "read" }
]
```
By using these commands:
```commandline
radosgw-admin caps add --uid <USER_ID> --caps "usage=read"
radosgw-admin caps add --uid <USER_ID> --caps "metadata=read"
radosgw-admin caps add --uid <USER_ID> --caps "buckets=read"
radosgw-admin caps add --uid <USER_ID> --caps "users=read"
```

## Usage
### Docker
```bash
docker run \
  --name radosgw_exporter \
  -it \
  -p 9242:9242 \
  -e ACCESS_KEY='PUT_YOUR_ACCESS_KEY' \
  -e SECRET_KEY='PUT_YOUR_SECRET_KEY' \
  -e HOST='PUT_YOUR_RADOSGW_ADDRESS' \
  -e PORT='PUT_YOUR_RADOSGW_PORT' \
  moghaddas/radosgw_exporter
```

### Command Line Interface
First, clone the repository:
```bash
git clone https://github.com/arvancloud/radosgw_exporter
```
Then go to the directory
```bash
cd radosgw_exporter
```
Then install the required packages
```bash
pip install -r requirements.txt
```
For printing usage info, use the following command:
```bash
./radosgw_exporter.py -h
```
The output should be like this:
```bash
usage: radosgw_exporter.py [-h] [-H HOST] [-p PORT] [-a ACCESS_KEY] [-s SECRET_KEY] [--insecure] [--debug] [-d] [--signature SIGNATURE] [-t SCRAP_TIMEOUT] [--expose-port EXPOSE_PORT] [--expose-address EXPOSE_ADDRESS]

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Host ip or url without http/https and port (required, env HOST)
  -p PORT, --port PORT  Port address (default 443, env PORT)
  -a ACCESS_KEY, --access-key ACCESS_KEY
                        Access Key of S3 (required, env ACCESS_KEY)
  -s SECRET_KEY, --secret-key SECRET_KEY
                        Secret Key of S3 (required, env SECRET_KEY)
  --insecure            Disable ssl/tls verification (default true)
  --debug               Enable debug mode
  -d, --daemon          Enable daemon mode (default false)
  --signature SIGNATURE
                        AWS signature version to use: AWS4 or AWS2 (default AWS4)
  -t SCRAP_TIMEOUT, --scrap-timeout SCRAP_TIMEOUT
                        Scrap interval in seconds (default 60)
  --expose-port EXPOSE_PORT
                        Exporter port (default 9242)
  --expose-address EXPOSE_ADDRESS
                        Exporter address (default 0.0.0.0)
```
And here is an example for using this app:
```bash 
./radosgw_exporter.py -H RADOSGW-HOST -p RADOSGW-PORT -a ACCESS_KEY -s SECRET_KEY --insecure --scrap-timeout 5 --expose-address 127.0.0.1
```


# links
https://github.com/valerytschopp/python-radosgw-admin

https://github.com/ceph/ceph/blob/master/doc/radosgw/compression.rst
