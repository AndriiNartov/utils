FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt .
COPY entrypoint.sh .

RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

COPY . .

ENTRYPOINT ["bash", "/usr/src/app/entrypoint.sh"]