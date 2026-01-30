FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py index.html ./
COPY cognee_example.py ./

EXPOSE 8000

CMD ["python", "server.py"]
