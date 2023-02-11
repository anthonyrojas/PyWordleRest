FROM python:3.11

RUN mkdir /usr/src/pywordle
WORKDIR /usr/src/pywordle
COPY ./requirements.txt /usr/src/pywordle/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /usr/src/pywordle
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
