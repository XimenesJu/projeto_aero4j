FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Create .env file from environment variables
ENV NEO4J_URI=${NEO4J_URI}
ENV NEO4J_USERNAME=${NEO4J_USERNAME}
ENV NEO4J_PASSWORD=${NEO4J_PASSWORD}
ENV NEO4J_DATABASE=${NEO4J_DATABASE}
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV CORS_ORIGINS=${CORS_ORIGINS}

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
