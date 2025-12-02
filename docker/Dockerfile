FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY services/ /app/config/services/
COPY shared/ /app/config/shared/

# Create secrets directory
RUN mkdir -p /app/config/.secrets && \
    chmod 700 /app/config/.secrets

# Expose port
EXPOSE 8015

# Run service
CMD ["python", "-m", "src.main"]

