FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/app.py .

# Expose port 3000
EXPOSE 3000

# Set environment variable
ENV PORT=3000

# Run the application
CMD ["python", "app.py"]
