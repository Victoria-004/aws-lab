FROM python:3.13-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY emulator.py .
RUN useradd --create-home emulator
USER emulator

CMD ["python", "-u", "emulator.py"]
