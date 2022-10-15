FROM python:alpine3.16

ENTRYPOINT [ "python3", "/radosgw_exporter.py" ]
EXPOSE 9242
COPY requirements.txt /
RUN pip install -U pip setuptools
RUN pip install --no-cache-dir -r /requirements.txt
COPY radosgw_exporter.py /
