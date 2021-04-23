FROM python:3.7-alpine
COPY . /
RUN pip3 install -r requirements.txt
ENTRYPOINT ["/usr/local/bin/python3"]
EXPOSE 8080
CMD ["generator.py","data"]
