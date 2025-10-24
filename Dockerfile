FROM python:3.11-slim
WORKDIR /app
COPY . /app
EXPOSE 8081
ENV HOST=0.0.0.0
ENV PORT=8085
ENV WEBROOT=/app
CMD ["python3", "server.py"]

