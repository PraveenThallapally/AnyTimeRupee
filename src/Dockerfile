# Use a lightweight Python image
FROM python:3.10-slim
# Set working directory
WORKDIR /app
# Copy requirements first for caching
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy application files
COPY . .
# Expose the port Flask runs on
EXPOSE 5000
# Command to run the app
CMD ["python", "app.py"]

