FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

COPY --chown=user pyproject.toml .
COPY --chown=user uv.lock .
COPY --chown=user server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r server/requirements.txt
RUN pip install --no-cache-dir -e .

COPY --chown=user __init__.py .
COPY --chown=user client.py .
COPY --chown=user app ./app
COPY --chown=user server ./server
COPY --chown=user baselines ./baselines
COPY --chown=user openenv.yaml .
COPY --chown=user README.md .

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
