FROM python:3.13-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd -m ctf
COPY --chown=ctf:ctf flag1.txt /flag1.txt
COPY --chown=ctf:ctf src /app

USER ctf
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "11202"]
