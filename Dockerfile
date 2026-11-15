
# 1. Base Python image
FROM python:3.12-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Prevent Python from generating bytecode
ENV PYTHONDONTWRITEBYTECODE=1

# 4. Show logs immediately
ENV PYTHONUNBUFFERED=1

# 5. Copy dependency file
COPY requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy application source code
COPY main.py .

# 8. Document the application port
EXPOSE 8000

# 9. Start FastAPI using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

