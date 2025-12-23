FROM docker:27.3.1-cli

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY bot/requirements.txt /app/bot/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/bot/requirements.txt

CMD ["python3", "-m", "bot.main"]
