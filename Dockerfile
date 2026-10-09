FROM python:3.12-slim

WORKDIR /app
COPY . .

ENV ADERRR_EDITOR_HOST=0.0.0.0
ENV PORT=8765
EXPOSE 8765

CMD ["python", "tools/editor_server.py"]
