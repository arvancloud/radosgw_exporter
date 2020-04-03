FROM python:3.8.2-alpine3.11

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY radosgw_exporter.py /

EXPOSE 9242
ENTRYPOINT [ "python3", "/radosgw_exporter.py" ]