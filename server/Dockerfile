FROM python:3.11.15-slim-trixie

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR $HOME/app

COPY --chown=user server/requirements.txt ./server/requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r server/requirements.txt

COPY --chown=user __init__.py .
COPY --chown=user client.py .
COPY --chown=user app ./app
COPY --chown=user server ./server
COPY --chown=user baselines ./baselines
COPY --chown=user openenv.yaml .
COPY --chown=user README.md .

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
