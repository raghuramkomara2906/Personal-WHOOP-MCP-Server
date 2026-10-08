FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
COPY src ./src
COPY app.py ./
COPY oauth_callback.py ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

RUN mkdir -p /app/.data

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]