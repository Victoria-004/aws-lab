FROM python:3.13-slim-bookworm

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN useradd --create-home appuser
USER appuser

EXPOSE 5000
CMD ["sh", "-c", "python init_db.py && exec gunicorn --bind 0.0.0.0:5000 --workers 3 --threads 4 --timeout 60 main:app"]