FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --no-deps .

ENV ADERRR_EDITOR_HOST=0.0.0.0
ENV PORT=8765
EXPOSE 8765

CMD ["python", "tools/editor_server.py"]
