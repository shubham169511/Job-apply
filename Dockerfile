
# Use official Python 3.10 image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (not mandatory for this bot but good practice)
EXPOSE 8000

# Run the Telegram bot script
CMD ["python", "oracle_job_telegram_bot.py"]
