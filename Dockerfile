FROM python:3.10-slim

WORKDIR /app

# Install uv for better dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY requirements.txt ./

# Install dependencies using uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy application files - FIXED: my_env_v4.py is in server folder
COPY server/ ./server/
COPY inference.py ./
COPY client.py ./
COPY models.py ./
COPY graders.py ./
COPY openenv.yaml ./

# Set environment variables
ENV PYTHONPATH=/app
ENV HF_TOKEN=""
ENV OPENAI_API_KEY=""

# Expose the port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]