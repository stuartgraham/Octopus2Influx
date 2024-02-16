FROM python:3.12-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt && rm requirements.txt
CMD ["python3", "./main.py"]