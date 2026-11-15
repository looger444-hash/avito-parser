FROM mcr.microsoft.com/playwright:v1.40.0-jammy
WORKDIR /app
RUN pip install playwright beautifulsoup4 requests
COPY . .
CMD ["python", "parser.py"]
