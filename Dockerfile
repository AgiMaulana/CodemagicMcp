FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir CodemagicMcp

ENV CODEMAGIC_API_KEY=dummy

CMD ["codemagic-mcp"]
