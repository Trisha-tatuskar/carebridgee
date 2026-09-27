FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD sh -c "python manage.py migrate && gunicorn carebridge_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}"