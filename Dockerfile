FROM python:3.9.19

WORKDIR /app
COPY . .
RUN pip3 install --upgrade pip
RUN chmod 755 .
RUN python3 -m pip install -r reqirements.txt
EXPOSE 27017


