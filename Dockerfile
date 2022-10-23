FROM python:3.10

WORKDIR /src
COPY ./src /src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
