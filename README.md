# Rados Gateway Exporter (radosgw_exporter)
## Introduction
This is Rados Gateway Exporter written in python3 for prometheus.
You can run it in simple linux or container.
I've check some repos in github and gitlab, but they have some problems with ceph and radosgw.

## Requirements
This script needs prometheus-client, radosgw-admin (1.7.1) and python-daemon as modules, and I wrote it with Python 3.8.2.
This is `requirements.txt` :
```bash
prometheus-client
radosgw-admin==1.7.1
python-daemon
```
Also you need a S3 user to get data from rados gateway.

## Usage
### Docker
```bash
docker run \
  --name radosgw_exporter \
  -it \
  -p 127.0.0.1:9242:9242 \
  -e ACCESS_KEY='put-your-access-key' \
  -e SECRET_KEY='put-your-secret-key' \
  -e HOST='put-your-radosgw-address' \
  -e PORT='put-your-radosgw-port' \
  moghaddas/radosgw_exporter
```

### Simple
```bash
git clone https://github.com/arvancloud/radosgw_exporter
cd radosgw_exporter

pip install -r requirements.txt


./radosgw_exporter.py -h
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

./radosgw_exporter.py -H RADOSGW-HOST -p RADOSGW-PORT -a ACCESS_KEY -s SECRET_KEY --insecure --scrap-timeout 5 --expose-address 127.0.0.1
```