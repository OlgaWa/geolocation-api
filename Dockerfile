FROM python:3.11.3

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]