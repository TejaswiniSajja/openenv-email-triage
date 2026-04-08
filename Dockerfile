FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY my_env_v4.py .
COPY inference.py .
COPY README.md .

# Set environment variables
ENV PYTHONPATH=/app
ENV HF_TOKEN=""
ENV OPENAI_API_KEY=""
ENV API_BASE_URL="https://api.openai.com/v1"
ENV MODEL_NAME="gpt-3.5-turbo"

# Run inference
CMD ["python", "inference.py"]