FROM python:3.11.5-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt \
    --no-cache-dir \
    --prefer-binary && \
    rm -rf /root/.cache/pip

COPY nebulagraph-gephi-exchange.py .

CMD ["streamlit", "run", "nebulagraph-gephi-exchange.py", "--server.port", "8501", "--theme.base", "dark"]

EXPOSE 8501

# docker buildx build --platform linux/amd64,linux/arm64 -t weygu/nebulagraph-gephi-exchange:latest --push .

