FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir codemagic-mcp

ENV CODEMAGIC_API_KEY=dummy

CMD ["codemagic-mcp"]
