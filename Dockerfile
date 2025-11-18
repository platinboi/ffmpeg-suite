# Multi-stage build for optimized image size
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fontconfig \
    fonts-liberation \
    fonts-dejavu \
    wget \
    unzip \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create custom fonts directory
RUN mkdir -p /usr/share/fonts/truetype/custom

# Download and install Inter font
RUN wget https://github.com/rsms/inter/releases/download/v3.19/Inter-3.19.zip -O /tmp/inter.zip && \
    unzip /tmp/inter.zip -d /tmp/inter && \
    cp /tmp/inter/Inter*.ttf /usr/share/fonts/truetype/custom/ 2>/dev/null || \
    cp /tmp/inter/desktop/*.ttf /usr/share/fonts/truetype/custom/ 2>/dev/null || \
    cp /tmp/inter/*.ttf /usr/share/fonts/truetype/custom/ 2>/dev/null || true && \
    rm -rf /tmp/inter /tmp/inter.zip

# Download and install TikTok Sans fonts
RUN wget https://github.com/google/fonts/raw/main/ofl/tiktoksans/TikTokSans-Medium.ttf -O /usr/share/fonts/truetype/custom/TikTokSans-Medium.ttf && \
    wget https://github.com/google/fonts/raw/main/ofl/tiktoksans/TikTokSans-SemiBold.ttf -O /usr/share/fonts/truetype/custom/TikTokSans-SemiBold.ttf

# Alternative: Copy fonts from local directory (if you have them)
# COPY fonts/*.ttf /usr/share/fonts/truetype/custom/

# Set proper permissions and update font cache
RUN chmod 644 /usr/share/fonts/truetype/custom/* && \
    fc-cache -f -v

# Verify fonts are installed
RUN fc-list | grep -i "inter\|tiktok" || echo "Warning: Fonts not found in font cache"

# Create temp directory for processing
RUN mkdir -p /app/temp

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
