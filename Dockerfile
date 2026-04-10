# Stage 1: Build Python environment
FROM python:3.9-slim as python-base

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build Node.js environment
FROM node:18-alpine as node-base

WORKDIR /app

# Install Node.js dependencies
COPY package*.json ./
RUN npm ci --only=production

# Stage 3: Final image
FROM python:3.9-slim

WORKDIR /app

# Copy Python dependencies from stage 1
COPY --from=python-base /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=python-base /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy Node.js dependencies from stage 2
COPY --from=node-base /app/node_modules ./node_modules

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web.app:app"]