FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements.lock Makefile README.md ./
COPY src ./src
COPY tests ./tests
RUN python -m pip install --no-cache-dir -r requirements.lock && python -m pip install --no-cache-dir -e .
CMD ["make", "verify"]
