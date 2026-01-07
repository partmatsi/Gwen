FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 10000
CMD ["streamlit", "run", "chat1.py", "--server.port=10000", "--server.address=0.0.0.0"]