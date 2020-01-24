FROM alpine:latest
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1
RUN apk add python3 python3-dev gcc musl-dev linux-headers 
WORKDIR /app
RUN pip3 install --upgrade pip setuptools
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install uwsgi
#RUN git clone https://github.com/minils/InventoryManager.git /app
COPY . /app
EXPOSE 8000
CMD ["uwsgi", "--http", ":8000", "--wsgi-file", "inventorymanager/wsgi.py"]
